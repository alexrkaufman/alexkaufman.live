import os

from flask import (
    Flask,
    render_template,
)

site_metadata = {
    "site_name": "alexkaufman.live",
    "tagline": "standup comic/former physicist",
}


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder="content/static")
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "alexkaufmanlive.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.context_processor
    def inject_sitename():
        return site_metadata

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

    from . import db

    db.init_app(app)

    return app
