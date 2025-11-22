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

    Process Jinja variables first, then convert markdown to HTML.
    This order ensures:
    - Jinja variables can be used in markdown syntax
    - Special characters (&, etc.) are handled correctly
    - Macros generate clean HTML that markdown passes through

    Note: Auto-escaping is disabled globally in the Flask app.

    Args:
        content: Markdown content string (may contain Jinja template syntax)
        **kwargs: Template variables to pass to Jinja2

    Returns:
        Rendered HTML string
    """
    # 1. Process Jinja template variables in the markdown
    templated_content = render_template_string(content, **kwargs)
    # 2. Convert markdown to HTML
    return markdown(templated_content)
