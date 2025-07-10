#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import ollama
import asyncio
import streamlit as st
from typing import List, Dict, Any
from lib.tools.shell import shell_tool
from lib.tools.rag import RAG
from lib.tools.browser import web_browser_tool
from lib.tools.message import ask_user_tool
from lib.tools.web_search import ddg_search
from lib.utils.env import load_env, get_system_prompt


def rag_tool(query: str) -> str:
  """
  Combines retrieval and generation with improved prompt formatting.

  :args:
  ------
    prompt (str): The query to search in vectorial database

  :return:
  --------
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
  :args:
  ------
    client (ollama.AsyncClient): The Ollama async client instance
    messages (List[Dict[str, Any]]): List of messages with role/content
    max_iterations (int): Maximum number of iterations to prevent infinite loops
  :return:
  --------
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
        web_browser_tool,
        rag_tool,
        ask_user_tool,
        ddg_search
      ],
    )
    messages.append(response.message)
    if response.message.tool_calls:
      st.toast(
        body=f"\n--- Processing {len(response.message.tool_calls)} tool call(s) ---",
        icon=None
      )
      for tool in response.message.tool_calls:
        if function_to_call := available_functions.get(tool.function.name):
          st.toast(f'Calling function: {tool.function.name}')
          st.toast(f'Arguments: {tool.function.arguments}')
          if asyncio.iscoroutinefunction(function_to_call):
            output = await function_to_call(**tool.function.arguments)
          else:
            output = function_to_call(**tool.function.arguments)
          st.toast(f'Function output: {output}')
          # add each tool result to messages
          messages.append({
            'role': 'tool',
            'content': str(output),
            'name': tool.function.name
          })
        else:
          st.toast(f'Function {tool.function.name} not found')
      # continue the loop to let the model process tool results and decide next steps
      iteration += 1
    else:
      # no more tool calls - model has finished
      st.toast(f'Assistant: {response.message.content}')
      break
  if iteration >= max_iterations:
    st.toast(f"\n⚠️  Reached maximum iterations ({max_iterations}). Stopping auto-execution.")
  return messages


def create_vdb_if_needed():
  VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vectordb")
  DATASETS_PATH = os.getenv("DATASETS_PATH", "datasets")
  rag = RAG(VECTOR_DB_PATH)
  if not rag.collection.count():
    st.toast("No data found in vector DB. Indexing documents...")
    rag.load(DATASETS_PATH)
    rag.chunk()
    rag.vector_store()
    st.toast("Vector store ready.")
  else:
    st.toast(f"Loaded existing vector DB with {rag.collection.count()} entries.")


async def main() -> None:
  create_vdb_if_needed()
  st.set_page_config(
    page_title="neko",
    page_icon="🐈",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
      'Get Help': 'https://github.com/Fastiraz/neko/issues',
      'Report a bug': "https://github.com/Fastiraz/neko/issues",
      'About': "An agentic AI for red team tasks."
    }
  )

  st.markdown("""
  <style>
    .stChatInput, .stChatInput:focus {
      border-radius: 8px;
    }
    .st-emotion-cache-jmw8un {
      background-color: #efb8fa !important;
    }
  </style>
  """, unsafe_allow_html=True)

  with st.sidebar:
    st.title("🐈 | neko")
    st.caption("by Fastiraz")
    st.divider()
    models = [model["model"] for model in ollama.list()["models"]]
    st.session_state["model"] = st.selectbox("Choose your model", models)
    os.environ['MODEL'] = st.session_state["model"]
    st.divider()

  st.title("💬 neko")
  st.caption("An agentic AI for red team tasks.")

  if "messages" not in st.session_state:
    st.session_state["messages"] = [
      {
        'role': 'system',
        'content': get_system_prompt(),
      },
      {
        "role": "assistant",
        "content": "What are we breaking today?"
      }
    ]

  for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
      st.chat_message(msg["role"]).write(msg["content"])

  if prompt := st.chat_input():
    client = ollama.AsyncClient()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = await process_model_response(
      client,
      st.session_state.messages
    )
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(response[-1].content)


if __name__ == "__main__":
  load_env()
  asyncio.run(main())
