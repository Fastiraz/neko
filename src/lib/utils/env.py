#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Tuple
import os


def env_info() -> Tuple[str,str]:
    """
    Returns the operating system name and the default shell.

    :return:
    --------
        A tuple containing the OS name and the default shell.
    """
    os_name = __import__('platform').system()
    sh = os.environ.get('SHELL', 'bash')

    return os_name, sh


def get_system_prompt(file_path: str = "knowledge/prompt.txt") -> str:
    """
    Returns the system prompt for the AI agent.

    :args:
    ------
        file_path (str): The system prompt file path.

    :return:
    --------
        str: A string containing the content of the system prompt file.
    """
    with open(file_path, 'r', encoding='utf8') as file:
        try:
            return file.read()
        except:
            return None


def load_env(env_path: str = ".env") -> None:
    """
    Load environment variables in the given *. env* file.

    :args:
    ------
        env_path (str): The file path to the file containing environment variables.
    """
    with open(env_path, 'r', encoding='utf8') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

