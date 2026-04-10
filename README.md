# CV1014

Gym recommendation project focused on a Textual TUI and an OpenStreetMap ingestion pipeline.

## Run

```bash
uv sync
uv run gym-recommender-tui
```

## Data Import (OpenStreetMap)

```bash
uv run python scripts/import_osm_gyms.py --limit 100 --output data/gyms_osm_sg.json
```

To overwrite the default dataset used by the TUI:

```bash
uv run python scripts/import_osm_gyms.py --limit 100 --output data/gyms.json
```

### Optional Environment Variables

- `OVERPASS_API_URL`: Override the Overpass API endpoint.
- `NOMINATIM_USER_AGENT`: User-Agent required by Nominatim.
- `NOMINATIM_EMAIL`: Optional contact email for Nominatim requests.
- `OSM_THROTTLE_SECONDS`: Delay between reverse geocoding requests.

## Tests

```bash
uv run pytest -q
```

## Notes

- The repository is focused on TUI workflows.
- The default dataset lives at `data/gyms.json`.
