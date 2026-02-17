"""Tests for the pwa component."""

from pathlib import Path

from app.config import Config

_TEST_DIR = Path(__file__).resolve().parent
_COMP_DIR = _TEST_DIR.parent
_BP_NAME = f"bp_{_COMP_DIR.name}"


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def test_pwa_blueprint_registered(flask_app):
    """Component blueprint should be registered using folder name."""
    assert _BP_NAME in flask_app.blueprints


def test_pwa_service_worker_and_manifest(client):
    """PWA static endpoints should return content and cache headers."""
    blueprint = client.application.blueprints[_BP_NAME]
    static_dir = blueprint.component["manifest"]["config"]["static-dir"]

    service_worker = client.get(_route(client.application, "/service-worker.js"))
    manifest = client.get(_route(client.application, f"/{static_dir}/manifest.json"))

    assert service_worker.status_code == 200
    assert manifest.status_code == 200
    assert service_worker.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL
    assert manifest.headers.get("Cache-Control") == Config.STATIC_CACHE_CONTROL

