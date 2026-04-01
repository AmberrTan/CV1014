"""Search and sorting utilities for gym records."""

from __future__ import annotations

import math

from gym_recommender.models import GymRecord, SearchFilters


def calculate_distance(user_x: int, user_y: int, gym_x: int, gym_y: int) -> float:
    """Return Euclidean distance in the dataset's coordinate space."""
    return math.sqrt((gym_x - user_x) ** 2 + (gym_y - user_y) ** 2)


def is_open_at(gym: GymRecord, time_value: int) -> bool:
    """Return True if a gym is open at the given HHMM time."""
    if gym["is_24_hours"]:
        return True
    return gym["opening_time"] <= time_value <= gym["closing_time"]


def search_gyms(gyms: list[GymRecord], filters: SearchFilters) -> list[GymRecord]:
    """Filter gyms based on the supplied search filters."""
    matches: list[GymRecord] = []
    required_facilities = {item.casefold() for item in filters.get("required_facilities", [])}
    target_area = filters.get("area")
    target_gym_type = filters.get("gym_type")

    for gym in gyms:
        if target_area and gym["area"].casefold() != target_area.casefold():
            continue
        if "max_budget" in filters and gym["monthly_price"] > filters["max_budget"]:
            continue
        if "min_rating" in filters and gym["rating"] < filters["min_rating"]:
            continue
        if "open_at" in filters and not is_open_at(gym, filters["open_at"]):
            continue
        if "is_24_hours" in filters and gym["is_24_hours"] is not filters["is_24_hours"]:
            continue
        if "classes_available" in filters and gym["classes_available"] is not filters["classes_available"]:
            continue
        if "female_friendly" in filters and gym["female_friendly"] is not filters["female_friendly"]:
            continue
        if target_gym_type and gym["gym_type"].casefold() != target_gym_type.casefold():
            continue

        gym_facilities = {facility.casefold() for facility in gym["facilities"]}
        if not required_facilities.issubset(gym_facilities):
            continue

        matches.append(gym)

    return matches


def sort_gyms(
    gyms: list[GymRecord],
    sort_key: str,
    user_x: int | None = None,
    user_y: int | None = None,
    scored_gyms: dict[int, float] | None = None,
) -> list[GymRecord]:
    """Sort gyms by a requested key while preserving deterministic tie breaks."""
    if sort_key == "price":
        return sorted(gyms, key=lambda gym: (gym["monthly_price"], -gym["rating"]))
    if sort_key == "rating":
        return sorted(gyms, key=lambda gym: (-gym["rating"], gym["monthly_price"]))
    if sort_key == "distance":
        if user_x is None or user_y is None:
            raise ValueError("distance sorting requires user_x and user_y")
        return sorted(
            gyms,
            key=lambda gym: calculate_distance(user_x, user_y, gym["x_coordinate"], gym["y_coordinate"]),
        )
    if sort_key == "score" and scored_gyms:
        return sorted(
            gyms,
            key=lambda gym: (-scored_gyms.get(gym["gym_id"], 0.0), -gym["rating"], gym["monthly_price"]),
        )
    return gyms[:]
