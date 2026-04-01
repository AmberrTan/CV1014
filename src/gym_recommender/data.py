"""Read/write helpers for the gym JSON database."""

from __future__ import annotations

import json
import os
from pathlib import Path

from gym_recommender.config import ROOT_DIR, load_dotenv
from gym_recommender.models import GymRecord

load_dotenv()
DEFAULT_DATABASE_PATH = ROOT_DIR / os.environ.get("GYM_DATABASE_PATH", "data/gyms.json")


def load_database(path: Path = DEFAULT_DATABASE_PATH) -> list[GymRecord]:
    """Load gym records from disk.

    Args:
        path: JSON file containing the gym list.

    Returns:
        A list of gym records parsed from the JSON file.
    """
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return list(data)


def save_database(gyms: list[GymRecord], path: Path = DEFAULT_DATABASE_PATH) -> None:
    """Persist gym records to disk.

    Args:
        gyms: Gym records to save.
        path: Destination JSON file.
    """
    with path.open("w", encoding="utf-8") as file:
        json.dump(gyms, file, indent=2)


def generate_next_gym_id(gyms: list[GymRecord]) -> int:
    """Compute the next integer gym ID for an append-only list."""
    if not gyms:
        return 1
    return max(gym["gym_id"] for gym in gyms) + 1
