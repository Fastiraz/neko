#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ollama
import asyncio
from lib.tools.shell import execute_shell_command
from lib.tools.rag import RAG
from lib.tools.browser import use_browser
from lib.utils.env import load_env, get_system_prompt


def ask_rag(prompt: str) -> str:
  """
  Combines retrieval and generation with improved prompt formatting.

  :args:
  ------
      prompt (str): The user prompt for the LLM.

  :return:
  --------
      str: The LLM's response.
  """
  rag = RAG()
  context = rag.retrieval(prompt=prompt)
  if not context:
    system_context = f"{rag.system_prompt}\n\nNote: No relevant context was found for this query."
    response = ollama.generate(
      model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
      system=system_context,
      prompt=prompt
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


available_functions = {
  'execute_shell_command': execute_shell_command,
  'use_browser': use_browser,
  'ask_rag': ask_rag,
}


async def process_model_response(client, messages, max_iterations=10):
  """
  Process model response and handle tool calls iteratively
  """
  iteration = 0

  while iteration < max_iterations:
    response: ollama.ChatResponse = await client.chat(
      model=os.environ.get('MODEL', 'deepseek-r1:14b').strip().strip('"'),
      messages=messages,
      think=False,
      tools=[execute_shell_command, use_browser, ask_rag],
    )

    # Add the assistant's response to messages
    messages.append(response.message)

    if response.message.tool_calls:
      print(f"\n--- Processing {len(response.message.tool_calls)} tool call(s) ---")

      # Process each tool call
      for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
          print(f'Calling function: {tool.function.name}')
          print(f'Arguments: {tool.function.arguments}')

          # Execute the function
          if asyncio.iscoroutinefunction(function_to_call):
            output = await function_to_call(**tool.function.arguments)
          else:
            output = function_to_call(**tool.function.arguments)

          print(f'Function output: {output}')

          # Add each tool result to messages
          messages.append({
            'role': 'tool',
            'content': str(output),
            'name': tool.function.name
          })
        else:
          print(f'Function {tool.function.name} not found')

      # Continue the loop to let the model process tool results and decide next steps
      iteration += 1
    else:
      # No more tool calls - model has finished
      print(f'Assistant: {response.message.content}')
      break

  if iteration >= max_iterations:
    print(f"\n⚠️  Reached maximum iterations ({max_iterations}). Stopping auto-execution.")

  return messages


async def main() -> None:
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

      # Process the conversation with automatic tool execution
      messages = await process_model_response(client, messages)

    except KeyboardInterrupt:
      print("\nGoodbye!")
      break
    except Exception as e:
      print(f"Error: {e}")


if __name__ == "__main__":
  load_env()
  asyncio.run(main())
