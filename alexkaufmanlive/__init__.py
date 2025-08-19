import os
import pathlib

import frontmatter
import mistune
from flask import (
    Flask,
    current_app,
    get_template_attribute,
    make_response,
    render_template,
    render_template_string,
    request,
)
from flask.helpers import redirect
from mistune.directives import FencedDirective, Image

from .db import get_db

site_metadata = {
    "site_name": "alexkaufman.live",
    "tagline": "standup comic/former physicist",
}

markdown = mistune.create_markdown(
    plugins=[
        FencedDirective([Image()]),
    ],
    escape=False,
)


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
                "SELECT id, title, show_date, link, meta"
                " FROM shows"
                " WHERE show_date >= CURRENT_DATE"
                " ORDER BY show_date ASC"
            )
        ).fetchall()

        home = frontmatter.load(str(home_path))
        content = render_page(
            home.content,
            upcoming_shows=upcoming_shows,
            show_list=get_template_attribute("parts.jinja2", "show_list"),
        )

        return render_template(
            "base.jinja2", content=content, title="alexkaufman.live", page_class="home"
        )

    @app.route("/epk")
    def epk():
        """Builds the home page of the site."""

        db = get_db()
        epk_path = pathlib.Path(current_app.root_path) / "content/epk.md"

        epk = frontmatter.load(str(epk_path))
        content = render_page(
            epk.content,
            show_list=get_template_attribute("parts.jinja2", "show_list"),
        )

        return render_template(
            "epk.jinja2", content=content, title="alexkaufman.live", page_class="epk"
        )

    @app.route("/sitemap")
    @app.route("/sitemap/")
    @app.route("/sitemap.xml")
    def sitemap():
        """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
        """
        from urllib.parse import urlparse

        host_components = urlparse(request.host_url)
        host_base = host_components.scheme + "://" + host_components.netloc

        urls = list()
        # Static routes with static content
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {"loc": f"{host_base}{str(rule)}"}
                urls.append(url)

        # Dynamic routes with dynamic content
        db = get_db()
        shows = db.execute(
            "SELECT id, title, show_date, link FROM shows ORDER BY show_date ASC"
        ).fetchall()
        for show in shows:
            url = {
                "loc": f"{host_base}/shows/{show['link']}",
            }
            urls.append(url)

        xml_sitemap = render_template(
            "sitemap_template.jinja2",
            urls=urls,
            host_base=host_base,
        )
        response = make_response(xml_sitemap)
        response.headers["Content-Type"] = "application/xml"
        return response

    @app.route("/blog/")
    def blog_redirect():
        return redirect("https://blog.alexkaufman.live", code=302)

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

    from . import shows

    app.register_blueprint(shows.bp)

    from . import db

    db.init_app(app)

    return app


def render_page(content, **kwargs):
    return render_template_string(markdown(content), **kwargs)
