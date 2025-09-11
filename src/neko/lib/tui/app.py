#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""WARN: This is AI generated code. It need a rewrite."""

import logging
from ..mcp.client import MCPClient
from ..utils.env import get_system_prompt
# from ..utils.database import *
from ...config.constants import ConstantConfig
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.text import Text
from rich.box import ROUNDED
from rich.align import Align
from rich.status import Status


logger = logging.getLogger(__name__)


class EnhancedChatTUI:
  """Enhanced Terminal User Interface for chat interactions."""

  def __init__(self):
    """Initialize the TUI with Rich console."""
    self.console = Console()
    self.setup_styles()

  def setup_styles(self):
    """Setup custom styles for the TUI."""
    self.primary_color = "bright_cyan"
    self.secondary_color = "bright_magenta"
    self.success_color = "bright_green"
    self.warning_color = "bright_yellow"
    self.error_color = "bright_red"
    self.text_color = "white"

  def display_welcome(self):
    """Display welcome message and instructions."""
    welcome_text = """
# 🤖 AI Chat Assistant

Welcome to your interactive AI assistant! Here are some things you can do:

- **Ask questions** about any topic
- **Request code** examples or explanations
- **Get help** with problem-solving
- **Have a conversation** about anything

## Commands:
- Type your message and press Enter
- Use `quit`, `exit`, or `q` to exit
- Use `clear` to clear the screen
- Use `help` to show this message again
    """

    welcome_panel = Panel(
      Markdown(welcome_text),
      title="[bold bright_cyan]AI Chat Assistant[/bold bright_cyan]",
      border_style=self.primary_color,
      box=ROUNDED,
      padding=(1, 2)
    )

    self.console.print()
    self.console.print(Align.center(welcome_panel))
    self.console.print()

  def display_help(self):
    """Display help information."""
    help_text = """
## Available Commands:
- `quit`, `exit` - Exit the chat
- `clear` - Clear the screen
- `help` - Show this help message
- `history` - Show conversation history
- `stats` - Show session statistics

## Tips:
- You can ask about anything - coding, math, science, general knowledge
- Request code in specific languages by mentioning the language
- Ask for explanations, examples, or step-by-step guides
    """

    help_panel = Panel(
      Markdown(help_text),
      title="[bold bright_yellow]Help & Commands[/bold bright_yellow]",
      border_style=self.warning_color,
      box=ROUNDED
    )

    self.console.print(help_panel)

  def display_thinking(self) -> Status:
    """Display thinking/processing animation."""
    return self.console.status(
      "[bold bright_cyan]🤔 Thinking...[/bold bright_cyan]",
      spinner="dots"
    )

  def display_user_message(self, message: str):
    """Display user message in a styled format.

    Args:
      message: User's input message.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    user_text = Text()
    user_text.append("🥷 You", style=f"bold {self.success_color}")
    user_text.append(f" [{timestamp}]", style="dim")

    user_panel = Panel(
      message,
      title=user_text,
      border_style=self.success_color,
      box=ROUNDED,
      padding=(0, 1)
    )

    self.console.print(user_panel)

  def display_ai_response(self, response: str):
    """Display AI response with markdown rendering.

    Args:
      response: AI's response content.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    ai_text = Text()
    ai_text.append("🤖 Assistant", style=f"bold {self.primary_color}")
    ai_text.append(f" [{timestamp}]", style="dim")

    # Render response as markdown
    markdown_response = Markdown(response)

    ai_panel = Panel(
      markdown_response,
      title=ai_text,
      border_style=self.primary_color,
      box=ROUNDED,
      padding=(0, 1)
    )

    self.console.print(ai_panel)

  def display_error(self, error: str):
    """Display error message in styled format.

    Args:
      error: Error message to display.
    """
    error_text = Text()
    error_text.append("❌ Error", style=f"bold {self.error_color}")

    error_panel = Panel(
      f"[{self.error_color}]{error}[/{self.error_color}]",
      title=error_text,
      border_style=self.error_color,
      box=ROUNDED
    )

    self.console.print(error_panel)

  def display_info(self, message: str, title: str = "Info"):
    """Display informational message.

    Args:
      message: Information message.
      title: Panel title.
    """
    info_panel = Panel(
      f"[{self.warning_color}]{message}[/{self.warning_color}]",
      title=f"[bold {self.warning_color}]ℹ️ {title}[/bold {self.warning_color}]",
      border_style=self.warning_color,
      box=ROUNDED
    )

    self.console.print(info_panel)

  def get_user_input(self) -> str:
    """Get user input with custom prompt.

    Returns:
      User's input string.
    """
    return Prompt.ask(
      "\n[bold bright_green]Enter a message...[/bold bright_green]",
      console=self.console
    ).strip()

  def clear_screen(self):
    """Clear the terminal screen."""
    self.console.clear()
    self.display_welcome()

  def display_goodbye(self):
    """Display goodbye message."""
    goodbye_text = """
# 👋 Goodbye!

Thank you for using the AI Chat Assistant!
Have a great day! ✨
    """

    goodbye_panel = Panel(
      Markdown(goodbye_text),
      title="[bold bright_magenta]Farewell[/bold bright_magenta]",
      border_style=self.secondary_color,
      box=ROUNDED
    )

    self.console.print()
    self.console.print(Align.center(goodbye_panel))
    self.console.print()


async def _chat(mcp_client: MCPClient, messages: list = None) -> None:
  """Run an interactive chat loop with enhanced TUI.

  Args:
    mcp_client: The MCP client instance.
    messages: Initial messages for the conversation.
  """
  tui = EnhancedChatTUI()
  if messages is not None:
    mcp_client.messages = messages
  tui.clear_screen()
  message_count = 0
  session_start = datetime.now()
  while True:
    try:
      query = tui.get_user_input()
      if query.lower() in ['quit', 'exit']:
        break
      elif query.lower() == 'clear':
        tui.clear_screen()
        continue
      elif query.lower() == 'help':
        tui.display_help()
        continue
      elif query.lower() == 'history':
        if hasattr(mcp_client, 'messages') and mcp_client.messages:
          history_text = f"**Conversation History ({len(mcp_client.messages)} messages)**\n\n"
          for i, msg in enumerate(mcp_client.messages[-10:], 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100] + ('...' if len(msg.get('content', '')) > 100 else '')
            history_text += f"{i}. **{role.title()}**: {content}\n"
          tui.console.print(Panel(Markdown(history_text), title="📜 History", border_style="blue"))
        else:
          tui.display_info("No conversation history available.", "History")
        continue
      elif query.lower() == 'stats':
        session_duration = datetime.now() - session_start
        stats_text = f"""
**Session Statistics**

- **Messages sent**: {message_count}
- **Session duration**: {str(session_duration).split('.')[0]}
- **Started at**: {session_start.strftime('%Y-%m-%d %H:%M:%S')}
        """
        tui.console.print(Panel(Markdown(stats_text), title="📊 Statistics", border_style="green"))
        continue
      elif not query:
        continue
      tui.display_user_message(query)
      with tui.display_thinking():
        try:
          response = await mcp_client.query(query)
          message_count += 1
        except Exception as e:
          logger.error(f'Failed to process query: {e}')
          tui.display_error(f"Failed to process query: {str(e)}")
          continue
      if response and len(response) > 0:
        ai_response = response[-1].get('content', 'No response content available.')
        tui.display_ai_response(ai_response)
      else:
        tui.display_error("No response received from the assistant.")
      tui.console.print()
    except KeyboardInterrupt:
      tui.console.print("\n")
      tui.display_info("Use 'quit' or 'exit' to leave gracefully.", "Interrupted")
    except EOFError:
      break
    except Exception as e:
      logger.error(f'Unexpected error in chat loop: {e}')
      tui.display_error(f"Unexpected error: {str(e)}")
  tui.display_goodbye()
  session_duration = datetime.now() - session_start
  tui.display_info(
    f"Session ended. You sent {message_count} messages in {str(session_duration).split('.')[0]}.",
    "Session Summary"
  )


async def tui() -> None:
  """Initialize and run the TUI chat interface."""
  # TODO: retrieve messages from pocketbase
  messages = [
    {'role': 'system', 'content': get_system_prompt()},
    {"role": "assistant", "content": "What are we breaking today?"}
  ]

  mcp_client = MCPClient()

  try:
    await mcp_client.connect_to_server(
      str(ConstantConfig.MCP_SERVER_PATH)
    )
    await _chat(mcp_client, messages)
  except Exception as e:
    console = Console()
    console.print(
      Panel(
        f"[red]An error occurred while trying to run the MCP server connection:\n{e}[/red]",
        title="[bold red]❌ Connection Error[/bold red]",
        border_style="red"
      )
    )
  finally:
    await mcp_client.cleanup()
