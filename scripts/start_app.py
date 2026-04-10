from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import typer

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"


def _ensure_src_on_path() -> None:
    src_path = str(SRC_DIR)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    existing = os.environ.get("PYTHONPATH", "")
    existing_parts = [part for part in existing.split(os.pathsep) if part]
    if src_path not in existing_parts:
        os.environ["PYTHONPATH"] = (
            src_path if not existing_parts else os.pathsep.join([src_path, *existing_parts])
        )


_ensure_src_on_path()

from gym_recommender.config import load_dotenv

app = typer.Typer(help="Start the Gym Recommendation System console app or API.")
load_dotenv()


def _run(command: list[str], *, cwd: Path | None = None) -> int:
    process = subprocess.run(command, cwd=cwd or ROOT_DIR, check=False)
    return process.returncode


@app.command()
def console() -> None:
    """Start the Python console application."""
    raise typer.Exit(_run(["uv", "run", "gym-recommender"]))


@app.command()
def api(
    host: str = typer.Option("127.0.0.1", help="Host for the FastAPI server."),
    port: int = typer.Option(8000, help="Port for the FastAPI server."),
) -> None:
    """Start the FastAPI backend."""
    raise typer.Exit(
        _run(
            [
                "uv",
                "run",
                "uvicorn",
                "gym_recommender.api:app",
                "--reload",
                "--host",
                host,
                "--port",
                str(port),
            ]
        )
    )


if __name__ == "__main__":
    app()
