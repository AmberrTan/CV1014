from __future__ import annotations

import argparse
import os
from pathlib import Path

from gym_recommender.config import load_dotenv
from gym_recommender.data import DEFAULT_DATABASE_PATH
from gym_recommender.openstreetmap_enrichment import (
    DEFAULT_COUNTRY_HINT,
    DEFAULT_USER_AGENT,
    enrich_database,
)


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Fetch extra OpenStreetMap place data for the gyms JSON database."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
        help="Path to the source gym JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write the enriched JSON file. Defaults to overwriting the input file.",
    )
    parser.add_argument(
        "--country-hint",
        default=os.environ.get("OSM_COUNTRY_HINT", DEFAULT_COUNTRY_HINT),
        help="Extra location text added to each search query.",
    )
    parser.add_argument(
        "--user-agent",
        default=os.environ.get("NOMINATIM_USER_AGENT", DEFAULT_USER_AGENT),
        help="Required User-Agent for Nominatim requests.",
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("NOMINATIM_EMAIL"),
        help="Optional contact email passed to Nominatim.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh entries that already contain an openstreetmap block.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only process the first N gyms.",
    )
    parser.add_argument(
        "--throttle-seconds",
        type=float,
        default=float(os.environ.get("OSM_THROTTLE_SECONDS", "1.1")),
        help="Delay between requests. Keep this at or above 1 second for the public Nominatim instance.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.user_agent:
        raise SystemExit("Missing User-Agent. Pass --user-agent or set NOMINATIM_USER_AGENT.")

    _, results = enrich_database(
        input_path=args.input,
        output_path=args.output,
        country_hint=args.country_hint,
        refresh_existing=args.refresh,
        max_records=args.limit,
        throttle_seconds=args.throttle_seconds,
        user_agent=args.user_agent,
        email=args.email,
    )

    matched_count = sum(1 for result in results if result.matched)
    print(f"Processed {len(results)} gyms. Matched {matched_count}.")
    for result in results:
        status = "MATCHED" if result.matched else "SKIPPED"
        print(f"[{status}] gym_id={result.gym_id} {result.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
