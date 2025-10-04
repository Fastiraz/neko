#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP
from neko.lib.tools.shell import shell_tool, hacking_tool
from neko.lib.tools.rag import RAG
from neko.lib.tools.browser import web_browser_tool
from neko.lib.tools.message import ask_user_tool
from neko.lib.tools.web_search import ddg_search
from neko.lib.tools.code import read_file, write_file


mcp = FastMCP("neko")


@mcp.tool()
def shell_tool_mcp(command: str) -> str:
  """
  Executes a shell command and returns the output as a single string.
  This function is designed to be used as a tool for LLM agents to interact with the system.
  Commands are validated for safety before execution.

  Args:
    command (str): The shell command to execute. Will be checked for dangerous patterns.

  Returns:
    str: The command output. Returns stdout if command succeeds, stderr if it fails, or an error message if execution fails or command is deemed unsafe.
  """
  return shell_tool(command)


@mcp.tool()
async def browser_tool(prompt: str):
  """
  This function allow an AI agent to perform tasks on a browser.

  Args:
    prompt (str): The task to do on the browser.

  Returns:
    str: The browser-use's result.
  """
  return await web_browser_tool(prompt)


@mcp.tool()
def hacking_tool_mcp(command: str) -> str:
  """
  Advanced hacking tool for security testing and penetration testing.

  Args:
    command (str): The hacking command to execute.
  Returns:
    str: The command output.
  """
  return hacking_tool(command)


@mcp.tool()
def ask_user_tool_mcp(message: str) -> str:
  """
  Ask the user a question and wait for their response.

  Args:
    message (str): The message/question to show to the user.

  Returns:
    str: The user's response.
  """
  return ask_user_tool(message)


@mcp.tool()
def ddg_search_mcp(query: str) -> str:
  """
  Search the web using DuckDuckGo API.

  Args:
    query (str): The search query.

  Returns:
    str: The search results.
  """
  return ddg_search(query)


@mcp.tool()
def rag_tool(prompt: str) -> str:
  """
  RAG retrieval.

  Args:
    prompt: The user query for the LLM.

  Returns:
    Context so the LLM can works with.
  """
  rag = RAG()
  rag.load()
  rag.chunk()
  rag.vector_store()
  context = rag.retrieval(prompt=prompt)
  if not context:
    system_context = (
      f"{rag.system_prompt}\n\n"
      "Note: No relevant context was found for this query."
    )
    return system_context
  context_text = "\n\n---\n\n".join(context)
  system_context = f"{rag.system_prompt}\n\nContext information:\n{context_text}"
  print(system_context)
  return system_context


@mcp.tool()
def write_file_tool(
  file_path: str,
  content: str,
  mode: str = 'w'
) -> bool:
  """
  This function allow the AI agent to write into a file.

  Args:
    file_path (str): The file path to write into.
    content (str): The content to write to the file.
    mode (str): File mode ('w' for write, 'a' for append). Default is 'w'.

  Returns:
    bool: True if successful, False otherwise.
  """
  return write_file(file_path, content, mode)


@mcp.tool()
def read_file_tool(file_path: str) -> str:
  """
  Utility function to read a file and return its content.

  Args:
    file_path (str): Path to the file to read.

  Returns:
    str: File content if successful, None if failed.
  """
  return read_file(file_path)


if __name__ == "__main__":
  mcp.run()
