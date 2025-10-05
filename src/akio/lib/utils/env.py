#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Tuple
import os
from ..tools.rag import RAG
from ...config.constants import ConstantConfig


def env_info() -> Tuple[str,str]:
  """
  Returns the operating system name and the default shell.

  Returns:
    A tuple containing the OS name and the default shell.
  """
  os_name = __import__('platform').system()
  sh = os.environ.get('SHELL', 'bash')
  return os_name, sh


def get_system_prompt(file_path: str = ConstantConfig.SYSTEM_PROMPT_PATH) -> str:
  """
  Returns the system prompt for the AI agent.

  Args:
    file_path (str): The system prompt file path.

  Returns:
    str: A string containing the content of the system prompt file.
  """
  with open(file_path, 'r', encoding='utf8') as file:
    return file.read()


def load_env(env_path: str = ".env") -> None:
  """
  Load environment variables from the `.env` file.

  Args:
    env_path (str): The path to the `.env` file.
  """
  with open(env_path, 'r', encoding='utf8') as file:
    for line in file:
      line = line.strip()
      if line and not line.startswith('#'):
        if '=' in line:
          key, value = line.split('=', 1)
          key = key.strip()
          value = value.strip()
          if (value.startswith('"') and value.endswith('"')) or \
             (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
          os.environ[key] = value


def create_vdb_if_needed() -> None:
  """
  Create the vector database if it does not already exist.
  """
  rag = RAG(str(ConstantConfig.VECTOR_DB_PATH))
  if not rag.collection.count():
    print("No data found in vector DB. Indexing documents...")
    rag.load(ConstantConfig.DATASETS_PATH)
    rag.chunk()
    rag.vector_store()
    print("Vector store ready.")
  else:
    print(f"Loaded existing vector DB with {rag.collection.count()} entries.")
