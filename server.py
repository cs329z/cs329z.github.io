#!/usr/bin/env python3
"""CS329Z course website.

Content lives in editable source files, rendered by Jinja2 templates:

    data/staff.json       instructors / course staff
    data/schedule.json    weekly lectures + readings
    data/deadlines.json   assignment & project deadlines
    pages/*.md            prose sections (welcome, coursework, project, logistics)

Run locally:   uv run python server.py         (serves http://localhost:5001)
Build static:  uv run python server.py build   (writes build/, deploy anywhere)
"""
import json
import os
import sys

from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]
FREEZER_DESTINATION = "build"
FREEZER_RELATIVE_URLS = True          # so the site works from any subpath / file://
FREEZER_IGNORE_MIMETYPE_WARNINGS = True

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)


def load_json(name):
    with open(os.path.join("data", name)) as f:
        return json.load(f)


def section(name):
    """A prose section from pages/<name>.md: {title, html}."""
    page = pages.get(name)
    if not page:
        return {"title": "", "html": ""}
    return {"title": page.meta.get("title", ""), "html": page.html}


def render_index():
    return render_template(
        "index.html",
        staff=load_json("staff.json"),
        schedule=load_json("schedule.json"),
        deadlines=load_json("deadlines.json"),
        welcome=section("welcome"),
        coursework=section("coursework"),
        project=section("project"),
        logistics=section("logistics"),
    )


@app.route("/")
def index():
    return render_index()


@app.errorhandler(404)
def not_found(e):
    return render_index(), 404


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        with app.app_context():
            freezer.freeze()
        print("Built static site into build/")
    else:
        port = int(os.environ.get("PORT", 5001))
        app.run(host="0.0.0.0", port=port, debug=True, use_debugger=False,
                extra_files=["templates", "static", "data", "pages"])
