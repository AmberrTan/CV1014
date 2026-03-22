from __future__ import annotations

import argparse
import os
from pathlib import Path

from gym_recommender.config import load_dotenv
from gym_recommender.osm_import import OVERPASS_API_URL, import_osm_gyms
from gym_recommender.openstreetmap_enrichment import DEFAULT_USER_AGENT


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Import a larger OpenStreetMap gym dataset into the app's JSON format."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of gyms to import.",
    )
    parser.add_argument(
        "--country-code",
        default="SG",
        help="ISO 3166-1 country code used in the Overpass area query.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/gyms_osm_sg.json"),
        help="Output JSON file for the imported gyms.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("OVERPASS_API_URL", OVERPASS_API_URL),
        help="Overpass interpreter endpoint.",
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
        "--user-agent",
        default=os.environ.get("NOMINATIM_USER_AGENT", DEFAULT_USER_AGENT),
        help="User-Agent used for reverse geocoding requests.",
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("NOMINATIM_EMAIL"),
        help="Optional contact email passed to Nominatim reverse geocoding.",
    )
    parser.add_argument(
        "--reverse-throttle-seconds",
        type=float,
        default=float(os.environ.get("OSM_THROTTLE_SECONDS", "1.1")),
        help="Delay between reverse geocoding requests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    imported = import_osm_gyms(
        limit=args.limit,
        country_code=args.country_code,
        api_url=args.api_url,
        resolve_areas=args.resolve_areas,
        reverse_geocode_throttle_seconds=args.reverse_throttle_seconds,
        user_agent=args.user_agent,
        email=args.email,
        output_path=args.output,
    )
    print(f"Wrote {len(imported)} gyms to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
