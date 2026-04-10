from __future__ import annotations

import importlib.util

import pytest


def test_tui_module_exists() -> None:
    spec = importlib.util.find_spec("gym_recommender.tui")
    if spec is None:
        pytest.fail("gym_recommender.tui module is missing")


def test_build_app_returns_textual_app() -> None:
    spec = importlib.util.find_spec("gym_recommender.tui")
    if spec is None:
        pytest.skip("tui module not implemented yet")

    from textual.app import App

    from gym_recommender.tui import build_app

    app = build_app()
    assert isinstance(app, App)
