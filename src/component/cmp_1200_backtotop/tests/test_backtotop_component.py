"""Tests for the backtotop component."""

from pathlib import Path

from app.config import Config

_TEST_DIR = Path(__file__).resolve().parent
_COMP_DIR = _TEST_DIR.parent
_BP_NAME = f"bp_{_COMP_DIR.name}"


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def test_backtotop_blueprint_registered(flask_app):
    """Component blueprint should be registered using folder name."""
    assert _BP_NAME in flask_app.blueprints


def test_backtotop_assets_are_served(client):
    """Backtotop CSS and JS routes should return static assets."""
    css = client.get(_route(client.application, "/css/backtotop.min.css"))
    js = client.get(_route(client.application, "/js/backtotop.min.js"))

    assert css.status_code == 200
    assert js.status_code == 200
    assert css.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL
    assert js.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL

