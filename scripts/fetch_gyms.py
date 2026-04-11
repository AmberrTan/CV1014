"""Fetch gyms from OpenStreetMap and enrich them in one run."""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import requests

from gym_recommender.data import DEFAULT_DATABASE_PATH, save_database
from gym_recommender.models import GymRecord, OpenStreetMapData

OVERPASS_API_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
DEFAULT_COUNTRY_HINT = "Singapore"
DEFAULT_USER_AGENT = "CV1014-GymRecommendationSystem/1.0 (+https://openstreetmap.org)"
SINGAPORE_BOUNDS = {
    "min_lat": 1.20,
    "max_lat": 1.48,
    "min_lon": 103.60,
    "max_lon": 104.05,
}
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


@dataclass
class OpenStreetMapEnrichmentResult:
    """Result message for a single OSM enrichment attempt."""

    gym_id: int
    matched: bool
    message: str


def get_session(user_agent: str) -> requests.Session:
    """Return a configured requests session."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
    )
    return session


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: dict[str, str] | None = None,
    data: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30,
    retries: int = 3,
    backoff_seconds: float = 1.0,
    extra_backoff_seconds: float = 0.0,
) -> Any:
    """Send an HTTP request and decode the JSON payload with retries."""
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.request(
                method,
                url,
                params=params,
                data=data,
                headers=headers,
                timeout=timeout,
            )
            if response.status_code in RETRY_STATUS_CODES and attempt < retries - 1:
                time.sleep(backoff_seconds * (2**attempt) + extra_backoff_seconds)
                continue
            if response.status_code >= 400:
                raise RuntimeError(
                    f"Request failed with {response.status_code}: {response.text}"
                )
            try:
                return response.json()
            except ValueError as exc:  # pragma: no cover - defensive
                raise RuntimeError(
                    f"Failed to decode JSON response from {url}: {response.text}"
                ) from exc
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(backoff_seconds * (2**attempt) + extra_backoff_seconds)
                continue
            raise RuntimeError(f"Request failed: {exc}") from exc

    raise RuntimeError(f"Request failed after retries: {last_error}") from last_error


def build_overpass_query(*, country_code: str = "SG") -> str:
    """Build the Overpass QL query for gym amenities."""
    return f"""
[out:json][timeout:120];
area[\"ISO3166-1\"=\"{country_code}\"][admin_level=2]->.searchArea;
(
  nwr[\"amenity\"=\"gym\"](area.searchArea);
  nwr[\"leisure\"=\"fitness_centre\"](area.searchArea);
);
out center tags;
""".strip()


def fetch_overpass_elements(
    session: requests.Session,
    *,
    country_code: str = "SG",
    api_url: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch raw elements from Overpass using the configured query with retries and mirrors."""
    query = build_overpass_query(country_code=country_code)
    urls = [api_url] if api_url else []
    for mirror in OVERPASS_API_URLS:
        if mirror not in urls:
            urls.append(mirror)

    last_exc: Exception | None = None
    for url in urls:
        try:
            payload = request_json(
                session,
                "POST",
                url,
                data={"data": query},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=180,
                retries=3,
                backoff_seconds=1.0,
            )
            return payload.get("elements", [])
        except RuntimeError as exc:
            last_exc = exc
            continue

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
    session: requests.Session,
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

    payload = request_json(
        session,
        "GET",
        NOMINATIM_REVERSE_URL,
        params=params,
        timeout=30,
        retries=3,
        backoff_seconds=1.0,
        extra_backoff_seconds=1.0,
    )

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
    session: requests.Session,
    *,
    limit: int = 100,
    country_code: str = "SG",
    api_url: str | None = None,
    resolve_areas: bool = True,
    reverse_geocode_throttle_seconds: float = 1.1,
    user_agent: str = DEFAULT_USER_AGENT,
    email: str | None = None,
) -> list[GymRecord]:
    """Import and normalize gyms from OpenStreetMap."""
    elements = fetch_overpass_elements(
        session, country_code=country_code, api_url=api_url
    )
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
                        session, lat, lon, user_agent=user_agent, email=email
                    )
                    reverse_cache[cache_key] = area_name or gym["area"]
                    time.sleep(reverse_geocode_throttle_seconds)
                if area_name:
                    gym["area"] = area_name

        normalized.append(gym)

    return normalized


def build_osm_search_query(
    gym: GymRecord, country_hint: str = DEFAULT_COUNTRY_HINT
) -> str:
    """Build a search string for the OSM Nominatim API."""
    query_parts = [gym["gym_name"]]
    if gym.get("address"):
        query_parts.append(gym["address"])
    if gym.get("area"):
        query_parts.append(gym["area"])
    if country_hint:
        query_parts.append(country_hint)
    return ", ".join(part.strip() for part in query_parts if part and part.strip())


def build_osm_search_queries(
    gym: GymRecord, country_hint: str = DEFAULT_COUNTRY_HINT
) -> list[str]:
    """Return de-duplicated query variants for better matching."""
    query_variants = [
        [gym["gym_name"], gym.get("address"), gym.get("area"), country_hint],
        [gym["gym_name"], gym.get("area"), country_hint],
        [gym["gym_name"], country_hint],
        [gym["gym_name"]],
    ]
    queries: list[str] = []
    seen: set[str] = set()

    for parts in query_variants:
        query = ", ".join(part.strip() for part in parts if part and part.strip())
        if query and query not in seen:
            queries.append(query)
            seen.add(query)
    return queries


def search_place(
    session: requests.Session,
    query: str,
    *,
    user_agent: str,
    email: str | None = None,
    limit: int = 1,
) -> dict[str, Any] | None:
    """Search for a single OSM place using Nominatim."""
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": str(limit),
        "addressdetails": "1",
        "namedetails": "1",
        "extratags": "1",
    }
    if email:
        params["email"] = email

    results = request_json(
        session,
        "GET",
        NOMINATIM_SEARCH_URL,
        params=params,
        timeout=30,
        retries=3,
        backoff_seconds=1.0,
        extra_backoff_seconds=1.0,
    )
    if not results:
        return None
    return results[0]


def build_openstreetmap_payload(match: dict[str, Any]) -> OpenStreetMapData:
    """Normalize an OSM match into the project's enrichment schema."""
    extratags = match.get("extratags", {})
    return {
        "osm_type": match.get("osm_type"),
        "osm_id": match.get("osm_id"),
        "place_id": match.get("place_id"),
        "display_name": match.get("display_name"),
        "name": match.get("name"),
        "latitude": float(match["lat"]) if match.get("lat") is not None else None,
        "longitude": float(match["lon"]) if match.get("lon") is not None else None,
        "category": match.get("category"),
        "type": match.get("type"),
        "importance": match.get("importance"),
        "place_rank": match.get("place_rank"),
        "address": match.get("address", {}),
        "namedetails": match.get("namedetails", {}),
        "extratags": extratags,
        "website": extratags.get("website"),
        "opening_hours": extratags.get("opening_hours"),
        "phone": extratags.get("phone") or extratags.get("contact:phone"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def merge_openstreetmap_data(
    gym: GymRecord, openstreetmap_payload: OpenStreetMapData
) -> GymRecord:
    """Return a gym record with OpenStreetMap enrichment attached."""
    merged = dict(gym)
    merged["openstreetmap"] = openstreetmap_payload
    return cast(GymRecord, merged)


def enrich_gyms(
    session: requests.Session,
    gyms: list[GymRecord],
    *,
    country_hint: str = DEFAULT_COUNTRY_HINT,
    refresh_existing: bool = False,
    max_records: int | None = None,
    throttle_seconds: float = 1.1,
    user_agent: str = DEFAULT_USER_AGENT,
    email: str | None = None,
) -> tuple[list[GymRecord], list[OpenStreetMapEnrichmentResult]]:
    """Enrich the database with OpenStreetMap metadata."""
    updated_gyms: list[GymRecord] = []
    results: list[OpenStreetMapEnrichmentResult] = []
    processed = 0

    for gym in gyms:
        if max_records is not None and processed >= max_records:
            updated_gyms.append(cast(GymRecord, dict(gym)))
            results.append(
                OpenStreetMapEnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message="Skipped because max record limit was reached.",
                )
            )
            continue

        if gym.get("openstreetmap") and not refresh_existing:
            updated_gyms.append(cast(GymRecord, dict(gym)))
            results.append(
                OpenStreetMapEnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message="Skipped because OpenStreetMap data already exists.",
                )
            )
            continue

        queries = build_osm_search_queries(gym, country_hint=country_hint)
        processed += 1
        match: dict[str, Any] | None = None
        matched_query: str | None = None

        for query in queries:
            match = search_place(session, query, user_agent=user_agent, email=email)
            if match:
                matched_query = query
                break
            time.sleep(throttle_seconds)

        if not match:
            updated_gyms.append(cast(GymRecord, dict(gym)))
            results.append(
                OpenStreetMapEnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message=f"No OpenStreetMap match found for queries: {queries}",
                )
            )
            continue

        updated_gyms.append(
            merge_openstreetmap_data(gym, build_openstreetmap_payload(match))
        )
        results.append(
            OpenStreetMapEnrichmentResult(
                gym_id=gym["gym_id"],
                matched=True,
                message=(
                    f"Matched OSM {match.get('osm_type')} {match.get('osm_id')} using query: "
                    f"{matched_query}"
                ),
            )
        )
        time.sleep(throttle_seconds)

    return updated_gyms, results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch gyms from OpenStreetMap and enrich them in one run."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of gyms to import from Overpass.",
    )
    parser.add_argument(
        "--country-code",
        default="SG",
        help="ISO 3166-1 country code used in the Overpass area query.",
    )
    parser.add_argument(
        "--country-hint",
        default=DEFAULT_COUNTRY_HINT,
        help="Country hint used for Nominatim search queries.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("OVERPASS_API_URL"),
        help="Overpass interpreter endpoint (defaults to trying multiple mirrors if not specified).",
    )
    parser.add_argument(
        "--resolve-areas",
        action="store_true",
        default=True,
        help="Reverse geocode coordinates to populate better area names.",
    )
    parser.add_argument(
        "--no-resolve-areas",
        action="store_false",
        dest="resolve_areas",
        help="Skip reverse geocoding and keep area names inferred only from OSM tags.",
    )
    parser.add_argument(
        "--reverse-geocode-throttle",
        type=float,
        default=float(os.environ.get("OSM_THROTTLE_SECONDS", "1.1")),
        help="Delay between reverse geocoding requests.",
    )
    parser.add_argument(
        "--refresh-existing",
        action="store_true",
        help="Re-enrich gyms even if OpenStreetMap data already exists.",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Limit the number of records enriched (useful for smoke tests).",
    )
    parser.add_argument(
        "--throttle",
        type=float,
        default=float(os.environ.get("OSM_THROTTLE_SECONDS", "1.1")),
        help="Delay between Nominatim search requests.",
    )
    parser.add_argument(
        "--user-agent",
        default=os.environ.get("NOMINATIM_USER_AGENT", DEFAULT_USER_AGENT),
        help="User-Agent used for Nominatim requests.",
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("NOMINATIM_EMAIL"),
        help="Optional contact email passed to Nominatim.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help="Output JSON file for the final dataset (defaults to data/gyms.json).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = get_session(args.user_agent)

    gyms = import_osm_gyms(
        session,
        limit=args.limit,
        country_code=args.country_code,
        api_url=args.api_url,
        resolve_areas=args.resolve_areas,
        reverse_geocode_throttle_seconds=args.reverse_geocode_throttle,
        user_agent=args.user_agent,
        email=args.email,
    )

    enriched, results = enrich_gyms(
        session,
        gyms,
        country_hint=args.country_hint,
        refresh_existing=args.refresh_existing,
        max_records=args.max_records,
        throttle_seconds=args.throttle,
        user_agent=args.user_agent,
        email=args.email,
    )

    save_database(enriched, args.output)

    matched = sum(1 for result in results if result.matched)
    print(
        f"Wrote {len(enriched)} gyms to {args.output} ({matched} matched with OpenStreetMap)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
