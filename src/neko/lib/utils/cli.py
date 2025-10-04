#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command Line Interface Handler.

This module handles all command-line argument parsing and execution
for the FastAPI server with MCP client functionality.
"""

import sys
import argparse
import subprocess
from ...config.constants import ConstantConfig


class CLIHandler:
  """Handles command-line interface operations."""

  def __init__(self, tui_func):
    """
    Initialize CLI handler with required functions.

    Args:
      tui_func: Function to run the chat loop.
    """
    self.tui = tui_func

  def _serve_api(self, host: str = "127.0.0.1", port: int = 1337) -> None:
    """
    Start the FastAPI server.

    Args:
      host: Host address to bind the server to.
      port: Port number to bind the server to.
    """
    try:
      cmd = [
        "uv", "run", "fastapi", "run", str(ConstantConfig.API_SERVER_PATH),
        f"--host={host}",
        f"--port={port}",
        "--reload"
      ]
      subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
      print(f"Error starting server: {e}")
      sys.exit(1)
    except KeyboardInterrupt:
      print("\nServer shutdown requested by user")
    except Exception as e:
      print(f"Unexpected error starting server: {e}")
      sys.exit(1)

  def parse_arguments(self) -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
      Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
      description="FastAPI server with MCP client functionality",
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog=f"""
Examples:
  {sys.argv[0]} serve --host=127.0.0.1 --port=1337
  {sys.argv[0]} serve
  {sys.argv[0]} --tui
      """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    serve_parser = subparsers.add_parser('serve', help='Start the FastAPI server')
    serve_parser.add_argument(
      '--host',
      type=str,
      default='127.0.0.1',
      help='Host address to bind the server to (default: 127.0.0.1)'
    )
    serve_parser.add_argument(
      '--port',
      type=int,
      default=1337,
      help='Port number to bind the server to (default: 1337)'
    )

    parser.add_argument(
      '--tui',
      action='store_true',
      help='Run the TUI chat loop'
    )
    parser.add_argument(
      'message',
      nargs='?',
      help='Message to print'
    )
    return parser.parse_args()

  async def handle_command(self) -> None:
    """Handle the parsed command-line arguments."""
    if len(sys.argv) == 1:
      self.parse_arguments().print_help()
      return
    args = self.parse_arguments()
    if args.command == 'serve':
      self._serve_api(args.host, args.port)
      return
    if args.tui:
      await self.tui()
      return
    if args.message:
      self.print_message(args.message)
      return
    self.parse_arguments().print_help()

  async def run(self) -> None:
    """Main entry point for CLI operations."""
    await self.handle_command()


def create_cli_handler(tui_func) -> CLIHandler:
  """Factory function to create a CLI handler.

  Args:
    tui_func: Function to run the chat loop.

  Returns:
    Configured CLIHandler instance.
  """
  return CLIHandler(tui_func)
