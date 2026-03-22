from __future__ import annotations

import json
from pathlib import Path

from gym_recommender.models import GymRecord

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "gyms.json"


def load_database(path: Path = DEFAULT_DATABASE_PATH) -> list[GymRecord]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return list(data)


def save_database(gyms: list[GymRecord], path: Path = DEFAULT_DATABASE_PATH) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(gyms, file, indent=2)


def generate_next_gym_id(gyms: list[GymRecord]) -> int:
    if not gyms:
        return 1
    return max(gym["gym_id"] for gym in gyms) + 1
