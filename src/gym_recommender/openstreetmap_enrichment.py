"""OpenStreetMap enrichment helpers for gym records."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from urllib import error, parse, request

from gym_recommender.data import DEFAULT_DATABASE_PATH, load_database
from gym_recommender.models import GymRecord, OpenStreetMapData

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_COUNTRY_HINT = "Singapore"
DEFAULT_USER_AGENT = "CV1014-GymRecommendationSystem/1.0 (+https://openstreetmap.org)"


@dataclass
class OpenStreetMapEnrichmentResult:
    """Result message for a single OSM enrichment attempt."""

    gym_id: int
    matched: bool
    message: str


def build_osm_search_query(gym: GymRecord, country_hint: str = DEFAULT_COUNTRY_HINT) -> str:
    """Build a search string for the OSM Nominatim API."""
    query_parts = [gym["gym_name"]]
    if gym.get("address"):
        query_parts.append(gym["address"])
    if gym.get("area"):
        query_parts.append(gym["area"])
    if country_hint:
        query_parts.append(country_hint)
    return ", ".join(part.strip() for part in query_parts if part and part.strip())


def build_osm_search_queries(gym: GymRecord, country_hint: str = DEFAULT_COUNTRY_HINT) -> list[str]:
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


def _read_json(url: str, *, user_agent: str) -> list[dict[str, Any]]:
    """Fetch a JSON payload from Nominatim."""
    http_request = request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": user_agent,
        },
        method="GET",
    )
    try:
        with request.urlopen(http_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:  # pragma: no cover - depends on live API responses
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Nominatim request failed with {exc.code}: {details}") from exc
    except error.URLError as exc:  # pragma: no cover - depends on network availability
        raise RuntimeError(f"Nominatim request failed: {exc.reason}") from exc


def search_place(
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

    url = f"{NOMINATIM_SEARCH_URL}?{parse.urlencode(params)}"
    results = _read_json(url, user_agent=user_agent)
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


def merge_openstreetmap_data(gym: GymRecord, openstreetmap_payload: OpenStreetMapData) -> GymRecord:
    """Return a gym record with OpenStreetMap enrichment attached."""
    merged = dict(gym)
    merged["openstreetmap"] = openstreetmap_payload
    return cast(GymRecord, merged)


def enrich_database(
    *,
    input_path: Path = DEFAULT_DATABASE_PATH,
    output_path: Path | None = None,
    country_hint: str = DEFAULT_COUNTRY_HINT,
    refresh_existing: bool = False,
    max_records: int | None = None,
    throttle_seconds: float = 1.1,
    user_agent: str = DEFAULT_USER_AGENT,
    email: str | None = None,
) -> tuple[list[GymRecord], list[OpenStreetMapEnrichmentResult]]:
    """Enrich the database with OpenStreetMap metadata."""
    gyms = load_database(input_path)
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
            match = search_place(query, user_agent=user_agent, email=email)
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

        updated_gyms.append(merge_openstreetmap_data(gym, build_openstreetmap_payload(match)))
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

    destination = output_path or input_path
    destination.write_text(f"{json.dumps(updated_gyms, indent=2)}\n", encoding="utf-8")
    return updated_gyms, results
