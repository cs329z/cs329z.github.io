#!/usr/bin/env python3
"""CS329Z course website.

Content lives in editable source files, rendered by Jinja2 templates:

    data/staff.json       instructors / course staff
    data/schedule.json    weekly lectures + readings
    data/deadlines.json   assignment & project deadlines
    pages/*.md            prose sections (welcome, coursework, project, logistics)

Run locally:   uv run python server.py         (serves http://localhost:5001)
Build static:  uv run python server.py build   (writes build/, deploy anywhere)
Staging build: SITE_STAGING=1 uv run python server.py build
"""
import json
import os
import sys
from datetime import datetime, time, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    COURSE_TZ = ZoneInfo("America/Los_Angeles")
except Exception:                      # pragma: no cover - fallback if tzdata is missing
    COURSE_TZ = timezone(timedelta(hours=-7))
from flask import Flask, redirect, render_template, url_for
from flask_flatpages import FlatPages
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]
FREEZER_DESTINATION = "build"
FREEZER_RELATIVE_URLS = True          # so the site works from any subpath / file://
FREEZER_IGNORE_MIMETYPE_WARNINGS = True
# Set SITE_STAGING=1 to build the staging preview (adds a banner + noindex).
STAGING = os.environ.get("SITE_STAGING") == "1"

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)


def asset_version():
    """Short hash of the stylesheet, appended to its URL to bust browser caches."""
    import hashlib
    with open(os.path.join("static", "css", "main.css"), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


@app.context_processor
def inject_globals():
    return {
        "staging": STAGING,
        "asset_version": asset_version(),
        # Temporary site-wide notice; delete pages/announcement.md to remove it.
        "announcement": announcement(),
    }


def load_json(name):
    with open(os.path.join("data", name)) as f:
        return json.load(f)


def section(name):
    """A prose section from pages/<name>.md: {title, html}."""
    page = pages.get(name)
    if not page:
        return {"title": "", "html": ""}
    return {"title": page.meta.get("title", ""), "html": page.html}


def announcement():
    """Temporary site-wide notice from pages/announcement.md.

    An optional `expires:` date in that file keeps the notice up through the end
    of that day, Pacific. Because the site is static, the cutoff is also emitted
    into the page so the browser hides the notice on time without a rebuild.
    """
    page = pages.get("announcement")
    if not page:
        return {"html": "", "expires_at_ms": None}

    expires = page.meta.get("expires")
    if not expires:
        return {"html": page.html, "expires_at_ms": None}

    if isinstance(expires, datetime):
        expires = expires.date()
    elif isinstance(expires, str):
        expires = datetime.strptime(expires.strip(), "%Y-%m-%d").date()

    # Show through the end of the expiry day, i.e. hide at midnight the next day.
    cutoff = datetime.combine(expires + timedelta(days=1), time.min, tzinfo=COURSE_TZ)
    if datetime.now(tz=COURSE_TZ) >= cutoff:
        return {"html": "", "expires_at_ms": None}      # already past: leave it out of the build
    return {"html": page.html, "expires_at_ms": int(cutoff.timestamp() * 1000)}


def render_index():
    return render_template(
        "index.html",
        staff=load_json("staff.json"),
        schedule=load_json("schedule.json"),
        deadlines=load_json("deadlines.json"),
        welcome=section("welcome"),
    )


@app.route("/")
def index():
    return render_index()


@app.route("/logistics.html")
def logistics():
    return render_template(
        "logistics.html",
        logistics=section("logistics"),
        coursework=section("coursework"),
    )


@app.route("/project.html")
def project():
    return render_template("project.html", project=section("project"))


@app.route("/office_hours.html")
def office_hours():
    """Keep old bookmarks working after office hours moved under Logistics."""
    return redirect(url_for("logistics") + "#office-hours")


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
