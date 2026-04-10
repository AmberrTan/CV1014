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

## Notes

- The repository is focused on TUI workflows.
- The default dataset lives at `data/gyms.json`.
