from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
import datetime
import frontmatter
import mistune
from werkzeug.exceptions import abort
import pathlib
from alexkaufmanlive.db import get_db
from . import load_shows

bp = Blueprint("shows", __name__, url_prefix="/shows")
shows_path = pathlib.Path("shows/")


@bp.route("/")
def index():
    """Show list page."""
    shows = load_shows()

    upcoming_shows = [
        show for show in shows if show["show_date"] > datetime.date.today()
    ]
    upcoming_shows.sort(key=lambda x: x["show_date"])

    past_shows = [show for show in shows if show["show_date"] < datetime.date.today()]
    past_shows.sort(key=lambda x: x["show_date"], reverse=True)

    return render_template(
        "shows.jinja2", upcoming_shows=upcoming_shows, past_shows=past_shows
    )


@bp.route("/<show_slug>")
def show(show_slug):
    """Show all the posts, most recent first."""
    shows = load_shows()
    show_path = pathlib.Path(current_app.root_path) / f"content/shows/{show_slug}.md"
    show_load = frontmatter.load(str(show_path))
    show = {
        "metadata": show_load.metadata,
        "content": mistune.html(show_load.content),
    }
    return render_template("show.jinja2", show=show)
