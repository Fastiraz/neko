#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import ollama
from mcp.server.fastmcp import FastMCP

from neko.lib.tools.shell import shell_tool, hacking_tool
from neko.lib.tools.rag import RAG
from neko.lib.tools.browser import web_browser_tool
from neko.lib.tools.message import ask_user_tool
from neko.lib.tools.web_search import ddg_search
from neko.lib.utils.env import load_env


load_env()
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
async def browser_tool(prompt: str) -> str:
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
  Search the web using DuckDuckGo.

  Args:
    query (str): The search query.

  Returns:
    str: The search results.
  """
  return ddg_search(query)


@mcp.resource("greeting://{prompt}")
def rag_tool(prompt: str) -> str:
  """
  Combines retrieval and generation with improved prompt formatting.

  Args:
    prompt (str): The user prompt for the LLM.

  Returns:
    str: The LLM's response.
  """
  rag = RAG()
  context = rag.retrieval(prompt=prompt)
  if not context:
    system_context = f"{rag.system_prompt}\n\nNote: No relevant context was found for this query."
    response = ollama.generate(
      model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
      system=system_context,
      prompt=prompt,
      think=False
    )
    return response['response']
  context_text = "\n\n---\n\n".join(context)
  system_context = f"{rag.system_prompt}\n\nContext information:\n{context_text}"
  response = ollama.generate(
    model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
    system=system_context,
    prompt=prompt
  )
  return response['response']


if __name__ == "__main__":
  mcp.run()
