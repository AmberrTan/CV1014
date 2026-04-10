from __future__ import annotations

import importlib.util
from pathlib import Path


def test_start_app_imports_without_missing_module() -> None:
    """Ensure start_app can import project modules without ModuleNotFoundError."""
    start_app_path = Path(__file__).resolve().parents[1] / "scripts" / "start_app.py"
    spec = importlib.util.spec_from_file_location("start_app", start_app_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        raise AssertionError("start_app.py should be importable without missing modules") from exc
