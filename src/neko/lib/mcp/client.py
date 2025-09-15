#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import ollama

from ..utils.env import load_env, get_system_prompt
from ...config.settings import Settings


load_env()
logger = logging.getLogger(__name__)
logging.basicConfig(filename='neko.log', level=logging.INFO)


class MCPClient:
  def __init__(self, messages: Optional[list] = None):
    self.session: Optional[ClientSession] = None
    self.exit_stack = AsyncExitStack()
    self.ollama = ollama.AsyncClient()
    self.tools = None
    self.messages = messages if messages is not None else [
      {'role': 'system', 'content': get_system_prompt()},
      {"role": "assistant", "content": "What are we breaking today?"}
    ]

  async def connect_to_server(self, server_script_path: str):
    """Connect to an MCP server

    Args:
      server_script_path: Path to the server script (.py or .js)
    """
    is_python = server_script_path.endswith('.py')
    is_js = server_script_path.endswith('.js')
    if not (is_python or is_js):
      raise ValueError("Server script must be a .py or .js file")
    command = "python" if is_python else "node"
    server_params = StdioServerParameters(
      command=command,
      args=[server_script_path],
      env=None
    )
    stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
    self.stdio, self.write = stdio_transport
    self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
    await self.session.initialize()
    response = await self.session.list_tools()
    self.tools = self._convert_tools(response.tools)

  def _convert_tools(self, tools):
    """
    Convert MCP tools into Ollama Tool objects.
    Returns a list of ollama.Tool instances with proper Parameters.Property wrapping.
    """
    converted_tools = []
    for i, tool in enumerate(tools):
      try:
        ollama_tool = ollama.Tool(
          type="function",
          function=ollama.Tool.Function(
            name=tool.name,
            description=tool.description,
            parameters=tool.inputSchema or {
              "type": "object",
              "properties": {},
              "required": []
            }
          )
        )
        converted_tools.append(ollama_tool)
      except Exception as e:
        print(f"An error occurred during tool convertion.\n{e}")
    return converted_tools

  async def query(
    self,
    query: str,
    max_iterations: int = 10
  ) -> list[dict[str, Any]]:
    """
    Process model response and handle tool calls iteratively

    Args:
      messages (List[Dict[str, Any]]): List of messages with role/content
      max_iterations (int): Maximum number of iterations to prevent infinite loops

    Returns:
      List[Dict[str, Any]]: Updated messages list with all interactions
    """
    self.messages.append({"role": "user","content": query})
    iteration = 0
    while iteration < max_iterations:
      response: ollama.ChatResponse = await self.ollama.chat(
        model=Settings.base_model,
        messages=self.messages,
        think=False,
        tools=self.tools,
        stream=False
      )
      self.messages.append(response.message)
      logger.info(f"\nDBG Response -> {response.message}")
      logger.info(f"\nDBG Tools -> {self.tools}")
      if response.message.tool_calls:
        logger.info(f"\n--- Processing {len(response.message.tool_calls)} tool call(s) ---")
        for tool in response.message.tool_calls:
          if any(tool.function.name == func.function.name for func in self.tools):
            for _, tool in enumerate(response.message.tool_calls):
              logger.info(f'Calling function: {tool.function.name}')
              logger.info(f'Arguments: {tool.function.arguments}')
              output = await self.session.call_tool(tool.function.name, tool.function.arguments)
              logger.info(f'Function output: {output}')
              self.messages.append({
                'role': 'tool',
                'content': str(output),
                'name': tool.function.name,
                'arguments': tool.function.arguments
              })
          else:
            logger.error(f'Function {tool.function.name} not found')
      else:
        iteration += 1
        return self.messages
        break
    if iteration >= max_iterations:
      logger.warning(f"\n⚠️  Reached maximum iterations ({max_iterations}). Stopping auto-execution.")
    return self.messages

  async def cleanup(self):
    """Clean up resources"""
    await self.exit_stack.aclose()
