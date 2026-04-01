"""Google Maps enrichment helpers for gym records."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from gym_recommender.data import DEFAULT_DATABASE_PATH, load_database
from gym_recommender.models import GymRecord

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACE_DETAILS_URL_TEMPLATE = "https://places.googleapis.com/v1/places/{place_id}"
TEXT_SEARCH_FIELDS = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.location",
        "places.types",
        "places.googleMapsUri",
        "places.businessStatus",
        "places.primaryType",
    ]
)
PLACE_DETAILS_FIELDS = ",".join(
    [
        "id",
        "displayName",
        "formattedAddress",
        "location",
        "googleMapsUri",
        "websiteUri",
        "internationalPhoneNumber",
        "regularOpeningHours.weekdayDescriptions",
        "regularOpeningHours.openNow",
        "rating",
        "userRatingCount",
        "businessStatus",
        "primaryType",
        "types",
    ]
)


@dataclass
class EnrichmentResult:
    """Result message for a single Google Maps enrichment attempt."""

    gym_id: int
    matched: bool
    message: str


def build_text_search_query(gym: GymRecord, country_hint: str = "Singapore") -> str:
    """Build a Google Places text search query."""
    query_parts = [gym["gym_name"]]
    if gym.get("address"):
        query_parts.append(gym["address"])
    if gym.get("area"):
        query_parts.append(gym["area"])
    if country_hint:
        query_parts.append(country_hint)
    return ", ".join(part.strip() for part in query_parts if part and part.strip())


def _post_json(url: str, payload: dict[str, Any], *, api_key: str, field_mask: str) -> dict[str, Any]:
    """Send a JSON POST request to the Google Places API."""
    encoded_payload = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask,
        },
        method="POST",
    )
    return _read_json(http_request)


def _get_json(url: str, *, api_key: str, field_mask: str) -> dict[str, Any]:
    """Send a JSON GET request to the Google Places API."""
    http_request = request.Request(
        url,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask,
        },
        method="GET",
    )
    return _read_json(http_request)


def _read_json(http_request: request.Request) -> dict[str, Any]:
    """Parse a JSON response from Google APIs."""
    try:
        with request.urlopen(http_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:  # pragma: no cover - depends on live API responses
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google Maps API request failed with {exc.code}: {details}") from exc
    except error.URLError as exc:  # pragma: no cover - depends on network availability
        raise RuntimeError(f"Google Maps API request failed: {exc.reason}") from exc


def search_place(query: str, *, api_key: str) -> dict[str, Any] | None:
    """Search for a place using the Google Places text search endpoint."""
    payload = {
        "textQuery": query,
        "pageSize": 1,
    }
    response = _post_json(TEXT_SEARCH_URL, payload, api_key=api_key, field_mask=TEXT_SEARCH_FIELDS)
    places = response.get("places", [])
    if not places:
        return None
    return places[0]


def fetch_place_details(place_id: str, *, api_key: str) -> dict[str, Any]:
    """Fetch detailed place metadata for a given place ID."""
    encoded_place_id = parse.quote(place_id, safe="")
    return _get_json(
        PLACE_DETAILS_URL_TEMPLATE.format(place_id=encoded_place_id),
        api_key=api_key,
        field_mask=PLACE_DETAILS_FIELDS,
    )


def build_google_maps_payload(search_match: dict[str, Any], details: dict[str, Any]) -> dict[str, Any]:
    """Normalize Google Places responses into the project's schema."""
    chosen_name = details.get("displayName", {}).get("text") or search_match.get("displayName", {}).get("text")
    chosen_address = details.get("formattedAddress") or search_match.get("formattedAddress")
    chosen_location = details.get("location") or search_match.get("location") or {}
    chosen_types = details.get("types") or search_match.get("types") or []

    return {
        "place_id": details.get("id") or search_match.get("id"),
        "display_name": chosen_name,
        "formatted_address": chosen_address,
        "location": {
            "latitude": chosen_location.get("latitude"),
            "longitude": chosen_location.get("longitude"),
        },
        "google_maps_uri": details.get("googleMapsUri") or search_match.get("googleMapsUri"),
        "website_uri": details.get("websiteUri"),
        "international_phone_number": details.get("internationalPhoneNumber"),
        "business_status": details.get("businessStatus") or search_match.get("businessStatus"),
        "primary_type": details.get("primaryType") or search_match.get("primaryType"),
        "types": chosen_types,
        "rating": details.get("rating"),
        "user_rating_count": details.get("userRatingCount"),
        "open_now": details.get("regularOpeningHours", {}).get("openNow"),
        "weekday_descriptions": details.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def merge_google_maps_data(gym: GymRecord, google_maps_payload: dict[str, Any]) -> GymRecord:
    """Return a gym record with Google Maps enrichment attached."""
    merged = dict(gym)
    merged["google_maps"] = google_maps_payload
    return merged


def enrich_database(
    *,
    api_key: str,
    input_path: Path = DEFAULT_DATABASE_PATH,
    output_path: Path | None = None,
    country_hint: str = "Singapore",
    refresh_existing: bool = False,
    max_records: int | None = None,
    throttle_seconds: float = 0.2,
) -> tuple[list[GymRecord], list[EnrichmentResult]]:
    """Enrich the database with Google Maps metadata."""
    gyms = load_database(input_path)
    updated_gyms: list[GymRecord] = []
    results: list[EnrichmentResult] = []
    processed = 0

    for gym in gyms:
        if max_records is not None and processed >= max_records:
            updated_gyms.append(dict(gym))
            results.append(
                EnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message="Skipped because max record limit was reached.",
                )
            )
            continue

        if gym.get("google_maps") and not refresh_existing:
            updated_gyms.append(dict(gym))
            results.append(
                EnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message="Skipped because Google Maps data already exists.",
                )
            )
            continue

        query = build_text_search_query(gym, country_hint=country_hint)
        match = search_place(query, api_key=api_key)
        processed += 1

        if not match or not match.get("id"):
            updated_gyms.append(dict(gym))
            results.append(
                EnrichmentResult(
                    gym_id=gym["gym_id"],
                    matched=False,
                    message=f"No Google Maps match found for query: {query}",
                )
            )
            if throttle_seconds > 0:
                time.sleep(throttle_seconds)
            continue

        details = fetch_place_details(match["id"], api_key=api_key)
        google_maps_payload = build_google_maps_payload(match, details)
        updated_gyms.append(merge_google_maps_data(gym, google_maps_payload))
        results.append(
            EnrichmentResult(
                gym_id=gym["gym_id"],
                matched=True,
                message=f"Matched Google place ID {google_maps_payload['place_id']}",
            )
        )

        if throttle_seconds > 0:
            time.sleep(throttle_seconds)

    destination = output_path or input_path
    destination.write_text(f"{json.dumps(updated_gyms, indent=2)}\n", encoding="utf-8")
    return updated_gyms, results
