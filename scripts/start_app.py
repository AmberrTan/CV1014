from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

import typer

from gym_recommender.config import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "web"
WEB_NODE_MODULES = WEB_DIR / "node_modules"
WEB_NEXT_BIN = WEB_NODE_MODULES / ".bin" / "next"

app = typer.Typer(
    help="Start the Gym Recommendation System console app, API, web UI, or full stack."
)
load_dotenv()


def _run(command: list[str], *, cwd: Path | None = None) -> int:
    process = subprocess.run(command, cwd=cwd or ROOT_DIR, check=False)
    return process.returncode


def _spawn(command: list[str], *, cwd: Path | None = None) -> subprocess.Popen[str]:
    return subprocess.Popen(command, cwd=cwd or ROOT_DIR, text=True)


def _terminate(processes: list[subprocess.Popen[str]]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        if process.poll() is None:
            process.wait(timeout=5)


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _pick_port(host: str, preferred: int) -> int:
    port = preferred
    while not _port_available(host, port):
        port += 1
    return port


def _wait_for_exit(process: subprocess.Popen[str]) -> int:
    while process.poll() is None:
        time.sleep(1)
    return process.poll() or 0


def _ensure_web_dependencies_installed() -> None:
    if WEB_NEXT_BIN.exists():
        return
    typer.echo("Next.js dependencies are not installed yet.")
    typer.echo("Run: uv run python scripts/start_app.py install-web")
    raise typer.Exit(1)


def _ensure_localstorage_file(node_options: str | None) -> str:
    storage_flag = "--localstorage-file=/tmp/node-localstorage.json"
    if not node_options:
        return storage_flag
    if "--localstorage-file" in node_options:
        return node_options
    return f"{node_options} {storage_flag}"


def _ensure_command_exists(command: str, install_hint: str) -> None:
    try:
        subprocess.run([command, "--version"], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        typer.echo(f"'{command}' is not available on your PATH.")
        typer.echo(install_hint)
        raise typer.Exit(1) from exc


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


@app.command()
def web(
    api_base_url: str = typer.Option(
        "http://127.0.0.1:8000",
        help="Backend base URL exposed to the Next.js app.",
    ),
    port: int = typer.Option(3000, help="Preferred port for the Next.js dev server."),
) -> None:
    """Start the Next.js showcase UI."""
    _ensure_command_exists("npm", "Install Node.js and npm, then run this command again.")
    _ensure_web_dependencies_installed()
    env = os.environ.copy()
    env["NEXT_PUBLIC_API_BASE_URL"] = api_base_url
    env["NODE_OPTIONS"] = _ensure_localstorage_file(env.get("NODE_OPTIONS"))
    actual_port = _pick_port("127.0.0.1", port)
    if actual_port != port:
        typer.echo(f"Port {port} is in use for the web UI. Using {actual_port} instead.")
    process = subprocess.run(
        ["npm", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", str(actual_port)],
        cwd=WEB_DIR,
        env=env,
        check=False,
    )
    raise typer.Exit(process.returncode)


@app.command()
def fullstack(
    host: str = typer.Option("127.0.0.1", help="Host for the FastAPI server."),
    port: int = typer.Option(8000, help="Port for the FastAPI server."),
    web_port: int = typer.Option(3000, help="Preferred port for the Next.js dev server."),
) -> None:
    """Start the FastAPI backend and Next.js frontend together."""
    _ensure_command_exists("npm", "Install Node.js and npm, then run this command again.")
    _ensure_web_dependencies_installed()
    api_port = _pick_port(host, port)
    frontend_port = _pick_port("127.0.0.1", web_port)
    if api_port != port:
        typer.echo(f"Port {port} is in use for the API. Using {api_port} instead.")
    if frontend_port != web_port:
        typer.echo(f"Port {web_port} is in use for the web UI. Using {frontend_port} instead.")

    env = os.environ.copy()
    api_base_url = f"http://{host}:{api_port}"
    env["NEXT_PUBLIC_API_BASE_URL"] = api_base_url
    env["NODE_OPTIONS"] = _ensure_localstorage_file(env.get("NODE_OPTIONS"))

    processes = [
        _spawn(
            [
                "uv",
                "run",
                "uvicorn",
                "gym_recommender.api:app",
                "--reload",
                "--host",
                host,
                "--port",
                str(api_port),
            ]
        ),
        subprocess.Popen(
            ["npm", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", str(frontend_port)],
            cwd=WEB_DIR,
            env=env,
            text=True,
        ),
    ]

    typer.echo(f"API starting at {api_base_url}")
    typer.echo(f"Web UI starting at http://127.0.0.1:{frontend_port}")
    typer.echo("Press Ctrl+C to stop both services.")

    api_process = processes[0]
    web_process = processes[1]

    try:
        while True:
            api_exit = api_process.poll()
            web_exit = web_process.poll()

            if api_exit is not None:
                if web_exit is None:
                    typer.echo("API process exited. Stopping the web UI.")
                break

            if web_exit is not None:
                typer.echo("Web UI process exited, but the API will keep running in reload mode.")
                typer.echo(
                    "The current Node.js binary looks incompatible with this macOS version. "
                    "Install an older Node release, then rerun "
                    "`uv run python scripts/start_app.py fullstack`."
                )
                typer.echo(f"API still available at {api_base_url}")
                typer.echo("Press Ctrl+C to stop the API watcher.")
                _wait_for_exit(api_process)
                break

            time.sleep(1)
    except KeyboardInterrupt:
        typer.echo("\nStopping services...")
    finally:
        _terminate(processes)

    exit_codes = [process.poll() or 0 for process in processes]
    raise typer.Exit(max(exit_codes))


@app.command()
def install_web() -> None:
    """Install Next.js dependencies inside the web app."""
    _ensure_command_exists("npm", "Install Node.js and npm, then run this command again.")
    raise typer.Exit(_run(["npm", "install"], cwd=WEB_DIR))


if __name__ == "__main__":
    app()
