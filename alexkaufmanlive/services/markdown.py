"""Markdown rendering service."""

import mistune
from flask import render_template_string
from mistune.directives import FencedDirective, Image

# Configure markdown renderer
markdown = mistune.create_markdown(
    plugins=[
        FencedDirective([Image()]),
    ],
    escape=False,
)


def render_page(content, **kwargs):
    """
    Render markdown content as HTML with Jinja2 template processing.

    Args:
        content: Markdown content string
        **kwargs: Template variables to pass to Jinja2

    Returns:
        Rendered HTML string
    """
    return render_template_string(markdown(content), **kwargs)
