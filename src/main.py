#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ollama
import asyncio
from typing import List, Dict, Any
from lib.tools.shell import shell_tool, hacking_tool
from lib.tools.rag import RAG
from lib.tools.browser import web_browser_tool
from lib.tools.message import ask_user_tool
from lib.tools.web_search import ddg_search
from lib.utils.env import load_env, get_system_prompt


def rag_tool(query: str) -> str:
  """
  Combines retrieval and generation with improved prompt formatting.

  Args:
    prompt (str): The query to search in vectorial database

  Returns:
    str: The LLM's response.
  """
  rag = RAG()
  context = rag.retrieval(prompt=query)
  if not context:
    system_context = f"{rag.system_prompt}\n\nNote: No relevant context was found for this query."
    response = ollama.generate(
      model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
      system=system_context,
      prompt=query,
      think=False
    )
    return response['response']
  context_text = "\n\n---\n\n".join(context)
  system_context = f"{rag.system_prompt}\n\nContext information:\n{context_text}"
  response = ollama.generate(
    model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
    system=system_context,
    prompt=query
  )
  return response['response']


available_functions = {
  'shell_tool': shell_tool,
  'hacking_tool': hacking_tool,
  'web_browser_tool': web_browser_tool,
  'rag_tool': rag_tool,
  'ask_user_tool': ask_user_tool,
  'ddg_search': ddg_search,
}


async def process_model_response(
  client: ollama.AsyncClient,
  messages: List[Dict[str, Any]],
  max_iterations: int = 10
) -> str:
  """
  Process model response and handle tool calls iteratively

  Args:
    client (ollama.AsyncClient): The Ollama async client instance
    messages (List[Dict[str, Any]]): List of messages with role/content
    max_iterations (int): Maximum number of iterations to prevent infinite loops

  Returns:
    List[Dict[str, Any]]: Updated messages list with all interactions
  """
  iteration = 0
  while iteration < max_iterations:
    response: ollama.ChatResponse = await client.chat(
      model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
      messages=messages,
      think=False,
      tools=[
        shell_tool,
        hacking_tool,
        web_browser_tool,
        rag_tool,
        ask_user_tool,
        ddg_search
      ],
    )
    messages.append(response.message)
    if response.message.tool_calls:
      print(f"\n--- Processing {len(response.message.tool_calls)} tool call(s) ---")
      for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
          print(f'Calling function: {tool.function.name}')
          print(f'Arguments: {tool.function.arguments}')
          if asyncio.iscoroutinefunction(function_to_call):
            output = await function_to_call(**tool.function.arguments)
          else:
            output = function_to_call(**tool.function.arguments)
          print(f'Function output: {output}')
          # add each tool result to messages
          messages.append({
            'role': 'tool',
            'content': str(output),
            'name': tool.function.name
          })
        else:
          print(f'Function {tool.function.name} not found')
      # continue the loop to let the model process tool results and decide next steps
      iteration += 1
    else:
      # no more tool calls - model has finished
      print(f'Assistant: {response.message.content}')
      break
  if iteration >= max_iterations:
    print(f"\n⚠️  Reached maximum iterations ({max_iterations}). Stopping auto-execution.")
  return messages


def create_vdb_if_needed() -> None:
  """
  Create the vector database if it does not already exist.
  """
  VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vectordb")
  DATASETS_PATH = os.getenv("DATASETS_PATH", "datasets")
  rag = RAG(VECTOR_DB_PATH)
  if not rag.collection.count():
    print("No data found in vector DB. Indexing documents...")
    rag.load(DATASETS_PATH)
    rag.chunk()
    rag.vector_store()
    print("Vector store ready.")
  else:
    print(f"Loaded existing vector DB with {rag.collection.count()} entries.")


async def main() -> None:
  """
  The main function.
  """
  create_vdb_if_needed()
  messages = [
    {
      'role': 'system',
      'content': get_system_prompt(),
    },
    {
      "role": "assistant",
      "content": "What are we breaking today?"
    }
  ]
  print("Assistant:", messages[1]["content"])
  while True:
    try:
      prompt = input("Enter a message... ➜ ")
      if not prompt.strip():
        continue
      client = ollama.AsyncClient()
      messages.append({"role": "user", "content": prompt})
      messages = await process_model_response(client, messages)
    except KeyboardInterrupt:
      print("\nGoodbye!")
      return
    except Exception as e:
      print(f"Error: {e}")


if __name__ == "__main__":
  load_env()
  asyncio.run(main())
