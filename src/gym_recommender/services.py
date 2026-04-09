"""Service-layer orchestration for API and console flows."""

from __future__ import annotations

from typing import Any, cast

from gym_recommender.data import generate_next_gym_id, load_database, save_database
from gym_recommender.models import GymRecord, SearchFilters
from gym_recommender.search import calculate_distance, search_gyms, sort_gyms


def _require_distance_coordinates(user_x: int | None, user_y: int | None) -> tuple[int, int]:
    if user_x is None or user_y is None:
        raise ValueError("distance sorting requires user_x and user_y")
    return user_x, user_y


def list_gyms() -> list[GymRecord]:
    """Return all gyms from the current database."""
    return load_database()


def get_gym_by_id(gym_id: int) -> GymRecord | None:
    """Return the gym record with a matching ID, if any."""
    return next((gym for gym in load_database() if gym["gym_id"] == gym_id), None)


def serialize_gym(
    gym: GymRecord,
    *,
    user_x: int | None = None,
    user_y: int | None = None,
) -> dict[str, Any]:
    """Build the API response payload for a gym record."""
    payload: dict[str, Any] = dict(cast(dict[str, Any], gym))
    payload["display_hours"] = _format_display_hours(gym)
    if user_x is not None and user_y is not None:
        payload["distance"] = round(
            calculate_distance(user_x, user_y, gym["x_coordinate"], gym["y_coordinate"]),
            2,
        )
    return payload


def _format_display_hours(gym: GymRecord) -> str:
    """Return a compact opening hours string for the UI."""
    if gym["is_24_hours"]:
        return "24 hours"
    return f"{gym['opening_time']:04d}-{gym['closing_time']:04d}"


def search_gym_records(filters: SearchFilters, sort_key: str = "none") -> list[dict[str, Any]]:
    """Search and return serialized gym records for API responses."""
    gyms = load_database()
    matches = search_gyms(gyms, filters)
    user_x = filters.get("user_x")
    user_y = filters.get("user_y")

    if sort_key == "distance":
        user_x, user_y = _require_distance_coordinates(user_x, user_y)
        matches = sort_gyms(matches, "distance", user_x=user_x, user_y=user_y)
    elif sort_key in {"price", "rating"}:
        matches = sort_gyms(matches, sort_key)

    return [serialize_gym(gym, user_x=user_x, user_y=user_y) for gym in matches]


def compare_gym_records(gym_ids: list[int]) -> list[dict[str, Any]]:
    """Compare 2-3 gyms and return serialized records."""
    gyms = load_database()
    if len(gym_ids) < 2 or len(gym_ids) > 3:
        raise ValueError("Please compare 2 or 3 gyms")
    if len(set(gym_ids)) != len(gym_ids):
        raise ValueError("Gym comparison requires 2 or 3 distinct gym IDs")

    gym_lookup = {gym["gym_id"]: gym for gym in gyms}
    missing_ids = [gym_id for gym_id in gym_ids if gym_id not in gym_lookup]
    if missing_ids:
        raise ValueError("One or more gyms were not found")

    selected = [gym_lookup[gym_id] for gym_id in gym_ids]
    return [serialize_gym(gym) for gym in selected]


def create_gym_record(payload: GymRecord) -> dict[str, Any]:
    """Create a new gym record and persist it."""
    gyms = load_database()
    new_record = cast(GymRecord, dict(payload))
    new_record["gym_id"] = generate_next_gym_id(gyms)
    gyms.append(new_record)
    save_database(gyms)
    return serialize_gym(new_record)


def update_gym_record(gym_id: int, payload: GymRecord) -> dict[str, Any] | None:
    """Replace a gym record with the provided payload."""
    gyms = load_database()
    for index, gym in enumerate(gyms):
        if gym["gym_id"] == gym_id:
            updated_record = cast(GymRecord, dict(payload))
            updated_record["gym_id"] = gym_id
            gyms[index] = updated_record
            save_database(gyms)
            return serialize_gym(updated_record)
    return None
