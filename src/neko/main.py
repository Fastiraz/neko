#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from .config.init import init
init()
from .lib.utils.env import create_vdb_if_needed
from .lib.utils.cli import create_cli_handler
from .lib.tui.app import tui


def main() -> None:
  create_vdb_if_needed()
  logging.basicConfig(filename='neko.log', level=logging.INFO)
  cli_handler = create_cli_handler(tui)
  asyncio.run(cli_handler.run())


if __name__ == "__main__":
  main()
