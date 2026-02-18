"""Resumen IA routes module."""

from flask import Response, jsonify, request

from app.extensions import require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_resumen import Dispatcher, DispatcherResumen


def _require_session(dispatch: DispatcherResumen):
    """Return unauthorized response when session is not active."""
    if dispatch.schema_data["HAS_SESSION"] is None:
        return jsonify({
            "success": False,
            "error": "Authentication required"
        }), 401
    return None


@bp.route('/', defaults={'route': ''}, methods=['GET'])
def resumen(route) -> Response:
    """Handle resumen home page requests."""
    dispatch = DispatcherResumen(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = dispatch.set_resumen_name(bp.schema)
    return dispatch.view.render()


@bp.route('/ajax', methods=['GET'])
def resumen_ajax() -> Response:
    """Handle ajax requests."""
    dispatch = Dispatcher(request, "404")
    return dispatch.view.render_error()


@bp.route('/ajax/<resumen_name>', defaults={'route': 'ajax'}, methods=['GET'])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def resumen_ajax_name(route, resumen_name) -> Response:
    """Handle ajax with resumen name."""
    dispatch = DispatcherResumen(request, route, bp.neutral_route)

    unauthorized = _require_session(dispatch)
    if unauthorized:
        return unauthorized

    dispatch.schema_data['dispatch_result'] = dispatch.set_resumen_name(bp.schema, resumen_name)

    if not dispatch.schema_data['dispatch_result']:
        dispatch = Dispatcher(request, "404")
        return dispatch.view.render_error()

    return dispatch.view.render()


@bp.route('/site/<resumen_name>', defaults={'route': 'site'}, methods=['GET'])
def resumen_site_name(route, resumen_name) -> Response:
    """Serve resumen by site name."""
    dispatch = DispatcherResumen(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = dispatch.set_resumen_name(bp.schema, resumen_name)

    if not dispatch.schema_data['dispatch_result']:
        dispatch = Dispatcher(request, "404")
        return dispatch.view.render_error()

    return dispatch.view.render()


@bp.route('/<path:route>', methods=['GET'])
def resumen_catch_all(route) -> Response:
    """Handle undefined urls."""
    dispatch = DispatcherResumen(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = True
    return dispatch.view.render()
