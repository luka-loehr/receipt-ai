#!/usr/bin/env python3
"""
Small path helpers shared across entrypoints.
"""

import os
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def path_to_file_url(path: str) -> str:
    """Convert a local path to a file:// URL."""
    return urljoin("file:", pathname2url(os.path.abspath(path)))


def ensure_directory(path: str | os.PathLike[str]) -> Path:
    """Ensure a directory exists and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_dir(path: str | os.PathLike[str]) -> Path:
    """Ensure the parent directory for a file path exists."""
    file_path = Path(path)
    return ensure_directory(file_path.parent)
