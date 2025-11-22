import pathlib

from flask import (
    Blueprint,
    abort,
    get_template_attribute,
    redirect,
    render_template,
    render_template_string,
)

from ..db import get_db
from ..services.markdown import render_page

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
            "SELECT id, title, show_date, link, meta"
            " FROM shows"
            " WHERE show_date >= CURRENT_DATE"
            " ORDER BY show_date ASC"
        )
    ).fetchall()
    past_shows = db.execute(
        (
            "SELECT id, title, show_date, link, meta"
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

    macros = {
        "eventbrite_button": get_template_attribute(
            "parts.jinja2",
            "eventbrite_button",
        ),
        "event_button": get_template_attribute(
            "parts.jinja2",
            "event_button",
        ),
        "tickettailor_button": get_template_attribute(
            "parts.jinja2",
            "tickettailor_button",
        ),
        "email_list_cta": get_template_attribute(
            "parts.jinja2",
            "email_list_cta",
        ),
    }

    db = get_db()

    show = db.execute(
        "SELECT * FROM shows WHERE link=:link", {"link": show_slug}
    ).fetchone()

    if not show:
        abort(404)

    if show["redirect"] is not None:
        return redirect(show["redirect"], code=302)

    show = dict(show)
    show["content"] = render_page(
        render_template_string(show["content"], **show, **macros)
    )
    return render_template("show.jinja2", **show)
