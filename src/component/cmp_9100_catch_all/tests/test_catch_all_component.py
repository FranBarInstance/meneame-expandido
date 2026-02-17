"""Tests for the catch_all component."""

from pathlib import Path

from app.config import Config

_TEST_DIR = Path(__file__).resolve().parent
_COMP_DIR = _TEST_DIR.parent
_BP_NAME = f"bp_{_COMP_DIR.name}"


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def _methods_for_rule(flask_app, rule_path: str) -> set[str]:
    methods = set()
    for rule in flask_app.url_map.iter_rules():
        if rule.rule == rule_path:
            methods.update(rule.methods)
    return methods


def test_catch_all_blueprint_and_routes_registered(flask_app):
    """Component should register catch-all rules."""
    assert _BP_NAME in flask_app.blueprints

    methods = _methods_for_rule(flask_app, _route(flask_app, "/<anyext:route>"))
    assert "GET" in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/<path:route>"))
    assert "GET" in methods


def test_catch_all_serves_existing_public_asset(client):
    """Known static public file should be served with static cache header."""
    response = client.get(_route(client.application, "/favicon.ico"))

    assert response.status_code == 200
    assert response.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL

