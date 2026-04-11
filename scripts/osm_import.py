"""Import gyms from OpenStreetMap via the Overpass API."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, cast
from urllib import error, parse, request

from gym_recommender.models import GymRecord
from gym_recommender.openstreetmap_enrichment import (
    DEFAULT_USER_AGENT,
    build_openstreetmap_payload,
)

OVERPASS_API_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
OVERPASS_API_URL = OVERPASS_API_URLS[0]
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
SINGAPORE_BOUNDS = {
    "min_lat": 1.20,
    "max_lat": 1.48,
    "min_lon": 103.60,
    "max_lon": 104.05,
}


def build_overpass_query(*, country_code: str = "SG") -> str:
    """Build the Overpass QL query for gym amenities."""
    return f"""
[out:json][timeout:120];
area["ISO3166-1"="{country_code}"][admin_level=2]->.searchArea;
(
  nwr["amenity"="gym"](area.searchArea);
  nwr["leisure"="fitness_centre"](area.searchArea);
);
out center tags;
""".strip()


def fetch_overpass_elements(
    *, country_code: str = "SG", api_url: str | None = None
) -> list[dict[str, Any]]:
    """Fetch raw elements from Overpass using the configured query with retries and mirrors."""
    query = build_overpass_query(country_code=country_code)
    encoded = parse.urlencode({"data": query}).encode("utf-8")

    # If api_url is provided, try it first. Always include mirrors as fallback.
    urls = [api_url] if api_url else []
    for mirror in OVERPASS_API_URLS:
        if mirror not in urls:
            urls.append(mirror)

    last_exc: Exception | None = None
    for url in urls:
        for attempt in range(3):  # Retry up to 3 times per URL
            http_request = request.Request(
                url,
                data=encoded,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            try:
                with request.urlopen(http_request, timeout=180) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                    return payload.get("elements", [])
            except error.HTTPError as exc:
                last_exc = exc
                # Retry on 429 (Too Many Requests) or 5xx (Server Errors like 504)
                if exc.code == 429 or 500 <= exc.code <= 599:
                    time.sleep(2**attempt)
                    continue
                details = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"Overpass request failed with {exc.code}: {details}"
                ) from exc
            except (error.URLError, TimeoutError) as exc:
                last_exc = exc
                time.sleep(2**attempt)
                continue

    # All URLs and retries exhausted
    if isinstance(last_exc, error.HTTPError):
        details = last_exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"All Overpass mirrors failed. Last error {last_exc.code}: {details}"
        ) from last_exc
    raise RuntimeError(f"All Overpass mirrors failed: {last_exc}") from last_exc


def coordinate_to_grid(lat: float, lon: float) -> tuple[int, int]:
    """Normalize lat/lon to the 0-100 grid used by the app."""
    lat_span = SINGAPORE_BOUNDS["max_lat"] - SINGAPORE_BOUNDS["min_lat"]
    lon_span = SINGAPORE_BOUNDS["max_lon"] - SINGAPORE_BOUNDS["min_lon"]
    normalized_x = (lon - SINGAPORE_BOUNDS["min_lon"]) / lon_span
    normalized_y = (lat - SINGAPORE_BOUNDS["min_lat"]) / lat_span
    x_value = max(0, min(100, round(normalized_x * 100)))
    y_value = max(0, min(100, round(normalized_y * 100)))
    return x_value, y_value


def _get_lat_lon(element: dict[str, Any]) -> tuple[float, float] | None:
    """Extract lat/lon from Overpass element payloads."""
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center")
    if center and "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None


def _build_address(tags: dict[str, str]) -> str:
    """Construct a readable address string from OSM tags."""
    address_parts = [
        tags.get("addr:unit"),
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
        tags.get("addr:postcode"),
    ]
    address = ", ".join(part.strip() for part in address_parts if part and part.strip())
    return address or "Address missing"


def _build_area(tags: dict[str, str]) -> str:
    """Pick the most specific available area name from tags."""
    return (
        tags.get("addr:suburb")
        or tags.get("addr:city_district")
        or tags.get("addr:neighbourhood")
        or tags.get("addr:quarter")
        or tags.get("addr:city")
        or "Singapore"
    )


def reverse_geocode_area(
    lat: float,
    lon: float,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    email: str | None = None,
) -> str | None:
    """Reverse geocode a lat/lon into a neighborhood/area name."""
    params = {
        "lat": str(lat),
        "lon": str(lon),
        "format": "jsonv2",
        "addressdetails": "1",
        "zoom": "16",
    }
    if email:
        params["email"] = email

    url = f"{NOMINATIM_REVERSE_URL}?{parse.urlencode(params)}"
    http_request = request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
        method="GET",
    )
    try:
        payload: dict[str, Any] = {}
        for attempt in range(3):  # Retry up to 3 times
            try:
                with request.urlopen(http_request, timeout=30) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                    break
            except error.HTTPError as exc:
                if attempt < 2 and (exc.code == 429 or 500 <= exc.code <= 599):
                    time.sleep(2**attempt + 1)  # Extra second for Nominatim
                    continue
                details = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"Nominatim reverse request failed with {exc.code}: {details}"
                ) from exc
            except (error.URLError, TimeoutError) as exc:
                if attempt < 2:
                    time.sleep(2**attempt + 1)
                    continue
                raise RuntimeError(f"Nominatim reverse request failed: {exc}") from exc
    except Exception as exc:  # pragma: no cover - live API
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError(f"Nominatim reverse request failed: {exc}") from exc

    address = payload.get("address", {})
    return (
        address.get("suburb")
        or address.get("city_district")
        or address.get("town")
        or address.get("neighbourhood")
        or address.get("quarter")
        or address.get("city")
    )


def _infer_gym_type(name: str, tags: dict[str, str]) -> str:
    """Infer gym type using tags and name keywords."""
    haystack = " ".join(
        filter(
            None,
            [
                name.lower(),
                tags.get("sport", "").lower(),
                tags.get("brand", "").lower(),
                tags.get("operator", "").lower(),
            ],
        )
    )
    if "active" in haystack or "community" in haystack or tags.get("fee") == "no":
        return "public"
    if any(keyword in haystack for keyword in ["pilates", "yoga", "barre"]):
        return "boutique"
    if any(
        keyword in haystack
        for keyword in ["crossfit", "f45", "bft", "ufit", "orangetheory"]
    ):
        return "group training"
    if any(
        keyword in haystack
        for keyword in ["muay", "boxing", "mma", "taekwondo", "martial"]
    ):
        return "martial arts"
    if "women" in haystack or "ladies" in haystack:
        return "women-only"
    return "commercial"


def _infer_facilities(name: str, tags: dict[str, str], gym_type: str) -> list[str]:
    """Infer a facility list from tags and gym type."""
    haystack = f"{name.lower()} {tags.get('sport', '').lower()}"
    facilities = {"cardio", "free weights", "machine weights"}
    if tags.get("shower") == "yes":
        facilities.add("shower")
    if tags.get("toilets") == "yes":
        facilities.add("toilets")
    if tags.get("sauna") == "yes":
        facilities.add("sauna")
    if tags.get("wheelchair") == "yes":
        facilities.add("accessible")
    if gym_type in {"boutique", "group training", "martial arts", "women-only"}:
        facilities.add("group classes")
    if gym_type in {"commercial", "group training", "boutique"}:
        facilities.add("personal training")
    if any(keyword in haystack for keyword in ["pilates", "yoga", "barre"]):
        facilities.add("studio")
    if any(keyword in haystack for keyword in ["boxing", "muay", "taekwondo", "mma"]):
        facilities.add("combat training")
    return sorted(facilities)


def _infer_hours(name: str, tags: dict[str, str]) -> tuple[int, int, bool]:
    """Infer opening hours from tags or name hints."""
    opening_hours = (tags.get("opening_hours") or "").lower()
    lowered_name = name.lower()
    if "24/7" in opening_hours or "24 hours" in lowered_name or "24-hr" in lowered_name:
        return 0, 2400, True
    if opening_hours and "-" in opening_hours and ";" not in opening_hours:
        start_value, end_value = opening_hours.split("-", 1)
        start_time = _parse_hhmm(start_value)
        end_time = _parse_hhmm(end_value)
        if start_time is not None and end_time is not None and start_time < end_time:
            return start_time, end_time, False
    return 600, 2200, False


def _parse_hhmm(value: str) -> int | None:
    """Parse a HH:MM string into an integer HHMM."""
    clean = value.strip()
    if len(clean) != 5 or clean[2] != ":":
        return None
    hours = clean[:2]
    minutes = clean[3:]
    if not (hours.isdigit() and minutes.isdigit()):
        return None
    return int(hours) * 100 + int(minutes)


def _infer_prices(gym_type: str) -> tuple[float, float]:
    """Return default monthly and day-pass prices for a gym type."""
    defaults = {
        "public": (55.0, 2.5),
        "commercial": (120.0, 22.0),
        "boutique": (165.0, 30.0),
        "group training": (210.0, 38.0),
        "martial arts": (140.0, 25.0),
        "women-only": (95.0, 18.0),
    }
    return defaults.get(gym_type, (120.0, 22.0))


def _infer_rating(tags: dict[str, str]) -> float:
    """Infer a default rating based on available OSM metadata."""
    score = 4.0
    if tags.get("website") or tags.get("contact:website"):
        score += 0.1
    if tags.get("phone") or tags.get("contact:phone"):
        score += 0.1
    if tags.get("opening_hours"):
        score += 0.1
    if tags.get("brand") or tags.get("operator"):
        score += 0.1
    return round(min(score, 4.5), 1)


def _infer_beginner_friendly(name: str, gym_type: str, tags: dict[str, str]) -> bool:
    """Infer whether the gym is beginner friendly."""
    haystack = f"{name.lower()} {tags.get('sport', '').lower()}"
    if gym_type == "martial arts" or any(
        keyword in haystack for keyword in ["crossfit", "power", "bodybuilding"]
    ):
        return False
    return True


def _infer_classes_available(gym_type: str, tags: dict[str, str]) -> bool:
    """Infer whether classes are likely available."""
    sport = tags.get("sport", "").lower()
    return gym_type in {
        "boutique",
        "group training",
        "martial arts",
        "women-only",
    } or bool(sport)


def _infer_trainer_available(gym_type: str) -> bool:
    """Infer trainer availability based on gym type."""
    return gym_type in {
        "commercial",
        "boutique",
        "group training",
        "martial arts",
        "women-only",
    }


def _normalize_element(element: dict[str, Any], gym_id: int) -> GymRecord | None:
    """Convert a raw Overpass element into a GymRecord."""
    tags = element.get("tags", {})
    name = (tags.get("name") or "").strip()
    if not name:
        return None
    lat_lon = _get_lat_lon(element)
    if lat_lon is None:
        return None
    lat, lon = lat_lon
    gym_type = _infer_gym_type(name, tags)
    opening_time, closing_time, is_24_hours = _infer_hours(name, tags)
    monthly_price, day_pass_price = _infer_prices(gym_type)
    x_coordinate, y_coordinate = coordinate_to_grid(lat, lon)
    classes_available = _infer_classes_available(gym_type, tags)

    return cast(
        GymRecord,
        {
            "gym_id": gym_id,
            "gym_name": name,
            "area": _build_area(tags),
            "address": _build_address(tags),
            "x_coordinate": x_coordinate,
            "y_coordinate": y_coordinate,
            "monthly_price": monthly_price,
            "day_pass_price": day_pass_price,
            "rating": _infer_rating(tags),
            "opening_time": opening_time,
            "closing_time": closing_time,
            "is_24_hours": is_24_hours,
            "gym_type": gym_type,
            "facilities": _infer_facilities(name, tags, gym_type),
            "beginner_friendly": _infer_beginner_friendly(name, gym_type, tags),
            "female_friendly": gym_type == "women-only"
            or tags.get("female") in {"yes", "only"},
            "student_discount": gym_type == "public",
            "peak_crowd_level": "high"
            if gym_type in {"commercial", "group training"}
            else "medium",
            "parking_available": tags.get("parking") == "yes",
            "near_mrt": False,
            "trainer_available": _infer_trainer_available(gym_type),
            "classes_available": classes_available,
            "openstreetmap": build_openstreetmap_payload(
                {
                    "osm_type": element.get("type"),
                    "osm_id": element.get("id"),
                    "place_id": None,
                    "display_name": name,
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "category": tags.get("amenity") or tags.get("leisure"),
                    "type": tags.get("sport") or gym_type,
                    "importance": None,
                    "place_rank": None,
                    "address": {
                        key: value
                        for key, value in tags.items()
                        if key.startswith("addr:")
                    },
                    "namedetails": {"name": name},
                    "extratags": tags,
                }
            ),
        },
    )


def import_osm_gyms(
    *,
    limit: int = 100,
    country_code: str = "SG",
    api_url: str | None = None,
    resolve_areas: bool = True,
    reverse_geocode_throttle_seconds: float = 1.1,
    user_agent: str = DEFAULT_USER_AGENT,
    email: str | None = None,
    output_path: Path | None = None,
) -> list[GymRecord]:
    """Import and normalize gyms from OpenStreetMap."""
    elements = fetch_overpass_elements(country_code=country_code, api_url=api_url)
    normalized: list[GymRecord] = []
    seen: set[tuple[str, int, int]] = set()
    reverse_cache: dict[tuple[float, float], str] = {}

    for element in elements:
        if len(normalized) >= limit:
            break
        gym = _normalize_element(element, gym_id=len(normalized) + 1)
        if gym is None:
            continue
        dedupe_key = (
            gym["gym_name"].casefold(),
            gym["x_coordinate"],
            gym["y_coordinate"],
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        if resolve_areas:
            osm = gym.get("openstreetmap", {})
            lat = osm.get("latitude")
            lon = osm.get("longitude")
            if isinstance(lat, float) and isinstance(lon, float):
                cache_key = (round(lat, 5), round(lon, 5))
                area_name = reverse_cache.get(cache_key)
                if area_name is None:
                    area_name = reverse_geocode_area(
                        lat, lon, user_agent=user_agent, email=email
                    )
                    reverse_cache[cache_key] = area_name or gym["area"]
                    time.sleep(reverse_geocode_throttle_seconds)
                if area_name:
                    gym["area"] = area_name

        normalized.append(gym)

    if output_path is not None:
        output_path.write_text(
            f"{json.dumps(normalized, indent=2)}\n", encoding="utf-8"
        )
    return normalized
