#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ...config.settings import Settings
from browser_use import (
  Agent,
  Tools,
  ChatOllama,
  Controller,
  ActionResult,
)
from browser_use.agent.views import AgentHistoryList


SYSTEM_MESSAGE = """
You are a profesional pentester. Your goal is to find vulnerabilities manually. Test every inputs of the website and every parameters in URL.
Once you found it, explain me why it's vulnerable, which payload have you use and which result do you have.
Test for SQL injection, XSS, SSTI...
When you find a vulnerability, stop.
"""
EXTEND_SYSTEM_MESSAGE = """
You are a profesional pentester. Your goal is to find vulnerabilities manually. Test every inputs of the website and every parameters in URL.
Once you found it, explain me why it's vulnerable, which payload have you use and which result do you have.
Test for SQL injection, XSS, SSTI...
When you find a vulnerability, stop.
"""
controller = Controller()


@controller.action('Ask human for help with a question')
def ask_human(question: str) -> ActionResult:
  """
  Allow a LLM to ask a question to a human.

  Args:
    question (str): The question.

  Returns:
    ActionResult: The human's answer.
  """
  answer = input(f'\x1b[48;5;235m\x1b[91m{question}\x1b[0m\n> ')
  return ActionResult(
    extracted_content=f'The human responded with: {answer}',
    include_in_memory=True
  )


async def web_browser_tool(prompt: str) -> AgentHistoryList:
  # Initialize tools
  tools = Tools()

  # Create agent with MCP-enabled tools
  agent = Agent(
    task=prompt,
    llm = ChatOllama(
      host=Settings.llm_provider_base_url,
      model=Settings.browser_model,
    ),
    tools=tools,
    controller=controller,
    # use_vision=True,
  )

  # Run the agent
  try:
    history = await agent.run()
    print("\nSession summary:")
    print(history.urls())
    print(history.screenshots())
    print(history.action_names())
    print(history.extracted_content())
    print(history.errors())
    print(history.model_actions())
    return history
  except Exception as e:
    print(f"Error during execution: {e}")
    return None
  finally:
    return None
