from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from alexkaufmanlive.db import get_db

bp = Blueprint("shows", __name__, url_prefix="/shows")


@bp.route("/")
def index():
    """Show list page."""
    shows = [{"title": "test"}, {"title": "test2"}]
    return render_template("shows.html", shows=shows)


@bp.route("/<title>")
def show(title):
    """Show all the posts, most recent first."""
    return render_template("show.html", title=title)
