# cs329z.github.io

Course website for **CS329Z: Engineering AI Agents** (Stanford).

Built with Flask + Jinja2 + [Flask-FlatPages](https://flask-flatpages.readthedocs.io/)
(markdown) + [Frozen-Flask](https://frozen-flask.readthedocs.io/) (static export).
Content is modular so collaborators can edit it without touching HTML.

## Editing content

Everything you'd normally change lives in plain data / markdown files:

| To change… | Edit… |
|---|---|
| Instructors / CAs | `data/staff.json` |
| Weekly lectures, themes, readings | `data/schedule.json` |
| Assignment & project deadlines | `data/deadlines.json` |
| Weekly office hours | `data/oh.csv` |
| Welcome blurb | `pages/welcome.md` |
| Assignments & grading | `pages/coursework.md` |
| Project description | `pages/project.md` |
| Logistics (info, office hours, prerequisites, honor code, accommodations) | `pages/logistics.md` |
| Look & feel | `static/css/main.css` |
| Logos / headshots | `static/images/` (referenced by name from `data/staff.json`) |

The page layouts live in `templates/example_home.html`,
`templates/logistics.html`, and `templates/project.html`; the shared shell
(navbar, `<head>`) is `templates/base.html`.

## Develop

```bash
uv sync                      # once, to install dependencies
uv run python server.py      # or: make preview
```

Serves at http://localhost:5001 with live reload. (Prefer this over opening
files directly — it's the normal workflow and avoids `file://` quirks.)

## Build the static site

```bash
uv run python server.py build   # or: make build
```

Writes a self-contained static site to `build/` (relative URLs, so it works
from any host or even opened directly). Deploy `build/` anywhere.

## Deploy

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every
push to `main`. Enable it once under **Settings → Pages → Source: GitHub Actions**.

| Branch | Published at |
|---|---|
| `main` | https://cs329z.stanford.edu/ (live) |
| `staging` | https://cs329z.stanford.edu/staging/ (preview, with a banner, `noindex`) |

### Staging workflow

Commit drafts to `staging` and share the preview link with co-instructors;
merge into `main` when they're approved:

```bash
git checkout staging && git merge main   # keep staging current
# ...edit, commit, push -> preview updates in a minute or two...
git checkout main && git merge staging && git push   # go live
```

A push to `staging` runs `staging.yml`, which re-triggers `deploy.yml` on
`main`; that workflow builds both branches into one Pages deployment (the
`github-pages` environment only permits deployments from `main`). If `staging`
is ever deleted, the live site still deploys on its own.

## Structure

```
data/        JSON content (staff, schedule, deadlines)
pages/       Markdown prose sections
templates/   Jinja2 templates for the shared shell and individual pages
static/      CSS, self-hosted font, images
server.py    Flask app + static-site generator
```

## TODO before launch

- Confirm instructor homepage URLs in `data/staff.json`
- Fill in schedule dates in `data/schedule.json` (currently `TBA`)
- Fill in deadline dates/times in `data/deadlines.json`
- Fill in remaining logistics: office hours and contact (`pages/logistics.md`)
- Add CAs to `data/staff.json` (`cas` array) as confirmed
- Add lecture-material links in `data/schedule.json` as released
