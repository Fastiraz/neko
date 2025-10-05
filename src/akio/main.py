#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from .config.init import init
init()
from .lib.utils.env import create_vdb_if_needed
from .lib.utils.cli import run_cli
from .lib.tui.app import tui


def main() -> None:
  create_vdb_if_needed()
  logging.basicConfig(
    filename='akio.log',
    level=logging.INFO,
    # format='[%(asctime)s] %(levelname)s - %(message)s',
  )
  # cli_handler = create_cli_handler(tui)
  # asyncio.run(cli_handler.run())
  run_cli()


if __name__ == "__main__":
  main()
