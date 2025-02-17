import pathlib

import mistune

from flask import (
    Blueprint,
    get_template_attribute,
    render_template,
    render_template_string,
)

from .db import get_db

bp = Blueprint("shows", __name__, url_prefix="/shows")
shows_path = pathlib.Path("shows/")
shows_metadata = {"page_class": "shows"}


@bp.context_processor
def inject_sitename():
    return shows_metadata


@bp.route("/")
def index():
    """Show list page."""
    db = get_db()

    upcoming_shows = db.execute(
        (
            "SELECT id, title, show_date, link"
            " FROM shows"
            " WHERE show_date >= CURRENT_DATE"
            " ORDER BY show_date ASC"
        )
    ).fetchall()
    past_shows = db.execute(
        (
            "SELECT id, title, show_date, link"
            " FROM shows"
            " WHERE show_date < CURRENT_DATE"
            " ORDER BY show_date DESC"
        )
    ).fetchall()

    return render_template(
        "shows.jinja2",
        upcoming_shows=upcoming_shows,
        past_shows=past_shows,
        title="alexkaufman.live | shows",
    )


@bp.route("/<show_slug>")
def show(show_slug):
    """Show all the posts, most recent first."""

    db = get_db()

    show = db.execute(
        "SELECT *"
        f" FROM shows WHERE link='{show_slug}'"
    ).fetchone()

    if show != []:
        show = dict(show)
        show["content"] = mistune.html(
            render_template_string(
                show["content"],
                show=show,
                eventbrite_button=get_template_attribute(
                    "parts.jinja2", "eventbrite_button"
                ),
            )
        )
        return render_template("show.jinja2", show=show)

    return render_template("404.jinja2"), 404
