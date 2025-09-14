#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from .lib.utils.env import load_env, create_vdb_if_needed
from .config.init import init


def main() -> None:
  load_env()
  init()
  create_vdb_if_needed()
  logging.basicConfig(filename='neko.log', level=logging.INFO)
  from .lib.utils.cli import create_cli_handler
  from .lib.tui.app import tui
  cli_handler = create_cli_handler(
    tui,
    load_env
  )
  asyncio.run(cli_handler.run())


if __name__ == "__main__":
  main()
