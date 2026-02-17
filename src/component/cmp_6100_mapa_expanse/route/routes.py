"""Home routes module."""

from flask import Response, request, send_from_directory

from app.config import Config
from core.dispatcher import Dispatcher

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route('/', defaults={'route': ''}, methods=['GET'])
def home(route) -> Response:
    """Route handler for the home page."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = True
    return dispatch.view.render()


@bp.route("/mapa.min.css", methods=["GET"])
def mapa_expanse_css() -> Response:
    """mapa_expanse.css"""
    response = send_from_directory(STATIC, "mapa.min.css")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route("/mapa.min.js", methods=["GET"])
def mapa_expanse_js() -> Response:
    """mapa_expanse.js"""
    response = send_from_directory(STATIC, "mapa.min.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
