# cs329z.github.io

Course website for **CS329Z: Engineering AI Agents** (Stanford).

Built with Flask + Jinja2 + [Flask-FlatPages](https://flask-flatpages.readthedocs.io/)
(markdown) + [Frozen-Flask](https://frozen-flask.readthedocs.io/) (static export).
Content is modular so collaborators can edit it without touching HTML.

## Editing content

Everything you'd normally change lives in plain data / markdown files:

| To change… | Edit… |
|---|---|
| Instructors / TAs | `data/staff.json` |
| Weekly lectures, themes, readings | `data/schedule.json` |
| Guest speakers | add a `"speakers": [{"name": "…", "url": "https://…"}]` list to the lecture in `data/schedule.json` |
| Lecture code repo | add a `"code_url": "https://github.com/…"` link to the lecture in `data/schedule.json` (renders as a "Code" button next to "Slides") |
| Lecture slides | add a `"slides_url": "https://…"` link to the lecture in `data/schedule.json` |
| Lecture video | add a `"video_url": "https://…"` link to the lecture in `data/schedule.json` (renders as a "Video" button next to "Slides") |
| Assignment & project deadlines | `data/deadlines.json` |
| Welcome blurb | `pages/welcome.md` |
| Temporary site-wide notice | `pages/announcement.md` (set `expires:` to auto-hide; delete the file to remove it) |
| Assignments & grading | `pages/coursework.md` |
| Project description | `pages/project.md` |
| Logistics (info, office hours, prerequisites, honor code, accommodations) | `pages/logistics.md` |
| Look & feel | `static/css/main.css` |
| Logos / headshots | `static/images/` (referenced by name from `data/staff.json`) |

The page layouts live in `templates/index.html`,
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

### Lecture videos (automatic)

Every afternoon, `lecture-videos.yml` checks the Stanford Online YouTube
channel for uploads with "CS329Z" in the title, skipping Shorts. Each new one
gets a PR that adds its `video_url` to the lecture named by "Lecture N" in the
title and tags the GitHub users in `PR_REVIEWERS` in that workflow file:

- **Title says "Lecture N":** the PR is merged right away and the site
  redeploys (set `AUTO_MERGE: "false"` in the workflow to review these too). If
  one is wrong, use the **Revert** button on its PR.
- **No lecture number, but a guest speaker's name:** the PR stays open and
  requests review. Merge it to publish, or close it to skip that video.
- **Anything else** (clips, trailers) is ignored.

Run it by hand from the repo's **Actions** tab, or locally with
`python3 .github/scripts/lecture_videos.py --dry-run`.

A [cron-job.org](https://cron-job.org) job (set up by XenonMolecule) starts it
through GitHub's API several times each afternoon from 1:15 p.m. Pacific
(YouTube's feed can take an hour or more to list a new upload; runs that find
nothing change nothing), using a fine-grained token
that can only run Actions in this repo. When the token expires, cron-job.org
reports the job as failing: create a new token and paste it into the job's
`Authorization` header. The `schedule` in the workflow file is only a backup,
because GitHub currently starts scheduled runs hours late.

For the preview link on PRs left open, the action resets `staging` to `main`
plus every open video PR. It only does this when `staging` has no commits from
anyone else, so your drafts are safe. Its preview commits can still be there when you start a
draft, so begin with `git checkout -B staging origin/main` rather than
`git merge main`. Otherwise merging `staging` into `main` would also publish
the pending videos.

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
