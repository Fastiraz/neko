#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from .constants import ConstantConfig


class Config:
  def __init__(self):
    self.create_config_folder_not_exists()
    self.create_config_file()

  def create_config_folder_not_exists(self) -> None:
    if not os.path.exists(ConstantConfig.NEKO_CONFIG_PATH):
      os.makedirs(ConstantConfig.NEKO_CONFIG_PATH)

  def create_config_file(self) -> None:
    if not os.path.exists(ConstantConfig.NEKO_CONFIG_FILE):
      open(ConstantConfig.NEKO_CONFIG_FILE, 'a').close()
    # TODO: Write the default settings into the file.

  # TODO: Create the datasets folder and downloads the default datasets.

  # TODO: Create the knowledge folder and the default system prompt


def init() -> None
  config = Config()
