import os

from flask import Flask
from flask import render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.route("/")
    def home_page():
        return "<p>Home Page</p>"

    @app.route("/about")
    def about_page():
        return "<p>About</p>"

    @app.route("/shows/")
    def shows_page():
        return "<p>Shows</p>"

    @app.route("/blog/")
    def blog_page():
        return "<p>Blog</p>"

    return app
