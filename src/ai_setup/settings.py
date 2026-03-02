"""
Configuration and path resolution for AI model setup.

This module centralizes all constants and filesystem paths used by the
Ollama model installer.

Responsibilities:
- Define the default model name.
- Define minimum disk space requirements.
- Resolve project-relative cache directories.
- Provide a single source of truth for Ollama base URL and model storage path.

Important design decisions:
- Model files are stored in a project-local cache directory ('.cache/ollama_models')
  instead of the global Ollama storage.
- The cache directory is intentionally excluded from version control.
- Paths are resolved dynamically based on the project root to avoid reliance
  on the current working directory.

This module must contain configuration only.
No I/O, no network calls, no side effects.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / ".cache"
MODELS_DIR = CACHE_DIR / "ollama_models"

MODEL_NAME = "qwen2.5:3b"
MIN_FREE_GB = 5
OLLAMA_BASE_URL = "http://localhost:11434"