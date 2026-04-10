# TUI-Only Demo Tightening Design

## Summary
Tighten the codebase so it contains only the Textual TUI runtime and the OpenStreetMap ingestion pipeline used to overwrite `data/gyms.json`. Remove any remaining code, tests, and docs that are not required for the TUI demo or the ingestion flow. Keep Nominatim enrichment so imported gyms include `openstreetmap` metadata.

## Goals
- Keep only TUI runtime code needed to load/search/compare gyms from `data/gyms.json`.
- Keep only the OSM ingestion pipeline (Overpass + Nominatim) that writes to `data/gyms.json` by default.
- Remove non-demo artifacts, unused modules, and tests unrelated to TUI or OSM import/enrichment.
- Ensure README reflects the simplified demo workflow.

## Non-Goals
- No new features for the TUI.
- No new data sources beyond OSM + Nominatim.
- No change to the gym schema beyond removing unused fields or modules.

## Scope
- **Keep:** `src/gym_recommender/{tui.py,data.py,search.py,models.py,config.py,osm_import.py,openstreetmap_enrichment.py}`.
- **Keep:** `scripts/import_osm_gyms.py` as the only ingestion entry point.
- **Keep:** `data/gyms.json` as the sole dataset consumed by the TUI.
- **Keep:** tests covering TUI wiring and OSM import/enrichment behavior.
- **Remove:** docs/plans not needed for demo, any unused modules or files, and tests unrelated to TUI or OSM import.

## Ingestion Simplification
- `scripts/import_osm_gyms.py` defaults to writing `data/gyms.json`.
- `--output` remains optional for explicit override, but demo instructions focus on the default path.
- Pipeline stays: Overpass fetch → Nominatim enrichment → write JSON.

## Documentation
- README updated to highlight the TUI demo flow and the single ingestion command that overwrites `data/gyms.json`.

## Testing
- Run the existing TUI tests.
- Run OSM import/enrichment tests (unit-level; no live API calls).

