"""Main application routes."""

import pathlib

import frontmatter
from flask import (
    Blueprint,
    current_app,
    get_template_attribute,
    jsonify,
    make_response,
    render_template,
    request,
)
from flask.helpers import redirect

from ..db import get_db
from ..services.email import subscribe_to_buttondown
from ..services.markdown import render_page

bp = Blueprint("main", __name__)


@bp.route("/")
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


@bp.route("/sitemap")
@bp.route("/sitemap/")
@bp.route("/sitemap.xml")
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
    for rule in current_app.url_map.iter_rules():
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


@bp.route("/blog/")
def blog_redirect():
    """Redirect to external blog."""
    return redirect("https://blog.alexkaufman.live", code=302)


@bp.route("/api/subscribe", methods=["POST"])
def email_subscribe():
    """Handle email subscription via Buttondown API."""
    email = request.form.get("email")
    tags = request.form.getlist("tag")

    success, message, status_code = subscribe_to_buttondown(email, tags)

    if success:
        return jsonify({"success": True, "message": message}), status_code
    else:
        return jsonify({"success": False, "error": message}), status_code
