#!/usr/bin/env python3
"""Decide which story of a fleet runs next and which branch it stacks on.

Reads a fleet manifest whose stories are listed in the order they stack, checks
it, then returns RUN, RESUME, BLOCKED or DONE for the first story that is not
done. A story stacks on the branch of the story before it, the first one on the
trunk. Contract violations exit 2.

The manifest is {"trunk": <branch>, "stories": [...]}. Each story has "id",
"story" (the path of its story file), "depends_on" (ids of stories listed
before it) and "status"; once it starts it also has its ship/* "branch", and it
may carry "context", "pr" and "blocked_reason".
"""

import argparse
import json
import sys
from pathlib import Path

STATUSES = ("pending", "running", "needs_input", "blocked", "done")
OUTCOMES = {"pending": "RUN", "running": "RESUME", "needs_input": "RESUME", "blocked": "BLOCKED"}
MANIFEST_KEYS = ("trunk", "stories")
STORY_KEYS = ("id", "story", "depends_on", "status")
BOOKKEEPING_KEYS = ("branch", "context", "pr", "blocked_reason")
BRANCH_PREFIX = "ship/"


class FleetError(Exception):
    """Raised when a fleet manifest violates the contract. Never swallowed."""


def decide(manifest):
    """Validate the manifest and return the decision for its first unfinished story as a dict."""
    stories = _validate(manifest)
    base = manifest["trunk"]
    for story in stories:
        if story["status"] != "done":
            return {"outcome": OUTCOMES[story["status"]], "story": story["id"], "base": base}
        base = story["branch"]
    return {"outcome": "DONE", "story": None, "base": None}


def _validate(manifest):
    if not isinstance(manifest, dict):
        raise FleetError(f"manifest must be a JSON object, got {type(manifest).__name__}")
    _check_keys(manifest, MANIFEST_KEYS, (), "manifest")
    if not _is_text(manifest["trunk"]):
        raise FleetError("trunk must be a non-empty string")
    stories = manifest["stories"]
    if not isinstance(stories, list) or not stories:
        raise FleetError("stories must be a non-empty list")
    position = _positions(stories)
    unfinished = None
    for story in stories:
        _check_story(story, position)
        if unfinished is None:
            if story["status"] != "done":
                unfinished = story
        elif story["status"] != "pending":
            raise FleetError(
                f"story {story['id']!r} is {story['status']} but the earlier story {unfinished['id']!r} is not done"
            )
    return stories


def _positions(stories):
    position = {}
    for number, story in enumerate(stories, start=1):
        if not isinstance(story, dict):
            raise FleetError(f"story {number} must be a JSON object, got {type(story).__name__}")
        _check_keys(story, STORY_KEYS, BOOKKEEPING_KEYS, f"story {number}")
        if not _is_text(story["id"]):
            raise FleetError(f"story {number}: id must be a non-empty string")
        if story["id"] in position:
            raise FleetError(f"duplicate id {story['id']!r}")
        position[story["id"]] = number
    return position


def _check_story(story, position):
    sid = story["id"]
    if not _is_text(story["story"]):
        raise FleetError(f"story {sid!r}: story must be a non-empty path")
    if not isinstance(story["depends_on"], list):
        raise FleetError(f"story {sid!r}: depends_on must be a list of story ids")
    for dep in story["depends_on"]:
        if dep == sid:
            raise FleetError(f"story {sid!r} depends on itself")
        if not isinstance(dep, str) or dep not in position:
            raise FleetError(f"story {sid!r} depends on unknown story {dep!r}")
        if position[dep] > position[sid]:
            raise FleetError(f"story {sid!r} depends on {dep!r}, which is listed after it; list stories in stack order")
    if story["status"] not in STATUSES:
        raise FleetError(f"story {sid!r}: status {story['status']!r} is not one of {', '.join(STATUSES)}")
    branch = story.get("branch")
    if story["status"] != "pending" and not (isinstance(branch, str) and branch.startswith(BRANCH_PREFIX)):
        raise FleetError(f"story {sid!r}: branch must be a {BRANCH_PREFIX}* branch once the story starts, got {branch!r}")


def _check_keys(entry, required, optional, label):
    for key in entry:
        if key not in required and key not in optional:
            raise FleetError(f"{label}: unexpected key {key!r}")
    for key in required:
        if key not in entry:
            raise FleetError(f"{label}: missing {key!r}")


def _is_text(value):
    return isinstance(value, str) and bool(value.strip())


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise FleetError(f"{path}: {exc}") from exc


def main(argv=None):
    """CLI entry point: print the decision as JSON; exit 2 on a contract violation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="the fleet manifest JSON")
    args = parser.parse_args(argv)
    try:
        result = decide(_load(args.manifest))
    except FleetError as exc:
        print(f"fleet_plan: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
