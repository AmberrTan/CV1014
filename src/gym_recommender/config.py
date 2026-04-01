"""Project configuration helpers.

This module provides lightweight helpers for locating the repository root and
loading environment variables from a `.env` file. The loader is intentionally
minimal to keep dependencies small and predictable for coursework use.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV_PATH = ROOT_DIR / ".env"


def load_dotenv(path: Path = DEFAULT_ENV_PATH) -> None:
    """Populate os.environ with values from a .env file.

    The parser ignores blank lines, comments, and malformed entries. Existing
    environment variables are left untouched to allow shell overrides.

    Args:
        path: Location of the .env file.
    """
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]

        os.environ.setdefault(key, value)
