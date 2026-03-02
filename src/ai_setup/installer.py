__author__ = 'Mihail Mihaylov'
"""
Ollama model installation and verification logic.

This module contains pure setup logic for ensuring that a required
Ollama model is available locally inside the project cache directory.

Responsibilities:
- Check disk space availability.
- Ensure Ollama server is reachable.
- Verify if the model exists.
- Pull the model if missing.
- Perform a minimal verification generate call.

No CLI handling. No user interaction.
All failures raise exceptions.
"""

import os
import shutil
from typing import Dict, Any

import requests

from .settings import (
    PROJECT_ROOT,
    CACHE_DIR,
    MODELS_DIR,
    MODEL_NAME,
    MIN_FREE_GB,
    OLLAMA_BASE_URL,
    TAGS_TIMEOUT_S,
    PING_TIMEOUT_S,
    PULL_TIMEOUT_S,
    GENERATE_TIMEOUT_S,
    BYTES_IN_GB,
)


# ---------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------


def ensure_cache_directories() -> None:
    """
    Ensures that cache directories exist.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)


def check_disk_space(min_free_gb: int = MIN_FREE_GB) -> None:
    """
    Checks whether sufficient disk space is available.

    :param min_free_gb: Minimum required free space in GB.
    :raises RuntimeError: if not enough space.
    """
    usage = shutil.disk_usage(PROJECT_ROOT)
    free_gb = usage.free / BYTES_IN_GB

    if free_gb < min_free_gb:
        raise RuntimeError(
            f"Insufficient disk space. Required: {min_free_gb} GB, "
            f"available: {free_gb:.2f} GB."
        )


# ---------------------------------------------------------------------
# Ollama checks
# ---------------------------------------------------------------------


def ensure_ollama_running() -> None:
    """
    Ensures Ollama server is reachable.

    :raises RuntimeError: if server is not reachable.
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=PING_TIMEOUT_S)
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError("Ollama server is not running.") from exc


def model_exists(model_name: str = MODEL_NAME) -> bool:
    """
    Checks if the given model exists in Ollama.

    :param model_name: Model name to check.
    :return: True if model exists.
    """
    resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=TAGS_TIMEOUT_S)
    resp.raise_for_status()
    data: Dict[str, Any] = resp.json()

    for model in data.get("models", []):
        if model.get("name") == model_name:
            return True
    return False


def pull_model(model_name: str = MODEL_NAME) -> None:
    """
    Pulls the model via Ollama API.

    :param model_name: Model name to pull.
    :raises RuntimeError: if pull fails.
    """
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/pull",
        json={"model": model_name, "stream": False},
        timeout=PULL_TIMEOUT_S,
    )
    resp.raise_for_status()

    data = resp.json()
    status = data.get("status")

    if status and status.lower() not in ("success", "completed"):
        raise RuntimeError(f"Model pull failed: {data}")


def verify_model(model_name: str = MODEL_NAME) -> None:
    """
    Performs a minimal generate call to verify that the model works.

    :param model_name: Model name.
    :raises RuntimeError: if generation fails.
    """
    os.environ["OLLAMA_MODELS"] = str(MODELS_DIR)

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model_name,
            "prompt": "Respond with OK",
            "stream": False,
            "temperature": 0.0,
        },
        timeout=GENERATE_TIMEOUT_S,
    )
    resp.raise_for_status()

    data = resp.json()
    if "response" not in data:
        raise RuntimeError("Model verification failed.")
