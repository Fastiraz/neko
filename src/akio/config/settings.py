from dataclasses import dataclass
import json

from .constants import ConstantConfig


@dataclass
class Settings:
  with open(ConstantConfig.AKIO_CONFIG_FILE, 'r', encoding='utf-8') as f:
    _config = json.load(f)
  llm_provider_base_url = _config['llm_provider_base_url']
  base_model = _config['base_model']
  embedding_model = _config['embedding_model']
  vision_model = _config['vision_model']
  coding_model = _config['coding_model']
  browser_model = _config['browser_model']
  baas_base_url = _config['baas_base_url']
  chroma_base_url = _config['chroma_base_url']
