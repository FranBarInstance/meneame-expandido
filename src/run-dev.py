"""This script initializes and runs the Flask application."""

from app import create_app

app = create_app()
debug_mode = app.debug

if __name__ == '__main__':
    app.run(
        host=app.config.get('APP_BIND_IP', 'localhost'),
        port=app.config.get('APP_BIND_PORT', 55000),
        debug=debug_mode
    )
