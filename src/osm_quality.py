from collections import Counter
from typing import Dict, Iterable, List

from .utils import split_normalized


def build_overpass_query(lat: float, lon: float, radius_m: int) -> str:
    return (
        "[out:json];\n"
        f"node[\"leisure\"=\"fitness_centre\"](around:{radius_m},{lat},{lon});\n"
        "out body;"
    )


def extract_tag_flags(tags: Dict[str, str]) -> Dict[str, bool]:
    return {
        "has_sport": "sport" in tags,
        "has_female_friendly": "female_friendly" in tags,
        "has_equipment": any(
            key in tags for key in ("equipment", "gym", "fitness_station")
        ),
    }


def split_sport_values(value: str) -> List[str]:
    return split_normalized(value)


def summarize_elements(elements: Iterable[Dict]) -> Dict[str, object]:
    totals = {
        "total": 0,
        "has_sport": 0,
        "has_female_friendly": 0,
        "has_equipment": 0,
        "sport_counts": Counter(),
    }

    for element in elements:
        totals["total"] += 1
        tags = element.get("tags", {})
        flags = extract_tag_flags(tags)

        if flags["has_sport"]:
            totals["has_sport"] += 1
            totals["sport_counts"].update(split_normalized(tags.get("sport", "")))
        if flags["has_female_friendly"]:
            totals["has_female_friendly"] += 1
        if flags["has_equipment"]:
            totals["has_equipment"] += 1

    return totals


def format_top_sports(counter: Counter, limit: int = 5) -> str:
    if not counter:
        return ""
    pairs = [f"{key}({count})" for key, count in counter.most_common(limit)]
    return ", ".join(pairs)
