import os
import pathlib

import frontmatter
import mistune
import requests
from flask import (
    Flask,
    current_app,
    get_template_attribute,
    jsonify,
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
            email_list_cta=get_template_attribute("parts.jinja2", "email_list_cta"),
        )

        return render_template(
            "base.jinja2", content=content, title="alexkaufman.live", page_class="home"
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

    @app.route("/api/subscribe", methods=["POST"])
    def email_subscribe():
        """Handle email subscription via Buttondown API"""
        try:
            email = request.form.get("email")
            tags = request.form.getlist("tag")

            if not email:
                return jsonify({"success": False, "error": "Email is required"}), 400

            # Prepare data for Buttondown API
            data = {"email_address": email}
            data["type"] = "regular"
            for tag in tags:
                data["tag"] = tag

            # Make request to Buttondown API
            url = "https://api.buttondown.com/v1/subscribers"
            headers = {
                "Authorization": "Token daa462da-c883-4efa-a9e3-9e080bc204b9",
                "X-Buttondown-Collision-Behavior": "add",
            }

            response = requests.request(
                "POST", url, headers=headers, json=data, timeout=10
            )

            if response.status_code == 201:
                return jsonify({"success": True, "message": "Successfully subscribed!"})
            else:
                return jsonify({"success": False, "error": "Failed to subscribe"}), 400

        except requests.RequestException:
            return jsonify({"success": False, "error": "Network error occurred"}), 500
        except Exception:
            return jsonify({"success": False, "error": "An error occurred"}), 500

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
