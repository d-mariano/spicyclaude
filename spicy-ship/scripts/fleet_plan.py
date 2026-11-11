#!/usr/bin/env python3
"""Decide which stories of a fleet start next and which branch each stacks on.

Reads a fleet manifest, checks it, then returns RUN, WAIT, BLOCKED or DONE with
the stories to start now. A story starts once every story it depends on is
done, and stacks on the branch of its dependency, or on the trunk when it has
none. Stories that do not depend on each other run in parallel, up to
--max-parallel at a time. A blocked story strands the stories behind it and
nothing else. Contract violations exit 2.

The manifest is {"trunk": <branch>, "stories": [...]}. Each story has "id",
"story" (the path of its story file), "depends_on" (ids of stories listed
before it) and "status"; once it starts it also has its ship/* "branch", and it
may carry "context", "worktree", "pr" and "blocked_reason". A story with several
dependencies needs one of them to depend on all the others, so that one branch
holds everything it builds on.
"""

import argparse
import json
import sys
from pathlib import Path

STATUSES = ("pending", "running", "needs_input", "blocked", "done")
ACTIVE = ("running", "needs_input")
MANIFEST_KEYS = ("trunk", "stories")
STORY_KEYS = ("id", "story", "depends_on", "status")
BOOKKEEPING_KEYS = ("branch", "context", "worktree", "pr", "blocked_reason")
BRANCH_PREFIX = "ship/"


class FleetError(Exception):
    """Raised when a fleet manifest violates the contract. Never swallowed."""


def decide(manifest, *, max_parallel=2):
    """Validate the manifest and return the scheduling decision as a dict.

    start lists the stories to spawn now and active the ones already started, each with the
    branch it stacks on; blocked and stranded list the ids that cannot proceed.
    """
    if max_parallel < 1:
        raise FleetError("max-parallel must be at least 1")
    stories, tips = _validate(manifest)
    by_id = {story["id"]: story for story in stories}
    active, ready, blocked, stranded = [], [], [], []
    halted = set()
    for story in stories:
        sid, status, deps = story["id"], story["status"], story["depends_on"]
        tip = tips[sid]
        run = {"story": sid, "base": manifest["trunk"] if tip is None else by_id[tip].get("branch")}
        if status in ACTIVE:
            active.append(run)
        elif status == "blocked":
            blocked.append(sid)
            halted.add(sid)
        elif status == "pending" and halted.intersection(deps):
            stranded.append(sid)
            halted.add(sid)
        elif status == "pending" and all(by_id[dep]["status"] == "done" for dep in deps):
            ready.append(run)
    start = ready[: max(0, max_parallel - len(active))]
    if all(story["status"] == "done" for story in stories):
        outcome = "DONE"
    elif start:
        outcome = "RUN"
    elif active:
        outcome = "WAIT"
    else:
        outcome = "BLOCKED"
    return {"outcome": outcome, "start": start, "active": active, "blocked": blocked, "stranded": stranded}


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
    by_id = {story["id"]: story for story in stories}
    ancestors, tips = {}, {}
    for story in stories:
        _check_story(story, position, by_id)
        deps = story["depends_on"]
        ancestors[story["id"]] = set(deps).union(*(ancestors[dep] for dep in deps))
        tips[story["id"]] = _tip(story["id"], deps, ancestors)
    return stories, tips


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


def _check_story(story, position, by_id):
    sid, status = story["id"], story["status"]
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
            raise FleetError(f"story {sid!r} depends on {dep!r}, which is listed after it")
    if status not in STATUSES:
        raise FleetError(f"story {sid!r}: status {status!r} is not one of {', '.join(STATUSES)}")
    if status == "pending":
        return
    branch = story.get("branch")
    if not (isinstance(branch, str) and branch.startswith(BRANCH_PREFIX)):
        raise FleetError(f"story {sid!r}: branch must be a {BRANCH_PREFIX}* branch once it starts, got {branch!r}")
    for dep in story["depends_on"]:
        if by_id[dep]["status"] != "done":
            raise FleetError(f"story {sid!r} is {status} but its dependency {dep!r} is not done")


def _tip(sid, deps, ancestors):
    """Return the dependency whose branch holds every other dependency, or None without dependencies."""
    if not deps:
        return None
    for dep in deps:
        if all(other == dep or other in ancestors[dep] for other in deps):
            return dep
    listed = " and ".join(repr(dep) for dep in deps)
    raise FleetError(f"story {sid!r} depends on {listed}, which are on separate branches; make one depend on the other")


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
    parser.add_argument("--max-parallel", type=int, default=2, help="stories that may run at once")
    args = parser.parse_args(argv)
    try:
        result = decide(_load(args.manifest), max_parallel=args.max_parallel)
    except FleetError as exc:
        print(f"fleet_plan: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
