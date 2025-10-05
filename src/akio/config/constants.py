from pathlib import Path

__version__ = "0.0.1-dev"


class ConstantConfig:
  """Constant parameters information"""
  # Akio Version
  version: str = __version__

  # 0xcat akio documentation link
  landing: str = "https://0xcat.io"
  documentation: str = "https://docs.0xcat.io"

  # OS Dir full root path of akio project
  src_root_path_obj: Path = Path(__file__).parent.parent.parent.resolve()

  # Path to the EULA docs
  eula_path: Path = src_root_path_obj / "akio/utils/docs/eula.md"

  # Akio config directory
  AKIO_CONFIG_PATH: Path = Path().home() / ".akio"

  # Akio config file
  AKIO_CONFIG_FILE: Path = AKIO_CONFIG_PATH / "settings.json"

  # Install mode, check if Akio has been git cloned or installed using pip package
  git_source_installation: bool = (src_root_path_obj / '.git').is_dir()
  pip_installed: bool = src_root_path_obj.name == "site-packages"
  pipx_installed: bool = "/pipx/venvs/" in src_root_path_obj.as_posix()
  uv_installed: bool = "/uv/tools/" in src_root_path_obj.as_posix()

  GITHUB_REPO: str = "Fastiraz/akio"

  # Vector database path
  VECTOR_DB_PATH: str = AKIO_CONFIG_PATH / "vectordb"

  # Datasets path
  DATASETS_PATH: str = AKIO_CONFIG_PATH / "datasets"

  # LLM system prompt path
  SYSTEM_PROMPT_PATH: str = AKIO_CONFIG_PATH / "knowledge/prompt.txt"

  # MCP server path
  MCP_SERVER_PATH: str = src_root_path_obj / "akio/lib/mcp/server.py"

  # API server path
  API_SERVER_PATH: str = src_root_path_obj / "akio/lib/api/routes.py"
