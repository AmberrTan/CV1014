# Fetch Gyms Unified Script Design

Date: 2026-04-11

## Summary
Create a single CLI script, `scripts/fetch_gyms.py`, that performs both OpenStreetMap import and enrichment in one run, replacing the two existing scripts. The script will use `requests` with a small in-script helper for sessions and JSON requests, keep current retry/backoff behavior, and overwrite the database file by default. Documentation will be updated to reflect the new entry point and behavior.

## Goals
- One CLI entry point that runs import + enrichment in sequence.
- Cleaner HTTP code using `requests` with centralized configuration.
- Preserve current normalization and enrichment logic.
- Default behavior overwrites the existing database file.
- Update relevant docs to reflect the new CLI and behavior.

## Non-Goals
- Adding async support.
- Changing data model or schema.
- Changing business logic heuristics.
- Introducing new tests beyond a simple smoke run.

## Proposed Approach
### Option Selected
Use a single script (`scripts/fetch_gyms.py`) that embeds a minimal `requests` helper. This keeps the demo footprint small and avoids creating additional modules.

### Script Structure
- CLI arguments (argparse):
  - Import parameters: `--limit`, `--country-code`, `--api-url`, `--resolve-areas`, `--reverse-geocode-throttle`
  - Enrichment parameters: `--refresh-existing`, `--max-records`, `--throttle`
  - Shared parameters: `--user-agent`, `--email`, `--output`
- Execution flow:
  1. Fetch Overpass elements and normalize gyms.
  2. Reverse geocode areas when enabled (with cache + throttle).
  3. Enrich each gym via Nominatim search.
  4. Write final list to output path (default overwrite).

### HTTP Helper (in-script)
- `get_session(user_agent: str) -> requests.Session`
  - Configure `User-Agent`, `Accept`, retry adapter (429/5xx), and timeouts.
- `request_json(...) -> dict | list`
  - Build GET/POST, handle errors, parse JSON.

## Data Flow
- Overpass -> elements -> normalization -> gym list
- Optional reverse geocode -> `area`
- Nominatim search -> OpenStreetMap payload -> merged gyms
- Output JSON written to target path

## Error Handling
- Keep current retry and backoff semantics for 429 and 5xx.
- Preserve mirror fallback for Overpass.
- Raise `RuntimeError` with useful details when retries are exhausted.

## Documentation Updates
- Update any existing README or script docs to point to `scripts/fetch_gyms.py`.
- Note that the script overwrites the database by default unless `--output` is provided.
- Remove or deprecate references to the old scripts.

## Testing
- Optional manual smoke run: low limit (e.g., `--limit 3`) and verify output JSON shape.

## Rollout / Migration
- Remove or archive old scripts after the new script is in place.
- Update any internal references or instructions.

## Open Questions
- None (per current requirements).
