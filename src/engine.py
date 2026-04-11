from geopy.distance import geodesic
from typing import List, Dict, Iterable, Optional, Tuple
import httpx
import re
import logging
import asyncio
from .models import UserProfile, Gym, Recommendation, ScoreExplanation
from .data import MOCK_GYMS

MIN_RESULTS = 15
OSM_NAME_RE = re.compile(r"^gym\\s*\\d+$", re.IGNORECASE)
logger = logging.getLogger(__name__)
OVERPASS_API_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
DEFAULT_USER_AGENT = "CV1014-GymRecommendationSystem/1.0 (+https://openstreetmap.org)"


def normalize_tag_values(value: str) -> List[str]:
    if not value:
        return []
    parts = []
    for chunk in value.replace(",", ";").split(";"):
        cleaned = chunk.strip().lower()
        if cleaned:
            parts.append(cleaned)
    return parts


def extract_osm_values(tags: Dict[str, str], key: str) -> List[str]:
    return normalize_tag_values(tags.get(key, ""))


def extract_osm_equipment(tags: Dict[str, str]) -> List[str]:
    values: List[str] = []
    for key in ("equipment", "gym", "fitness_station"):
        values.extend(normalize_tag_values(tags.get(key, "")))
    return values


def extract_osm_facilities(tags: Dict[str, str]) -> List[str]:
    def is_truthy(value: str) -> bool:
        return value.strip().lower() in {"yes", "true", "1", "y"}

    facilities: List[str] = []
    if tags.get("opening_hours", "").strip().lower() == "24/7":
        facilities.append("24h")
    if is_truthy(tags.get("female_friendly", "")):
        facilities.append("female-friendly")
    if (
        is_truthy(tags.get("shower", ""))
        or is_truthy(tags.get("showers", ""))
        or is_truthy(tags.get("toilets:shower", ""))
    ):
        facilities.append("showers")
    if is_truthy(tags.get("locker", "")) or is_truthy(tags.get("lockers", "")):
        facilities.append("lockers")
    if (
        is_truthy(tags.get("classes", ""))
        or is_truthy(tags.get("fitness_classes", ""))
        or is_truthy(tags.get("group_classes", ""))
    ):
        facilities.append("classes")
    return facilities


TRUTHY_REGEX = "yes|true|1|y"


def _escape_regex_values(values: Iterable[str]) -> str:
    escaped = [re.escape(value) for value in values if value]
    return "|".join(escaped)


def _build_filter_suffixes(user: UserProfile) -> List[str]:
    suffixes: List[str] = []

    if user.access_24h:
        suffixes.append('["opening_hours"="24/7"]')

    if user.requires_classes:
        suffixes.extend([
            f'["classes"~"{TRUTHY_REGEX}"]',
            f'["fitness_classes"~"{TRUTHY_REGEX}"]',
            f'["group_classes"~"{TRUTHY_REGEX}"]',
        ])

    if user.female_friendly:
        suffixes.append(f'["female_friendly"~"{TRUTHY_REGEX}"]')

    sport_values = _escape_regex_values(normalize_user_filters(user.sport_filters))
    if sport_values:
        suffixes.append(f'["sport"~"{sport_values}"]')

    equipment_values = _escape_regex_values(normalize_user_filters(user.equipment_filters))
    if equipment_values:
        suffixes.append(f'["equipment"~"{equipment_values}"]')

    return suffixes or [""]


def _sport_regex_with_user(user: Optional[UserProfile], base_regex: str) -> str:
    if not user:
        return base_regex
    extra = _escape_regex_values(normalize_user_filters(user.sport_filters))
    if extra:
        return f"{base_regex}|{extra}"
    return base_regex


def build_overpass_query(lat: float, lon: float, radius_m: int, user: Optional[UserProfile] = None) -> str:
    suffixes = _build_filter_suffixes(user) if user else [""]
    selectors = [
        'nwr["leisure"="fitness_centre"]',
        'nwr["leisure"="fitness_station"]',
        f'nwr["leisure"="sports_centre"]["sport"~"{_sport_regex_with_user(user, "fitness|weightlifting|crossfit|gym")}"]',
        'nwr["amenity"="gym"]',
    ]
    parts = []
    for base in selectors:
        for suffix in suffixes:
            if '["sport"~' in base and user and normalize_user_filters(user.sport_filters):
                # Avoid adding a second sport filter on top of the sports_centre base.
                if '["sport"~' in suffix:
                    continue
            parts.append(f"{base}{suffix}(around:{radius_m},{lat},{lon});")
    return "[out:json][timeout:120];(" + "".join(parts) + ");out center tags;"


def build_overpass_country_query(country_code: str = "SG", user: Optional[UserProfile] = None) -> str:
    suffixes = _build_filter_suffixes(user) if user else [""]
    selectors = [
        'nwr["amenity"="gym"]',
        'nwr["leisure"="fitness_centre"]',
    ]
    parts = []
    for base in selectors:
        for suffix in suffixes:
            parts.append(f"{base}{suffix}(area.searchArea);")
    return (
        "[out:json][timeout:120];"
        f'area["ISO3166-1"="{country_code}"][admin_level=2]->.searchArea;'
        "("
        + "".join(parts) +
        ");out center tags;"
    )


def is_valid_osm_name(name: str) -> bool:
    if not name:
        return False
    return OSM_NAME_RE.match(name.strip()) is None


def get_element_location(element: Dict[str, object]) -> Optional[Tuple[float, float]]:
    if "lat" in element and "lon" in element:
        return (element["lat"], element["lon"])
    center = element.get("center")
    if isinstance(center, dict) and "lat" in center and "lon" in center:
        return (center["lat"], center["lon"])
    return None


def normalize_user_filters(values: Iterable[str]) -> List[str]:
    normalized = []
    for value in values:
        if value is None:
            continue
        cleaned = str(value).strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def user_has_hard_filters(user: UserProfile) -> bool:
    return bool(
        user.sport_filters
        or user.equipment_filters
        or user.access_24h
        or user.requires_classes
    )


def gym_matches_hard_filters(user: UserProfile, gym: Gym) -> bool:
    sport_filters = set(normalize_user_filters(user.sport_filters))
    equipment_filters = set(normalize_user_filters(user.equipment_filters))
    gym_sports = set(normalize_user_filters(gym.sports))
    gym_equipment = set(normalize_user_filters(gym.equipment))

    if sport_filters and not gym_sports.intersection(sport_filters):
        return False
    if equipment_filters and not gym_equipment.intersection(equipment_filters):
        return False
    if user.access_24h and "24h" not in gym.facilities:
        return False
    if user.requires_classes and "classes" not in gym.facilities:
        return False
    return True


def dedupe_gyms_by_name_location(gyms: List[Gym], threshold_km: float = 0.02) -> List[Gym]:
    deduped: List[Gym] = []
    for gym in gyms:
        is_duplicate = False
        for kept in deduped:
            if gym.name.strip().lower() == kept.name.strip().lower():
                if geodesic(gym.location, kept.location).km <= threshold_km:
                    is_duplicate = True
                    break
        if not is_duplicate:
            deduped.append(gym)
    return deduped


def _build_gym_from_element(element: Dict[str, object], tags: Dict[str, str]) -> Gym:
    gym_id = str(element.get("id"))
    price = 100.0 + (int(gym_id) % 150)
    facilities = extract_osm_facilities(tags)
    sports = extract_osm_values(tags, "sport")
    equipment = extract_osm_equipment(tags)
    location = get_element_location(element)
    return Gym(
        gym_id=gym_id,
        name=tags.get("name", ""),
        location=location,
        price=price,
        facilities=facilities,
        sports=sports,
        equipment=equipment,
        rating=4.0,
        popularity_score=0.5,
        tags=list(tags.keys()),
    )


def _filter_and_collect(
    elements: List[Dict[str, object]],
    *,
    distance_origin: Optional[Tuple[float, float]] = None,
    max_distance_km: Optional[float] = None,
) -> Tuple[List[Gym], int, int]:
    gyms: List[Gym] = []
    skipped_name = 0
    skipped_location = 0
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name", "")
        if not is_valid_osm_name(name):
            skipped_name += 1
            continue

        location = get_element_location(element)
        if not location:
            skipped_location += 1
            continue

        if distance_origin and max_distance_km is not None:
            if geodesic(distance_origin, location).km > max_distance_km:
                continue

        gyms.append(_build_gym_from_element(element, tags))

    return gyms, skipped_name, skipped_location


async def _fetch_overpass_payload(query: str, *, timeout: float, label: str) -> Optional[Dict[str, object]]:
    data = None
    async with httpx.AsyncClient(
        headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}
    ) as client:
        for url in OVERPASS_API_URLS:
            for attempt in range(1, 4):
                response = await client.post(
                    url,
                    data={"data": query},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=timeout,
                )
                logger.info(
                    "%s response url=%s status=%s attempt=%s body_preview=%s",
                    label,
                    url,
                    response.status_code,
                    attempt,
                    response.text[:500],
                )
                if response.status_code in RETRY_STATUS_CODES:
                    logger.warning(
                        "%s retryable status=%s url=%s attempt=%s",
                        label,
                        response.status_code,
                        url,
                        attempt,
                    )
                elif response.status_code >= 400:
                    logger.warning(
                        "%s non-200 status=%s url=%s attempt=%s",
                        label,
                        response.status_code,
                        url,
                        attempt,
                    )
                else:
                    try:
                        data = response.json()
                        break
                    except ValueError:
                        logger.error(
                            "%s invalid JSON response url=%s attempt=%s",
                            label,
                            url,
                            attempt,
                        )
                if attempt < 3:
                    await asyncio.sleep(1.0 * (2 ** (attempt - 1)))
            if data is not None:
                break
    return data


async def fetch_real_gyms_from_osm(lat: float, lon: float, radius_km: float = 5.0, user: Optional[UserProfile] = None) -> List[Gym]:
    """Fetch real gym data from OpenStreetMap using Overpass API"""
    radius_m = int(radius_km * 1000)
    query = build_overpass_query(lat, lon, radius_m, user=user)
    logger.info(
        "OSM fetch start lat=%s lon=%s radius_km=%s radius_m=%s",
        lat,
        lon,
        radius_km,
        radius_m,
    )
    logger.info("OSM query=%s", query)

    try:
        data = await _fetch_overpass_payload(query, timeout=30.0, label="OSM fetch")
        if data is None:
            logger.error("OSM fetch failed after retries")
            return []

        elements = data.get("elements", [])
        sample_names = []
        for element in elements[:5]:
            tags = element.get("tags", {})
            sample_names.append(tags.get("name") or "")
        logger.info(
            "OSM fetch elements total=%s sample_names=%s",
            len(elements),
            sample_names,
        )
        gyms, skipped_name, skipped_location = _filter_and_collect(elements)
        deduped = dedupe_gyms_by_name_location(gyms)
        logger.info(
            "OSM fetch results total=%s kept=%s skipped_name=%s skipped_location=%s deduped=%s",
            len(elements),
            len(gyms),
            skipped_name,
            skipped_location,
            len(deduped),
        )
        if len(deduped) > 0:
            return deduped

        country_query = build_overpass_country_query("SG", user=user)
        logger.info("OSM country query fallback=%s", country_query)
        data = await _fetch_overpass_payload(country_query, timeout=60.0, label="OSM country fetch")
        if data is None:
            logger.error("OSM country fetch failed after retries")
            return []

        elements = data.get("elements", [])
        sample_names = []
        for element in elements[:5]:
            tags = element.get("tags", {})
            sample_names.append(tags.get("name") or "")
        logger.info(
            "OSM country fetch elements total=%s sample_names=%s",
            len(elements),
            sample_names,
        )
        gyms, skipped_name, skipped_location = _filter_and_collect(
            elements,
            distance_origin=(lat, lon),
            max_distance_km=radius_km,
        )
        deduped = dedupe_gyms_by_name_location(gyms)
        logger.info(
            "OSM country fetch results total=%s kept=%s skipped_name=%s skipped_location=%s deduped=%s",
            len(elements),
            len(gyms),
            skipped_name,
            skipped_location,
            len(deduped),
        )
        return deduped
    except Exception as e:
        logger.exception("OSM Fetch Error: %s", e)
        return []


def calculate_distance_score(distance_km: float, max_dist_km: float) -> float:
    """Closer = Higher Score [0, 1]"""
    if distance_km > max_dist_km:
        return 0.0
    if max_dist_km == 0:
        return 1.0
    return max(0.0, 1.0 - (distance_km / max_dist_km))


def calculate_budget_score(gym_price: float, budget_range: tuple) -> float:
    """Match between user budget and gym pricing [0, 1]"""
    min_b, max_b = budget_range
    if min_b <= gym_price <= max_b:
        return 1.0
    if gym_price < min_b:
        # User budget is higher than gym price, still a good match
        return 0.8
    if max_b == 0:
        return 0.0
    # Penalty for being over budget
    return max(0.0, 1.0 - (gym_price - max_b) / max_b)


def calculate_facility_score(user_prefs: Dict[str, bool], gym_facilities: List[str]) -> float:
    """Overlap between user preferences and gym features [0, 1]"""
    pref_map = {
        "access_24h": "24h",
        "requires_classes": "classes",
        "requires_shower_lockers": "showers",
        "female_friendly": "female-friendly",
    }

    requested = [pref_map[k] for k, v in user_prefs.items() if v and k in pref_map]
    if not requested:
        return 1.0

    matches = []
    for facility in requested:
        if facility == "showers":
            if {"showers", "lockers"} & set(gym_facilities):
                matches.append(facility)
        elif facility in gym_facilities:
            matches.append(facility)
    return len(matches) / len(requested)


def calculate_rating_score(rating: float) -> float:
    """Normalize rating 0-5 to 0-1"""
    return rating / 5.0


def get_recommendations(user: UserProfile, gyms: List[Gym]) -> List[Recommendation]:
    recs = []

    W_DIST = 0.30
    W_BUDGET = 0.25
    W_FACILITY = 0.25
    W_RATING = 0.20

    user_prefs = {
        "access_24h": user.access_24h,
        "requires_classes": user.requires_classes,
        "requires_shower_lockers": user.requires_shower_lockers,
        "female_friendly": user.female_friendly,
    }

    filtered_gyms = [gym for gym in gyms if gym_matches_hard_filters(user, gym)]

    for gym in filtered_gyms:
        distance_km = geodesic(user.preferred_location, gym.location).km

        d_score = calculate_distance_score(distance_km, user.max_travel_distance_km)
        b_score = calculate_budget_score(gym.price, user.budget_range)
        f_score = calculate_facility_score(user_prefs, gym.facilities)
        r_score = calculate_rating_score(gym.rating)

        final_score = (
            W_DIST * d_score +
            W_BUDGET * b_score +
            W_FACILITY * f_score +
            W_RATING * r_score
        )

        recs.append(Recommendation(
            gym_id=gym.gym_id,
            name=gym.name,
            distance_km=round(distance_km, 2),
            score=round(final_score, 2),
            explanation=ScoreExplanation(
                distance=round(d_score, 2),
                budget=round(b_score, 2),
                facilities=round(f_score, 2),
                rating=round(r_score, 2)
            )
        ))

    recs.sort(key=lambda x: x.score, reverse=True)
    return recs


def _generate_synthetic_gyms(user: UserProfile, existing_ids: set, count: int) -> List[Gym]:
    """Generate deterministic, nearby gyms so we can always return a minimum count."""
    if count <= 0:
        return []

    base_lat, base_lon = user.preferred_location
    min_budget, max_budget = user.budget_range
    if max_budget <= 0:
        max_budget = max(100.0, min_budget)

    gyms = []
    for idx in range(count):
        gym_id = f"synthetic_{user.user_id}_{idx}"
        if gym_id in existing_ids:
            continue

        offset = 0.003 * (idx + 1)
        lat = base_lat + offset * (1 if idx % 2 == 0 else -1)
        lon = base_lon + offset * (1 if (idx // 2) % 2 == 0 else -1)

        price = min_budget + ((idx * 17) % 50)
        price = min(price, max_budget + 40.0)

        facilities = ["showers"]
        if user.access_24h:
            facilities.append("24h")
        if user.requires_classes:
            facilities.append("classes")
        if user.female_friendly:
            facilities.append("female-friendly")

        gyms.append(Gym(
            gym_id=gym_id,
            name=f"Local Fitness Hub {idx + 1}",
            location=(round(lat, 6), round(lon, 6)),
            price=float(round(price, 2)),
            facilities=facilities,
            sports=[],
            equipment=[],
            rating=4.0,
            popularity_score=0.6,
            tags=["synthetic", "nearby"],
        ))
        existing_ids.add(gym_id)
    return gyms


def ensure_minimum_gyms(user: UserProfile, gyms: List[Gym], min_results: int = MIN_RESULTS) -> List[Gym]:
    """Guarantee a minimum number of gyms by appending mock and synthetic entries."""
    if len(gyms) >= min_results:
        return gyms

    existing_ids = {gym.gym_id for gym in gyms}
    merged = list(gyms)

    for gym in MOCK_GYMS:
        if len(merged) >= min_results:
            break
        if gym.gym_id in existing_ids:
            continue
        merged.append(gym)
        existing_ids.add(gym.gym_id)

    remaining = min_results - len(merged)
    if remaining > 0:
        merged.extend(_generate_synthetic_gyms(user, existing_ids, remaining))

    return merged
