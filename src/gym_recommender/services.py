"""Service-layer orchestration for API and console flows."""

from __future__ import annotations

from typing import Any

from gym_recommender.data import generate_next_gym_id, load_database, save_database
from gym_recommender.models import GymRecord, SearchFilters, UserPreferences
from gym_recommender.recommendation import build_recommendation_reason, calculate_match_score, recommend_gyms
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
    score: float | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Build the API response payload for a gym record."""
    payload: dict[str, Any] = dict(gym)
    payload["display_hours"] = _format_display_hours(gym)
    if user_x is not None and user_y is not None:
        payload["distance"] = round(
            calculate_distance(user_x, user_y, gym["x_coordinate"], gym["y_coordinate"]),
            2,
        )
    if score is not None:
        payload["recommendation_score"] = score
    if reason is not None:
        payload["recommendation_reason"] = reason
    return payload


def _format_display_hours(gym: GymRecord) -> str:
    """Return a compact opening hours string for the UI."""
    if gym["is_24_hours"]:
        return "24 hours"
    return f"{gym['opening_time']:04d}-{gym['closing_time']:04d}"


def _search_preferences(filters: SearchFilters) -> UserPreferences:
    """Translate search filters into recommendation preferences."""
    prefs: UserPreferences = {}
    if "area" in filters:
        prefs["preferred_area"] = filters["area"]
    if "max_budget" in filters:
        prefs["max_budget"] = filters["max_budget"]
    if "min_rating" in filters:
        prefs["min_rating"] = filters["min_rating"]
    if "required_facilities" in filters:
        prefs["preferred_facilities"] = filters["required_facilities"]
    if "user_x" in filters and "user_y" in filters:
        prefs["user_x"] = filters["user_x"]
        prefs["user_y"] = filters["user_y"]
    if filters.get("classes_available"):
        prefs["classes_required"] = filters["classes_available"]
    if filters.get("female_friendly"):
        prefs["female_friendly"] = filters["female_friendly"]
    if "gym_type" in filters:
        prefs["preferred_gym_type"] = filters["gym_type"]
    if "open_at" in filters:
        prefs["preferred_time"] = filters["open_at"]
    return prefs


def search_gym_records(filters: SearchFilters, sort_key: str = "none") -> list[dict[str, Any]]:
    """Search and return serialized gym records for API responses."""
    gyms = load_database()
    matches = search_gyms(gyms, filters)
    scored_gyms: dict[int, float] | None = None
    score_reasons: dict[int, str] = {}
    user_x = filters.get("user_x")
    user_y = filters.get("user_y")

    if sort_key == "score":
        prefs = _search_preferences(filters)
        scored_gyms = {}
        for gym in matches:
            score = calculate_match_score(gym, prefs)
            scored_gyms[gym["gym_id"]] = score
            score_reasons[gym["gym_id"]] = build_recommendation_reason(gym, prefs, score)
        matches = sort_gyms(matches, "score", scored_gyms=scored_gyms)
    elif sort_key == "distance":
        user_x, user_y = _require_distance_coordinates(user_x, user_y)
        matches = sort_gyms(
            matches,
            "distance",
            user_x=user_x,
            user_y=user_y,
        )
    elif sort_key in {"price", "rating"}:
        matches = sort_gyms(matches, sort_key)

    return [
        serialize_gym(
            gym,
            user_x=user_x,
            user_y=user_y,
            score=scored_gyms.get(gym["gym_id"]) if scored_gyms else None,
            reason=score_reasons.get(gym["gym_id"]),
        )
        for gym in matches
    ]


def recommend_gym_records(prefs: UserPreferences) -> list[dict[str, Any]]:
    """Return serialized recommendation payloads."""
    gyms = load_database()
    recommendations = recommend_gyms(gyms, prefs)
    return [
        serialize_gym(
            gym,
            user_x=prefs.get("user_x"),
            user_y=prefs.get("user_y"),
            score=score,
            reason=reason,
        )
        for gym, score, reason in recommendations
    ]


def compare_gym_records(gym_ids: list[int], prefs: UserPreferences | None = None) -> list[dict[str, Any]]:
    """Compare 2-3 gyms with optional recommendation scoring."""
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

    if prefs:
        compared_gyms: list[dict[str, Any]] = []
        for gym in selected:
            score = calculate_match_score(gym, prefs)
            compared_gyms.append(
                serialize_gym(
                    gym,
                    user_x=prefs.get("user_x"),
                    user_y=prefs.get("user_y"),
                    score=score,
                    reason=build_recommendation_reason(gym, prefs, score),
                )
            )
        return compared_gyms
    return [serialize_gym(gym) for gym in selected]


def create_gym_record(payload: GymRecord) -> dict[str, Any]:
    """Create a new gym record and persist it."""
    gyms = load_database()
    new_record = dict(payload)
    new_record["gym_id"] = generate_next_gym_id(gyms)
    gyms.append(new_record)
    save_database(gyms)
    return serialize_gym(new_record)


def update_gym_record(gym_id: int, payload: GymRecord) -> dict[str, Any] | None:
    """Replace a gym record with the provided payload."""
    gyms = load_database()
    for index, gym in enumerate(gyms):
        if gym["gym_id"] == gym_id:
            updated_record = dict(payload)
            updated_record["gym_id"] = gym_id
            gyms[index] = updated_record
            save_database(gyms)
            return serialize_gym(updated_record)
    return None
