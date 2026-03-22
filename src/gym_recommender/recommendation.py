from __future__ import annotations

from gym_recommender.models import GymRecord, UserPreferences
from gym_recommender.search import calculate_distance, is_open_at

MAX_DISTANCE = 120.0


def passes_hard_filters(gym: GymRecord, prefs: UserPreferences) -> bool:
    preferred_area = prefs.get("preferred_area")
    if preferred_area and gym["area"].casefold() != preferred_area.casefold():
        return False
    if "max_budget" in prefs and gym["monthly_price"] > prefs["max_budget"]:
        return False
    if "min_rating" in prefs and gym["rating"] < prefs["min_rating"]:
        return False
    if prefs.get("classes_required") and not gym["classes_available"]:
        return False
    if prefs.get("female_friendly") and not gym["female_friendly"]:
        return False
    if "preferred_time" in prefs and not is_open_at(gym, prefs["preferred_time"]):
        return False

    requested_facilities = {facility.casefold() for facility in prefs.get("preferred_facilities", [])}
    gym_facilities = {facility.casefold() for facility in gym["facilities"]}
    return requested_facilities.issubset(gym_facilities)


def _rating_score(gym: GymRecord) -> float:
    return gym["rating"] / 5


def _price_score(gym: GymRecord, prefs: UserPreferences) -> float:
    budget = prefs.get("max_budget")
    if budget is None or budget <= 0:
        return 0.6
    gap = max(budget - gym["monthly_price"], 0.0)
    return max(0.0, min(1.0, gap / budget + 0.25))


def _distance_score(gym: GymRecord, prefs: UserPreferences) -> float:
    if "user_x" not in prefs or "user_y" not in prefs:
        return 0.5
    distance = calculate_distance(
        prefs["user_x"],
        prefs["user_y"],
        gym["x_coordinate"],
        gym["y_coordinate"],
    )
    return max(0.0, 1 - (distance / MAX_DISTANCE))


def _facility_score(gym: GymRecord, prefs: UserPreferences) -> float:
    requested = prefs.get("preferred_facilities", [])
    if not requested:
        return 0.5
    requested_set = {facility.casefold() for facility in requested}
    available_set = {facility.casefold() for facility in gym["facilities"]}
    return len(requested_set & available_set) / len(requested_set)


def _goal_environment_score(gym: GymRecord, prefs: UserPreferences) -> float:
    score = 0.4
    fitness_goal = prefs.get("fitness_goal", "").casefold()
    skill_level = prefs.get("skill_level", "").casefold()
    preferred_gym_type = prefs.get("preferred_gym_type", "").casefold()

    if preferred_gym_type and gym["gym_type"].casefold() == preferred_gym_type:
        score += 0.4
    if fitness_goal == "bodybuilding" and gym["gym_type"] in {"bodybuilding", "powerlifting"}:
        score += 0.3
    elif fitness_goal in {"general fitness", "weight loss"} and gym["gym_type"] in {
        "commercial",
        "public",
        "boutique",
        "premium",
    }:
        score += 0.3
    elif fitness_goal == "classes" and gym["classes_available"]:
        score += 0.3

    if skill_level == "beginner" and gym["beginner_friendly"]:
        score += 0.3
    elif skill_level == "advanced" and gym["gym_type"] in {"bodybuilding", "powerlifting"}:
        score += 0.2

    return min(score, 1.0)


def calculate_match_score(gym: GymRecord, prefs: UserPreferences) -> float:
    total = (
        0.30 * _rating_score(gym)
        + 0.25 * _price_score(gym, prefs)
        + 0.20 * _distance_score(gym, prefs)
        + 0.15 * _facility_score(gym, prefs)
        + 0.10 * _goal_environment_score(gym, prefs)
    )
    return round(total * 100, 2)


def build_recommendation_reason(gym: GymRecord, prefs: UserPreferences, score: float) -> str:
    reasons: list[str] = [f"match score {score:.2f}"]
    if gym["rating"] >= 4.5:
        reasons.append("high rating")
    if "max_budget" in prefs and gym["monthly_price"] <= prefs["max_budget"]:
        reasons.append("within budget")
    if prefs.get("classes_required") and gym["classes_available"]:
        reasons.append("has classes")
    if prefs.get("female_friendly") and gym["female_friendly"]:
        reasons.append("female-friendly")
    preferred_facilities = {facility.casefold() for facility in prefs.get("preferred_facilities", [])}
    available_facilities = {facility.casefold() for facility in gym["facilities"]}
    matched_facilities = sorted(preferred_facilities & available_facilities)
    if matched_facilities:
        reasons.append(f"matches facilities: {', '.join(matched_facilities[:3])}")
    return "; ".join(reasons)


def recommend_gyms(
    gyms: list[GymRecord],
    prefs: UserPreferences,
) -> list[tuple[GymRecord, float, str]]:
    recommendations: list[tuple[GymRecord, float, str]] = []
    for gym in gyms:
        if not passes_hard_filters(gym, prefs):
            continue
        score = calculate_match_score(gym, prefs)
        reason = build_recommendation_reason(gym, prefs, score)
        recommendations.append((gym, score, reason))

    recommendations.sort(key=lambda item: (-item[1], -item[0]["rating"], item[0]["monthly_price"]))
    return recommendations[:3]
