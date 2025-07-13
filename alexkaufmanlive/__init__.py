import os
import pathlib

import frontmatter
import mistune
from flask import (
    Flask,
    current_app,
    get_template_attribute,
    render_template,
    render_template_string,
    send_from_directory,
)
from flask.helpers import redirect

from .db import get_db

site_metadata = {
    "site_name": "alexkaufman.live",
    "tagline": "Standup comedian / Former physicist",
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

    @app.route("/")
    def home_page():
        """Builds the home page of the site."""

        db = get_db()
        home_path = pathlib.Path(current_app.root_path) / "content/home.md"

        upcoming_shows = db.execute(
            (
                "SELECT id, title, show_date, link"
                " FROM shows"
                " WHERE show_date >= CURRENT_DATE"
                " ORDER BY show_date ASC"
            )
        ).fetchall()

        home = frontmatter.load(str(home_path))
        content = render_template_string(
            str(mistune.html(home.content)),
            upcoming_shows=upcoming_shows,
            show_list=get_template_attribute("parts.jinja2", "show_list"),
        )

        return render_template(
            "base.jinja2", content=content, title="alexkaufman.live", page_class="home"
        )

    @app.route("/sitemap.xml")
    def sitemap_xml():
        send_from_directory(app.static_folder, "sitemap.xml")

    @app.route("/blog/")
    def blog_redirect():
        return redirect("https://blog.alexkaufman.live", code=302)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.jinja2"), 404

    from . import shows

    app.register_blueprint(shows.bp)

    from . import db

    db.init_app(app)

    return app
