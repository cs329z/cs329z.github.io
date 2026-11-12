#!/usr/bin/env python3
"""Propose newly uploaded CS329Z lecture videos for the course site.

Run daily by .github/workflows/lecture-videos.yml. Reads the Stanford Online
YouTube channel's upload feed and keeps videos whose title mentions CS329Z.
For each one that isn't on the site and hasn't been proposed before, it:

  1. pushes a branch lecture-video/lecture-NN-<youtube id> that adds the video
     as that lecture's "video_url" in data/schedule.json (NN comes from
     "Lecture N" in the video title) and opens a PR for it;
  2. rebuilds the staging preview (https://cs329z.stanford.edu/staging/) as
     main plus every open lecture-video PR, so the PR has a page to check.

Closing a PR without merging skips that video for good. Pass --dry-run to
print what would happen without changing anything in git or on GitHub.
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

CHANNEL_ID = "UCBa5G_ESCn8Yd4vw5U-gIcg"  # Stanford Online
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
NS = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
COURSE_RE = re.compile(r"\bCS\s?329Z\b", re.I)
LECTURE_RE = re.compile(r"\bLecture\s*#?\s*(\d+)\b", re.I)
BRANCH_RE = re.compile(r"lecture-video/lecture-(\d+)-([\w-]{11})")
SCHEDULE = "data/schedule.json"
PREVIEW_URL = "https://cs329z.stanford.edu/staging/"
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
# GitHub users to tag in each PR and request review from (set in the workflow).
REVIEWERS = os.environ.get("PR_REVIEWERS", "").replace(",", " ").split()


def run(*cmd, check=True):
    return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, text=True)


def git(*args, check=True):
    return run("git", "-c", f"user.name={BOT_NAME}", "-c", f"user.email={BOT_EMAIL}", *args, check=check)


def fetch_feed():
    """The channel's most recent uploads (YouTube serves the latest 15), oldest first."""
    for attempt in range(4):
        try:
            with urllib.request.urlopen(FEED_URL, timeout=30) as resp:
                root = ET.fromstring(resp.read())
            break
        except (OSError, ET.ParseError):
            if attempt == 3:
                raise
            time.sleep(20 * (attempt + 1))
    videos = [{"id": e.findtext("yt:videoId", namespaces=NS),
               "title": e.findtext("atom:title", namespaces=NS),
               "published": e.findtext("atom:published", namespaces=NS)}
              for e in root.findall("atom:entry", NS)]
    return sorted(videos, key=lambda v: v["published"])


def class_lectures(schedule):
    """Class meetings in order, numbered like the slides (lecture01.pdf, ...):
    every lecture in a numbered week except holidays."""
    return [lec for week in schedule if isinstance(week.get("week"), int)
            for lec in week["lectures"] if not lec.get("holiday")]


def youtube_id(url):
    m = re.search(r"(?:youtu\.be/|[?&]v=|/embed/|/live/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def add_video_url(text, lecture, url):
    """Insert "video_url" into the lecture's entry in schedule.json, editing only
    that spot so the hand-formatted file keeps its layout."""
    lines = text.splitlines(keepends=True)
    date_line = f'"date": {json.dumps(lecture["date"], ensure_ascii=False)},'
    start = next((i for i, line in enumerate(lines) if line.strip() == date_line), None)
    if start is None:
        raise RuntimeError(f"Can't find {date_line} in {SCHEDULE}")
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip().startswith(('"readings"', '"date"', "}"))), len(lines))
    block = range(start, end)
    # Put it right after the slides link (it renders next to it), else after the description.
    anchor = next(i for key in ('"slides_url"', '"slides"', '"description"', '"title"')
                  for i in block if lines[i].strip().startswith(key))
    indent = lines[anchor][: len(lines[anchor]) - len(lines[anchor].lstrip())]
    entry = f'{indent}"video_url": {json.dumps(url)}'
    if lines[anchor].rstrip().endswith(","):
        lines.insert(anchor + 1, entry + ",\n")
    else:  # anchor was the entry's last key
        lines[anchor] = lines[anchor].rstrip() + ",\n"
        lines.insert(anchor + 1, entry + "\n")
    new_text = "".join(lines)

    # The result must be exactly the old schedule plus this one field.
    want = json.loads(text)
    for lec in class_lectures(want):
        if lec["date"] == lecture["date"]:
            lec["video_url"] = url
    if json.loads(new_text) != want:
        raise RuntimeError(f"Editing {SCHEDULE} for {lecture['date']} changed more than video_url")
    return new_text


def pick_lecture(video, lectures, taken):
    """(index, guessed) of the lecture a video belongs to, or None. Uses "Lecture N"
    from the title; without one, guesses a guest lecture whose speaker is named in
    the title, else the first lecture that has no video and no pending PR."""
    m = LECTURE_RE.search(video["title"])
    if m:
        n = int(m.group(1))
        return (n - 1, False) if 1 <= n <= len(lectures) else None
    free = [i for i, lec in enumerate(lectures) if not lec.get("video_url") and i not in taken]
    named = [i for i in free if any(sp.get("name", "").lower() in video["title"].lower()
                                    for sp in lectures[i].get("speakers", []))]
    slots = named or free
    return (slots[0], True) if slots else None


def refresh_preview(refs):
    """Point staging at main plus the given branches and redeploy the site.
    Leaves staging alone (returns False) if it has commits someone else made."""
    authors = run("git", "log", "--format=%an", "origin/main..origin/staging", check=False).stdout
    if any(name != BOT_NAME for name in authors.splitlines()):
        print("::warning::staging has commits that aren't on main; not touching it.")
        return False
    git("switch", "--quiet", "-C", "staging-preview", "origin/main")
    for ref in refs:
        if git("merge", "--quiet", "--no-edit", ref, check=False).returncode:
            git("merge", "--abort", check=False)
            print(f"::warning::{ref} doesn't merge cleanly; left out of the preview.")
    git("push", "--quiet", "--force", "origin", "HEAD:refs/heads/staging")
    run("gh", "workflow", "run", "deploy.yml", "--ref", "main")
    return True


def pr_body(video, lec, n, guessed, preview_ok):
    url = f"https://youtu.be/{video['id']}"
    when = datetime.fromisoformat(video["published"]).astimezone(ZoneInfo("America/Los_Angeles"))
    tags = "".join(f"@{r} " for r in REVIEWERS)
    parts = [
        f"{tags}Stanford Online uploaded a new CS329Z video:",
        f"[![thumbnail](https://i.ytimg.com/vi/{video['id']}/mqdefault.jpg)]({url})\n"
        f"**[{video['title']}]({url})**, uploaded {when:%a %b %-d, %-I:%M %p %Z}",
        f"This adds it as the **Video** link for **Lecture {n}: {lec['title']}** ({lec['date']}).",
    ]
    if guessed:
        parts.append("> [!WARNING]\n> The video title has no lecture number, so this lecture is a "
                     "best guess. Check it before merging.")
    if preview_ok:
        parts.append(f"**Preview:** {PREVIEW_URL} (rebuilds about a minute after this PR opens "
                     "and shows every open lecture-video PR)")
    else:
        parts.append("**Preview:** not updated, because the `staging` branch has commits that "
                     "aren't on `main`.")
    parts.append(f"If the lecture is wrong, move the `video_url` line in `{SCHEDULE}` on this "
                 "branch. Close this PR without merging to skip the video; it won't be proposed again.")
    parts.append("<sub>Opened by `.github/workflows/lecture-videos.yml`.</sub>")
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="print the plan; change nothing")
    args = ap.parse_args()

    run("git", "fetch", "--quiet", "origin")
    text = run("git", "show", f"origin/main:{SCHEDULE}").stdout
    lectures = class_lectures(json.loads(text))
    on_site = {youtube_id(lec.get("video_url")) for lec in lectures} - {None}

    prs = json.loads(run("gh", "pr", "list", "--state", "all", "--limit", "1000",
                         "--json", "state,headRefName").stdout)
    bot_prs = [(m, pr["state"]) for pr in prs if (m := BRANCH_RE.fullmatch(pr["headRefName"]))]
    proposed = {m.group(2) for m, _ in bot_prs}
    pending = {m.group(0): int(m.group(1)) - 1 for m, state in bot_prs if state == "OPEN"}

    ours = [v for v in fetch_feed() if COURSE_RE.search(v["title"])]
    new = [v for v in ours if v["id"] not in on_site | proposed]
    print(f"{len(ours)} CS329Z video(s) in the feed, {len(new)} new.")

    taken = set(pending.values())
    created = []
    for video in new:
        pick = pick_lecture(video, lectures, taken)
        if pick is None:
            print(f"::warning::No lecture to attach {video['title']!r} to; skipping.")
            continue
        i, guessed = pick
        lec = lectures[i]
        if lec.get("video_url"):
            print(f"::warning::Lecture {i + 1} already has a video; skipping {video['title']!r}.")
            continue
        taken.add(i)
        branch = f"lecture-video/lecture-{i + 1:02d}-{video['id']}"
        title = f"Add video for Lecture {i + 1}: {lec['title']}" + (" (check lecture)" if guessed else "")
        new_text = add_video_url(text, lec, f"https://youtu.be/{video['id']}")
        created.append((branch, title, video, lec, i + 1, guessed))
        print(f"{video['title']!r} -> Lecture {i + 1} ({lec['date']}), branch {branch}")
        if args.dry_run:
            print("".join(difflib.unified_diff(text.splitlines(True), new_text.splitlines(True),
                                               SCHEDULE, SCHEDULE, n=1)))
            continue
        git("switch", "--quiet", "-C", branch, "origin/main")
        with open(SCHEDULE, "w", encoding="utf-8") as f:
            f.write(new_text)
        git("commit", "--quiet", "-am", title)
        git("push", "--quiet", "--force", "origin", f"HEAD:refs/heads/{branch}")

    if not created:
        return
    if args.dry_run:
        branch, title, *rest = created[-1]
        print(f"Would rebuild {PREVIEW_URL} and open PR(s). Last PR: {title}\n\n{pr_body(*rest, True)}")
        return
    preview_ok = refresh_preview([f"origin/{b}" for b in pending] + [b for b, *_ in created])
    for branch, title, *rest in created:
        reviewers = ["--reviewer", ",".join(REVIEWERS)] if REVIEWERS else []
        print(run("gh", "pr", "create", "--base", "main", "--head", branch, *reviewers,
                  "--title", title, "--body", pr_body(*rest, preview_ok)).stdout.strip())


if __name__ == "__main__":
    main()
