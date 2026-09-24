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
import csv
import json
import os
import sys
from datetime import datetime, timedelta

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
        # Temporary enrollment notice; delete pages/announcement.md to remove it.
        "announcement": section("announcement"),
    }


def load_json(name):
    with open(os.path.join("data", name)) as f:
        return json.load(f)


def load_office_hours():
    """Load weekly office hours from data/oh.csv."""
    day_order = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tues": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thur": 3,
        "thurs": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }
    staff = {
        "Diyi": {"name": "Diyi Yang", "location": "Gates 370"},
        "Michael": {"name": "Michael Ryan", "location": "Gates 3B Lounge"},
        "John": {"name": "John Yang", "location": "Gates 3B Lounge"},
    }
    weeks = []
    with open(os.path.join("data", "oh.csv"), newline="") as f:
        rows = csv.reader(f)
        next(rows, None)
        for row in rows:
            if not row:
                continue
            week_start = datetime.strptime(f"{row[1].strip()}/2026", "%m/%d/%Y").date()
            sessions = []
            for value in row[2:]:
                value = value.strip()
                if not value or value.lower() == "no office hour":
                    continue
                short_name, time = value.split(":", 1)
                person = staff[short_name.strip()]
                day, clock_time = time.strip().split(maxsplit=1)
                day_index = day_order[day.lower().rstrip(".")]
                session_date = week_start + timedelta(
                    days=(day_index - week_start.weekday()) % 7
                )
                sessions.append({
                    "name": person["name"],
                    "date": f"{session_date:%b} {session_date.day} ({session_date:%a})",
                    "time": clock_time,
                    "location": person["location"],
                    "day_index": day_index,
                })
            sessions.sort(key=lambda session: session["day_index"])
            weeks.append({
                "week": row[0].strip(),
                "date": row[1].strip() if len(row) > 1 else "",
                "sessions": sessions,
            })
    return weeks


def section(name):
    """A prose section from pages/<name>.md: {title, html}."""
    page = pages.get(name)
    if not page:
        return {"title": "", "html": ""}
    return {"title": page.meta.get("title", ""), "html": page.html}


def render_index():
    return render_template(
        "example_home.html",
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
        office_hours=load_office_hours(),
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
