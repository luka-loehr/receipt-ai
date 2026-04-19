#!/usr/bin/env python3
"""
Small path helpers shared across entrypoints.
"""

import os
from urllib.parse import urljoin
from urllib.request import pathname2url


def path_to_file_url(path: str) -> str:
    """Convert a local path to a file:// URL."""
    return urljoin("file:", pathname2url(os.path.abspath(path)))
