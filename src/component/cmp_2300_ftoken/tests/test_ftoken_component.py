"""Tests for the ftoken component."""

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


def test_ftoken_blueprint_and_routes_registered(flask_app):
    """Component routes should be mounted with expected methods."""
    assert _BP_NAME in flask_app.blueprints

    methods = _methods_for_rule(flask_app, _route(flask_app, "/<key>/<fetch_id>/<form_id>"))
    assert "GET" in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/ftoken.min.js"))
    assert "GET" in methods


def test_ftoken_requires_ajax_header(client):
    """Token creation endpoint should reject non-AJAX requests."""
    response = client.get(_route(client.application, "/k/fetch/form"))
    assert response.status_code == 403


def test_ftoken_js_served(client):
    """ftoken.min.js should be served as static asset."""
    response = client.get(_route(client.application, "/ftoken.min.js"))

    assert response.status_code == 200
    assert response.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL

