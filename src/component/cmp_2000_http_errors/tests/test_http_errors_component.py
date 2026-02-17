"""Tests for the http_errors component."""

from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_COMP_DIR = _TEST_DIR.parent
_BP_NAME = f"bp_{_COMP_DIR.name}"


def test_http_errors_blueprint_registered(flask_app):
    """Component blueprint should be registered using folder name."""
    assert _BP_NAME in flask_app.blueprints


def test_http_errors_handler_registered(flask_app):
    """Blueprint should register a global Exception handler."""
    blueprint = flask_app.blueprints[_BP_NAME]

    handler = blueprint.error_handler_spec[None][None].get(Exception)
    assert callable(handler)
    assert handler.__name__ == "handle_exception"

