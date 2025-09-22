import json
import pathlib
import sqlite3
from datetime import datetime

import click
import frontmatter
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(update_db_command)


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    update_db()


def update_db():
    db = get_db()
    shows_path = pathlib.Path(current_app.root_path) / "content/shows"
    show_files = list(shows_path.glob("**/*.md"))
    links = set()

    for show_file in show_files:
        show_data = dict.fromkeys(
            ["title", "show_date", "content", "link", "meta", "image", "redirect"], None
        )
        show_data |= frontmatter.load(str(show_file)).to_dict()

        show_data["link"] = (
            show_file.stem if show_data["link"] is None else show_data["link"]
        )

        db.execute(
            (
                "INSERT INTO shows (title, show_date, content, link, meta, image, redirect)"
                " values (:title, :show_date, :content, :link, json(:meta), :image, :redirect)"
                " ON CONFLICT(link)"
                " do UPDATE SET title=:title, show_date=:show_date, content=:content, meta=json(:meta), image=:image, redirect=:redirect"
            ),
            show_data,
        )

        links.add(show_data["link"])

        db.commit()

    links_in_db = {
        show["link"] for show in db.execute("SELECT link FROM shows").fetchall()
    }
    dead_links = links_in_db - links
    if len(dead_links) != 0:
        db.execute(
            (
                "DELETE FROM shows WHERE link IN ("
                + ",".join(["?"] * len(dead_links))
                + ")"
            ),
            list(dead_links),
        )
        db.commit()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("update-db")
def update_db_command():
    """Clear the existing data and create new tables."""
    update_db()
    click.echo("Updated the database.")


sqlite3.register_adapter(dict, lambda d: json.dumps(d).encode())
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))
sqlite3.register_converter("JSON", lambda v: json.loads(v.decode()))


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
