"""Flask application factory."""

import os

from flask import (
    Flask,
    render_template,
)

from .config import Config

site_metadata = {
    "site_name": "alexkaufman.live",
    "tagline": "standup comic/former physicist",
}


def create_app(config: Config):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True, static_folder="content/static")

    # Disable auto-escaping since all content is controlled by site owner
    app.jinja_env.autoescape = False

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=config.secret_key,
        DATABASE=os.path.join(app.instance_path, config.database),
        GITHUB_WEBHOOK_SECRET=config.github_webhook_secret,
        BUTTONDOWN_API_TOKEN=config.buttondown_api_token,
    )
    app.logger.setLevel(config.log_level)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register context processor
    @app.context_processor
    def inject_sitename():
        return site_metadata

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        content = {
            "error_code": "404",
            "error_message": "I couldnt find the page you were looking for, but I appreciate you believing in me. ",
        }
        return render_template("error.jinja2", **content), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        content = {
            "error_code": "500",
            "error_message": "Well, this is embarassing. Something is broken.",
        }
        return render_template("error.jinja2", **content), 500

    # Register blueprints
    from .routes import main, shows

    app.register_blueprint(main.bp)
    app.register_blueprint(shows.bp)

    # Initialize database
    from . import db

    db.init_app(app)

    return app
