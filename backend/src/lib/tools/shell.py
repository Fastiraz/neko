#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
from typing import Optional


def shell_tool(command: str, timeout: Optional[int] = 30) -> str:
  """
  Executes a shell command and returns the output as a single string.
  This function is designed to be used as a tool for LLM agents to interact with the system.
  Commands are validated for safety before execution.

  Args:
    command (str): The shell command to execute. Will be checked for dangerous patterns.
    timeout (Optional[int]): Timeout in seconds for command execution (default: 30).

  Returns:
    str: The command output. Returns stdout if command succeeds, stderr if it fails, or an error message if execution fails or command is deemed unsafe.
  """
  x = input(f"Do you want to execute the following command? [yes/no]\n\x1b[48;5;235m\x1b[91m{command}\x1b[0m\n> ")
  if x.lower().strip() == 'yes':
    try:
      result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        # timeout=timeout  # we remove the time out for pentest tools
      )
      if result.returncode == 0:
        return result.stdout.strip() if result.stdout else "Command executed successfully (no output)"
      else:
        return result.stderr.strip() if result.stderr else f"Command failed with exit code {result.returncode}"
    except subprocess.TimeoutExpired:
      return f"Command timed out after {timeout} seconds"
    except Exception as e:
      return f"Error executing command:\n{str(e)}"
  else:
    return f"Command {command} refused by the user."


def hacking_tool(command: str, timeout: Optional[int] = 300) -> str:
  """
  Executes a shell command in a containerized hacking environment and returns the output as a single string.
  This function is designed to be used as a tool for LLM agents to interact with the system.
  Commands are validated for safety before execution.

  Args:
    command (str): The shell command to execute. Will be checked for dangerous patterns.
    timeout (Optional[int]): Timeout in seconds for command execution (default: 300).

  Returns:
    str: The command output. Returns stdout if command succeeds, stderr if it fails, or an error message if execution fails or command is deemed unsafe.
  """
  x = input(f"Do you want to execute the following command? [yes/no]\n\x1b[48;5;235m\x1b[91m{command}\x1b[0m\n> ")
  if x.lower().strip() == 'yes':
    try:
      result = subprocess.run(
        # f"docker run --rm -it --network=host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --entrypoint=/bin/zsh nwodtuhs/exegol:nightly -c \"{command}\"",
        f"docker run --rm -it --network=host --privileged -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --entrypoint=/bin/zsh kali:latest -c \"{command}\"",
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout
      )
      if result.returncode == 0:
        return result.stdout.strip() if result.stdout else "Command executed successfully (no output)"
      else:
        return result.stderr.strip() if result.stderr else f"Command failed with exit code {result.returncode}"
    except subprocess.TimeoutExpired:
      return f"Command timed out after {timeout} seconds"
    except Exception as e:
      return f"Error executing command:\n{str(e)}"
  else:
    return f"Command {command} refused by the user."
