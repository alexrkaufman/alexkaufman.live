import datetime
import os

from flask import Flask
from flask import render_template, render_template_string, current_app
import pathlib
from flask.helpers import redirect
import frontmatter
import mistune


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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
        return dict(site_name="alexkaufman.live")

    @app.route("/")
    def home_page():
        home_path = pathlib.Path(current_app.root_path) / "content/home.md"
        shows = load_shows()
        upcoming_shows = [
            show for show in shows if show["show_date"] > datetime.date.today()
        ]
        upcoming_shows.sort(key=lambda x: x["show_date"], reverse=True)
        home = frontmatter.load(str(home_path))
        content = render_template_string(
            str(mistune.html(home.content)), upcoming_shows=upcoming_shows
        )
        return render_template("base.jinja2", content=content)

    @app.route("/blog/")
    def blog_redirect():
        return redirect("https://blog.alexkaufman.live", code=302)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.jinja2"), 404

    from . import shows

    app.register_blueprint(shows.bp)

    return app


def load_shows():

    shows_path = pathlib.Path(current_app.root_path) / "content/shows"
    shows = [
        {**frontmatter.load(str(show)), "link": show.stem}
        for show in list(shows_path.glob("**/*.md"))
    ]
    return shows
