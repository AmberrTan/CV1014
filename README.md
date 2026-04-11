# CV1014

Gym recommendation project focused on a Textual TUI and an OpenStreetMap ingestion pipeline.

## Run

```bash
uv sync
uv run gym-recommender-tui
```

## Data Import (OpenStreetMap)

    uv run python scripts/fetch_gyms.py --limit 100

Use `--output` to write elsewhere:

    uv run python scripts/fetch_gyms.py --limit 100 --output data/gyms_osm_sg.json

The script imports gyms and enriches them with OpenStreetMap metadata, overwriting
`data/gyms.json` by default.

## Tests

```bash
uv run pytest -q
```

## Notes

- The repository is focused on TUI workflows.
- The default dataset lives at `data/gyms.json`.
