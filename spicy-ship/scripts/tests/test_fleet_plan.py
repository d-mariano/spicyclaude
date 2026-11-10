"""Tests for fleet_plan: manifest checks and the next-story decision."""

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import fleet_plan
from fleet_plan import FleetError, decide


def story(sid, status="pending", deps=(), branch=None, **extra):
    entry = {"id": sid, "story": f"stories/{sid}.md", "depends_on": list(deps), "status": status, **extra}
    if branch is None and status != "pending":
        branch = f"ship/{sid.lower()}"
    if branch is not None:
        entry["branch"] = branch
    return entry


def manifest(*stories, trunk="main"):
    return {"trunk": trunk, "stories": list(stories)}


def failing(payload):
    """Call decide expecting FleetError and return its message."""
    try:
        decide(payload)
    except FleetError as exc:
        return str(exc)
    raise AssertionError("expected FleetError")


def run_main(argv):
    """Run fleet_plan.main and return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fleet_plan.main(argv)
    return code, out.getvalue(), err.getvalue()


class DecisionTest(unittest.TestCase):
    def test_first_story_runs_on_the_trunk(self):
        decision = decide(manifest(story("S1"), story("S2", deps=["S1"]), trunk="develop"))
        self.assertEqual(decision, {"outcome": "RUN", "story": "S1", "base": "develop"})

    def test_next_story_stacks_on_the_previous_branch(self):
        decision = decide(manifest(story("S1", "done", branch="ship/001-a"), story("S2"), story("S3")))
        self.assertEqual(decision, {"outcome": "RUN", "story": "S2", "base": "ship/001-a"})

    def test_independent_story_still_stacks_on_the_previous_branch(self):
        stories = [story("S1", "done"), story("S2", "done", branch="ship/002-b"), story("S3", deps=["S1"])]
        decision = decide(manifest(*stories))
        self.assertEqual(decision, {"outcome": "RUN", "story": "S3", "base": "ship/002-b"})

    def test_all_done_is_done(self):
        decision = decide(manifest(story("S1", "done"), story("S2", "done")))
        self.assertEqual(decision, {"outcome": "DONE", "story": None, "base": None})

    def test_started_story_is_resumed_with_its_base(self):
        for status in ("running", "needs_input"):
            decision = decide(manifest(story("S1", "done", branch="ship/001-a"), story("S2", status), story("S3")))
            self.assertEqual(decision, {"outcome": "RESUME", "story": "S2", "base": "ship/001-a"})

    def test_blocked_story_stops_the_fleet(self):
        decision = decide(manifest(story("S1", "done"), story("S2", "blocked"), story("S3")))
        self.assertEqual(decision, {"outcome": "BLOCKED", "story": "S2", "base": "ship/s1"})

    def test_optional_bookkeeping_keys_are_accepted(self):
        done = story("S1", "done", context="context/001-a", pr="https://example.test/pr/1", blocked_reason=None)
        self.assertEqual(decide(manifest(done, story("S2")))["story"], "S2")


class ManifestShapeTest(unittest.TestCase):
    def test_top_level_must_be_an_object_with_exactly_trunk_and_stories(self):
        self.assertIn("must be a JSON object", failing([story("S1")]))
        self.assertIn("missing 'trunk'", failing({"stories": [story("S1")]}))
        self.assertIn("missing 'stories'", failing({"trunk": "main"}))
        self.assertIn("unexpected key 'epic'", failing({**manifest(story("S1")), "epic": "x"}))

    def test_trunk_must_be_a_non_empty_string(self):
        self.assertIn("trunk", failing(manifest(story("S1"), trunk="")))
        self.assertIn("trunk", failing(manifest(story("S1"), trunk=3)))

    def test_stories_must_be_a_non_empty_list_of_objects(self):
        self.assertIn("non-empty list", failing({"trunk": "main", "stories": []}))
        self.assertIn("non-empty list", failing({"trunk": "main", "stories": {"S1": {}}}))
        self.assertIn("story 2 must be a JSON object", failing(manifest(story("S1"), "S2")))

    def test_story_keys_are_exact(self):
        self.assertIn("story 1: unexpected key 'title'", failing(manifest(story("S1", title="x"))))
        for key in ("id", "story", "depends_on", "status"):
            entry = story("S1")
            del entry[key]
            self.assertIn(f"story 1: missing {key!r}", failing(manifest(entry)))

    def test_id_and_story_path_must_be_non_empty_strings(self):
        self.assertIn("story 1: id", failing(manifest({**story("S1"), "id": " "})))
        self.assertIn("story 1: id", failing(manifest({**story("S1"), "id": 1})))
        self.assertIn("story 'S1': story", failing(manifest({**story("S1"), "story": ""})))
        self.assertIn("story 'S1': story", failing(manifest({**story("S1"), "story": None})))

    def test_duplicate_id_fails_loud(self):
        self.assertIn("duplicate id 'S1'", failing(manifest(story("S1"), story("S1"))))

    def test_status_must_be_known(self):
        self.assertIn("story 'S1': status 'finished'", failing(manifest(story("S1", "finished", branch="ship/a"))))


class DependencyTest(unittest.TestCase):
    def test_depends_on_must_be_a_list(self):
        self.assertIn("story 'S2': depends_on", failing(manifest(story("S1"), {**story("S2"), "depends_on": "S1"})))

    def test_unknown_dependency_fails_loud(self):
        self.assertIn("story 'S1' depends on unknown story 'S9'", failing(manifest(story("S1", deps=["S9"]))))

    def test_self_dependency_fails_loud(self):
        self.assertIn("story 'S1' depends on itself", failing(manifest(story("S1", deps=["S1"]))))

    def test_dependency_listed_later_fails_loud(self):
        message = failing(manifest(story("S1", deps=["S2"]), story("S2")))
        self.assertIn("story 'S1' depends on 'S2', which is listed after it", message)


class ProgressTest(unittest.TestCase):
    def test_started_story_needs_a_ship_branch(self):
        for status in ("running", "needs_input", "blocked", "done"):
            entry = story("S1", status)
            del entry["branch"]
            self.assertIn("story 'S1': branch", failing(manifest(entry)))
        self.assertIn("ship/", failing(manifest(story("S1", "done", branch="main"))))
        self.assertIn("story 'S1': branch", failing(manifest(story("S1", "done", branch=7))))

    def test_story_started_before_an_earlier_one_finished_fails_loud(self):
        for status in ("running", "needs_input", "blocked", "done"):
            message = failing(manifest(story("S1"), story("S2", status)))
            self.assertIn(f"story 'S2' is {status} but the earlier story 'S1' is not done", message)

    def test_two_unfinished_started_stories_fail_loud(self):
        message = failing(manifest(story("S1", "blocked"), story("S2", "running")))
        self.assertIn("story 'S2' is running but the earlier story 'S1' is not done", message)


class MainTest(unittest.TestCase):
    def write(self, tmp, payload):
        path = Path(tmp) / "fleet.json"
        path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        return str(path)

    def test_prints_the_decision_as_json(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([self.write(tmp, manifest(story("S1")))])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(out), {"outcome": "RUN", "story": "S1", "base": "main"})

    def test_contract_violation_exits_two_with_prefix(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([self.write(tmp, {})])
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("fleet_plan: "))

    def test_missing_and_invalid_files_exit_two_naming_the_file(self):
        code, _, err = run_main(["/nonexistent/fleet.json"])
        self.assertEqual(code, 2)
        self.assertIn("/nonexistent/fleet.json", err)
        with TemporaryDirectory() as tmp:
            invalid = self.write(tmp, "{not json")
            code, _, err = run_main([invalid])
        self.assertEqual(code, 2)
        self.assertIn(f"{invalid}: Expecting", err)


if __name__ == "__main__":
    unittest.main()
