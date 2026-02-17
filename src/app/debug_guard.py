"""Shared debug guard helpers for all app entrypoints."""

import os
import time

from app.config import Config


def _is_truthy(value) -> bool:
    """Return True when value represents an enabled boolean flag."""
    return str(value).strip().lower() in {"true", "1", "yes"}


def is_debug_enabled(
    flask_debug_env=None,
    debug_file=None,
    debug_expire=None,
    now_ts=None,
) -> bool:
    """Return True only when FLASK_DEBUG is enabled and debug file is fresh."""
    flag = flask_debug_env if flask_debug_env is not None else os.getenv("FLASK_DEBUG", "false")
    if not _is_truthy(flag):
        return False

    debug_path = debug_file if debug_file is not None else Config.DEBUG_FILE
    if not debug_path:
        return False

    try:
        expire_seconds = int(debug_expire if debug_expire is not None else Config.DEBUG_EXPIRE)
    except (TypeError, ValueError):
        return False

    if expire_seconds <= 0:
        return False

    try:
        file_mtime = os.path.getmtime(debug_path)
    except OSError:
        return False

    current_ts = now_ts if now_ts is not None else time.time()
    return (current_ts - file_mtime) <= expire_seconds


def is_wsgi_debug_enabled(wsgi_debug_allowed=None) -> bool:
    """Require WSGI_DEBUG_ALLOWED as second gate on top of is_debug_enabled."""
    gate = (
        wsgi_debug_allowed
        if wsgi_debug_allowed is not None
        else os.getenv("WSGI_DEBUG_ALLOWED", "false")
    )
    return _is_truthy(gate) and is_debug_enabled()
