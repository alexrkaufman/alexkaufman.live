import pathlib
import sqlite3
from datetime import datetime

import click
import frontmatter
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    shows_path = pathlib.Path(current_app.root_path) / "content/shows"
    show_files = list(shows_path.glob("**/*.md"))

    for show_file in show_files:
        show_data = dict.fromkeys(["title", "show_date", "content", "link"], None)
        show_data = {**show_data, **frontmatter.load(str(show_file)).to_dict()}
        show_data["link"] = (
            show_file.stem if show_data["link"] is None else show_data["link"]
        )

        db.execute(
            (
                "INSERT INTO shows (title, show_date, content, link)"
                "values (?, ?, ?, ?)"
            ),
            (
                show_data["title"],
                show_data["show_date"],
                show_data["content"],
                show_data["link"],
            ),
        )
        db.commit()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
