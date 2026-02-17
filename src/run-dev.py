"""This script initializes and runs the Flask application."""

from app import create_app

app = create_app()
debug_mode = app.debug

if __name__ == '__main__':
    app.run(debug=debug_mode)
