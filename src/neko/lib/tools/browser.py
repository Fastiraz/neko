#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
# import logging
from langchain_ollama import ChatOllama
from browser_use import Agent, Browser, Controller, ActionResult, BrowserConfig
from browser_use.agent.views import AgentHistoryList
# from browser_use.agent.memory import MemoryConfig
from ...config.settings import Settings


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
# logging.basicConfig(level=logging.DEBUG)
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
  return ActionResult(extracted_content=f'The human responded with: {answer}', include_in_memory=True)


# @controller.action('Take screenshot')
# async def take_screenshot(page: Page) -> ActionResult:
#     path = "screenshots"
#     Path(path).mkdir(exist_ok=True)
#     screenshot_path = f"{path}/screenshot_{page.url.replace('/', '_')}.png"
#     await page.screenshot(path=screenshot_path)
#     return ActionResult(extracted_content=f'Screenshot saved: {screenshot_path}')


async def on_step_start(agent: Agent):
  page = await agent.browser_session.get_current_page()
  print(f"Agent is now on: {page.url}")
  # await take_screenshot(page)


async def on_step_end(agent: Agent):
  history = agent.state.history
  print(f"Last action: {history.action_names()[-1] if history.action_names() else 'None'}")


async def web_browser_tool(prompt: str) -> AgentHistoryList:
  """
  This function allow an AI agent to perform tasks on a browser.

  Args:
    prompt (str): The task to do on the browser.

  Returns:
    AgentHistoryList: Browser task history.
  """
  config = BrowserConfig(
    headless=False,
    disable_security=False,
    # keep_alive=False,
    # viewport={"width": 1280, "height": 1100},
    # locale='en-US',
    # user_agent='0xcat - neko',
    # highlight_elements=True,
    # viewport_expansion=500,
    # extra_browser_args=[]  # ['--disable-web-security']
  )
  browser = Browser(config=config)
  # context = BrowserContext(browser=browser, config=config)
  llm = ChatOllama(
    base_url=Settings.llm_provider_base_url,
    model=Settings.browser_model,
    num_ctx=4096
  )
  # planner_llm = ChatOllama(
  #   base_url=os.environ.get(
  #     'OLLAMA_HOST',
  #     'http://localhost:11434'
  #   ).strip().strip('"'),
  #   model=os.environ.get(
  #     'BROWSER_PLANNER_MODEL',
  #     'deepseek-r1:14b'
  #   ).strip().strip('"'),
  #   num_ctx=8192
  # )
  # memory_config = MemoryConfig(
  #     agent_id="pentester_agent",
  #     memory_interval=15,
  #     embedder_provider="ollama",
  #     embedder_model=os.environ.get(
  #         'EMBED_MODEL',
  #         'mxbai-embed-large:latest'
  #     ).strip().strip('"'),
  #     embedder_dims=768,
  #     vector_store_provider="chroma",
  #     vector_store_collection_name="browser_use_memories",
  #     vector_store_config_override={
  #         "host": "localhost",
  #         "port": 8000
  #     }
  # )
  # Sensitive Data Configuration
  # sensitive_data = {
  #     'https://*.example.com': {
  #         'username': 'test',
  #         'password': 'test123'
  #     },
  # }
  agent = Agent(
    task=prompt,
    llm=llm,
    # browser=browser,
    # browser_context=context,
    controller=controller,
    use_vision=True,
    # planner_llm=planner_llm,
    # use_vision_for_planner=False,
    # planner_interval=10,
    save_conversation_path="logs/conversation",
    # message_context="This is a pentesting session. Be thorough in testing security vulnerabilities.",
    # max_actions_per_step=10,
    # max_failures=3,
    # retry_delay=10,
    generate_gif=False,
    # sensitive_data=sensitive_data,
    # override_system_message=SYSTEM_MESSAGE,
    # extend_system_message=EXTEND_SYSTEM_MESSAGE,
    # enable_memory=True,
    # memory_config=memory_config
  )
  try:
    history = await agent.run(
      # on_step_start=on_step_start,
      # on_step_end=on_step_end,
      # max_steps=30
    )
    print("\nSession summary:")
    print(history.urls())
    print(history.screenshots())
    print(history.action_names())
    print(history.extracted_content())
    print(history.errors())
    print(history.model_actions())
    await browser.close()
    return history
  except Exception as e:
    print(f"Error during execution: {e}")
    return None
  finally:
    await browser.close()
    return None
