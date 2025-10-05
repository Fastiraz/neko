#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def ask_user_tool(question: str, allow_empty: bool = True) -> str:
  """
  Allows the LLM to ask something to the user.

  Args:
    question (str): The question from the LLM
    allow_empty (bool): Whether to allow empty responses (default: True)

  Returns:
    str: The user's response
  """
  try:
    print(f"Agent: {question}")
    while True:
      response = input("\x1b[48;5;235m\x1b[93mYour response\x1b[0m\n> ")
      if allow_empty or response.strip():
        return response
      print("\x1b[91mPlease provide a response.\x1b[0m")
  except KeyboardInterrupt:
    print("\n\x1b[91mUser interrupted.\x1b[0m")
    return ""
  except EOFError:
    return ""
