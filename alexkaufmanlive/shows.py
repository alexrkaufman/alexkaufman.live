from flask import (
    Blueprint,
    render_template,
    current_app,
)
import datetime
import frontmatter
import mistune
import pathlib
from .db import load_shows

bp = Blueprint("shows", __name__, url_prefix="/shows")
shows_path = pathlib.Path("shows/")


@bp.route("/")
def index():
    """Show list page."""
    shows = load_shows()

    upcoming_shows = [
        show for show in shows if show["show_date"] > datetime.date.today()
    ]
    upcoming_shows.sort(key=lambda x: x["show_date"], reverse=True)

    past_shows = [show for show in shows if show["show_date"] < datetime.date.today()]
    past_shows.sort(key=lambda x: x["show_date"], reverse=True)

    return render_template(
        "shows.jinja2",
        upcoming_shows=upcoming_shows,
        past_shows=past_shows,
        title="alexkaufman.live | shows",
    )


@bp.route("/<show_slug>")
def show(show_slug):
    """Show all the posts, most recent first."""
    show_path = pathlib.Path(current_app.root_path) / f"content/shows/{show_slug}.md"
    if show_path.exists():
        show_load = frontmatter.load(str(show_path))
        show = {
            "metadata": show_load.metadata,
            "content": mistune.html(show_load.content),
        }
        return render_template(
            "show.jinja2", show=show, title=show["metadata"]["title"]
        )
    return render_template("404.jinja2"), 404
