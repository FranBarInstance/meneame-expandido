"""Tests for the home component."""

from pathlib import Path

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


def test_home_blueprint_and_root_route_registered(flask_app):
    """Component should register blueprint and GET route for home."""
    assert _BP_NAME in flask_app.blueprints
    methods = _methods_for_rule(flask_app, _route(flask_app, "/"))
    assert "GET" in methods


def test_home_route_responds(client):
    """Home route should be accessible."""
    response = client.get(_route(client.application, "/"))
    assert response.status_code == 200

