# Gym Recommendation System

Gym Recommendation System is a Python 3.12 project for browsing, searching, sorting, comparing, recommending, and updating gym records from an offline JSON database. The core assignment-safe deliverable remains a Python console application, and the project also includes a FastAPI backend plus an optional Next.js showcase UI for presentation.

## Project Structure

- `data/gyms.json`
  Offline gym database shared by the console app and API.
- `src/gym_recommender/main.py`
  Console application entrypoint.
- `src/gym_recommender/ui.py`
  Console menus and interactive workflows.
- `src/gym_recommender/search.py`
  Search, filtering, sorting, and distance utilities.
- `src/gym_recommender/recommendation.py`
  Recommendation scoring and ranking logic.
- `src/gym_recommender/services.py`
  Shared service layer used by the API.
- `src/gym_recommender/api.py`
  FastAPI application for web access.
- `web/`
  Optional Next.js App Router frontend.
- `tests/test_app.py`
  Unit tests for core logic and API coverage where dependencies are available.

## Core Features

- View all gyms in the local database
- Search by area, budget, rating, facilities, operating time, gym type, and more
- Sort by price, rating, distance, or recommendation score
- Generate personalized top gym recommendations from user preferences
- Compare 2-3 gyms side by side
- Add new gym records and update existing ones
- Serve the same data and logic through a JSON API
- Showcase the system in a web UI built with Next.js

## Tech Stack

- Python 3.12+
- `uv` for Python project management
- `typer` for the startup script
- `ruff` for formatting and linting
- `ty` for type checking
- FastAPI + Uvicorn for the backend API
- Next.js App Router + TypeScript for the optional frontend

## Setup

Install Python dependencies with `uv`:

```bash
uv sync
```

## Run The Console App

```bash
uv run gym-recommender
```

This is the safest lab/demo mode because it depends only on Python and the local JSON database.

## Run The FastAPI Backend

```bash
uv run uvicorn gym_recommender.api:app --reload
```

Default backend URL:

- `http://127.0.0.1:8000`

Useful endpoints:

- `GET /api/health`
- `GET /api/gyms`
- `GET /api/gyms/{gym_id}`
- `POST /api/search`
- `POST /api/recommend`
- `POST /api/compare`
- `POST /api/gyms`
- `PUT /api/gyms/{gym_id}`

## Run The Next.js Web UI

The web UI is optional and intended as a presentation/demo layer on top of the Python backend.

1. Start the FastAPI backend first.
2. In a second terminal, run:

```bash
cd web
npm install
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Default frontend URL:

- `http://localhost:3000`

Available pages:

- `/`
  Overview dashboard and featured gyms
- `/browse`
  Search and sort gyms
- `/recommend`
  Recommendation form and top matches
- `/compare`
  Side-by-side comparison view
- `/admin`
  Simple create/update admin form

## Start With The Typer Script

The project includes a Typer launcher at `scripts/start_app.py`.

```bash
uv run python scripts/start_app.py console
uv run python scripts/start_app.py api
uv run python scripts/start_app.py install-web
uv run python scripts/start_app.py web
uv run python scripts/start_app.py fullstack
```

Run `install-web` once before `web` or `fullstack` so `next` is installed in `web/node_modules`.

Use `fullstack` when you want the backend and Next.js UI to start together.
If port `8000` or `3000` is already in use, the launcher will automatically move to the next available port and print the new URL.

## Development Checks

Run formatting, linting, type checking, and tests:

```bash
uv run ruff format .
uv run ruff check .
uv run ty check
uv run python -m unittest
```

If you want a quick Python-only verification:

```bash
PYTHONPATH=src python3 -m unittest
PYTHONPYCACHEPREFIX=.pycache PYTHONPATH=src python3 -m compileall src tests
```

## Enrich Gym Data With Google Maps

The project stays fully functional offline, but you can optionally enrich `data/gyms.json` with live Google Places data.

This utility uses the Google Places API (New) Text Search and Place Details endpoints to add a nested `google_maps` block to each gym record, including items such as:

- Place ID
- Formatted address
- Latitude and longitude
- Google Maps link
- Website
- International phone number
- Live rating and rating count
- Opening-hours summary

Set your API key in `.env` and run the script:

```bash
PYTHONPATH=src python3 scripts/fetch_google_maps_data.py --output data/gyms.enriched.json
```

Useful options:

- `--input data/gyms.json`
- `--output data/gyms.enriched.json`
- `--limit 3`
- `--refresh`
- `--country-hint Singapore`

If you omit `--output`, the script overwrites the input JSON file in place.

Current root `.env` variables:

- `GOOGLE_MAPS_API_KEY`
- `NEXT_PUBLIC_API_BASE_URL`

## Notes For Demo And Submission

- The console app is the primary deliverable and fallback demo path.
- The JSON database is the single source of truth for both console and web flows.
- The Next.js frontend is optional and should be treated as a showcase layer.
- If Node.js is unavailable in the lab, the project still works through the console interface.
- If internet access is restricted, the system still works because it does not depend on live map or API calls for gym data.
