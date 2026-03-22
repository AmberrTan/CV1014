from __future__ import annotations

import argparse
import os
from pathlib import Path

from env_utils import load_dotenv
from gym_recommender.data import DEFAULT_DATABASE_PATH
from gym_recommender.google_maps_enrichment import enrich_database


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Fetch extra Google Maps place data for the gyms JSON database."
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
        default="Singapore",
        help="Extra location text added to each search query.",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("GOOGLE_MAPS_API_KEY"),
        help="Google Maps API key. Defaults to GOOGLE_MAPS_API_KEY.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh entries that already contain a google_maps block.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only process the first N gyms.",
    )
    parser.add_argument(
        "--throttle-seconds",
        type=float,
        default=0.2,
        help="Delay between API calls to keep request bursts modest.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.api_key:
        raise SystemExit("Missing API key. Pass --api-key or set GOOGLE_MAPS_API_KEY.")

    _, results = enrich_database(
        api_key=args.api_key,
        input_path=args.input,
        output_path=args.output,
        country_hint=args.country_hint,
        refresh_existing=args.refresh,
        max_records=args.limit,
        throttle_seconds=args.throttle_seconds,
    )

    matched_count = sum(1 for result in results if result.matched)
    print(f"Processed {len(results)} gyms. Matched {matched_count}.")
    for result in results:
        status = "MATCHED" if result.matched else "SKIPPED"
        print(f"[{status}] gym_id={result.gym_id} {result.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
