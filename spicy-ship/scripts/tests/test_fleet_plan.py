"""Tests for fleet_plan: manifest checks and the scheduling decision."""

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


def run(sid, base):
    return {"story": sid, "base": base}


def decision(outcome, start=(), active=(), blocked=(), stranded=()):
    return {
        "outcome": outcome,
        "start": list(start),
        "active": list(active),
        "blocked": list(blocked),
        "stranded": list(stranded),
    }


def failing(payload, **options):
    """Call decide expecting FleetError and return its message."""
    try:
        decide(payload, **options)
    except FleetError as exc:
        return str(exc)
    raise AssertionError("expected FleetError")


def run_main(argv):
    """Run fleet_plan.main and return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fleet_plan.main(argv)
    return code, out.getvalue(), err.getvalue()


class StartTest(unittest.TestCase):
    def test_independent_stories_start_together_on_the_trunk(self):
        stories = [story("S1"), story("S2"), story("S3", deps=["S1"])]
        result = decide(manifest(*stories, trunk="develop"), max_parallel=2)
        self.assertEqual(result, decision("RUN", start=[run("S1", "develop"), run("S2", "develop")]))

    def test_parallel_cap_limits_how_many_start(self):
        result = decide(manifest(story("S1"), story("S2")), max_parallel=1)
        self.assertEqual(result, decision("RUN", start=[run("S1", "main")]))

    def test_active_stories_count_toward_the_cap(self):
        stories = [story("S1", "running"), story("S2"), story("S3")]
        result = decide(manifest(*stories), max_parallel=2)
        self.assertEqual(result, decision("RUN", start=[run("S2", "main")], active=[run("S1", "main")]))
        result = decide(manifest(*stories), max_parallel=1)
        self.assertEqual(result, decision("WAIT", active=[run("S1", "main")]))

    def test_dependent_story_starts_on_its_dependency_branch(self):
        stories = [story("S1", "done", branch="ship/001-a"), story("S2", deps=["S1"]), story("S3")]
        result = decide(manifest(*stories), max_parallel=3)
        self.assertEqual(result, decision("RUN", start=[run("S2", "ship/001-a"), run("S3", "main")]))

    def test_dependent_story_waits_for_an_active_dependency(self):
        for status in ("running", "needs_input"):
            result = decide(manifest(story("S1", status), story("S2", deps=["S1"])), max_parallel=2)
            self.assertEqual(result, decision("WAIT", active=[run("S1", "main")]))

    def test_story_with_chained_dependencies_starts_on_the_tip(self):
        for deps in (["S1", "S2"], ["S2", "S1"]):
            done = [story("S1", "done"), story("S2", "done", deps=["S1"], branch="ship/002-b")]
            result = decide(manifest(*done, story("S3", deps=deps)))
            self.assertEqual(result["start"], [run("S3", "ship/002-b")])

    def test_more_active_stories_than_the_cap_start_nothing(self):
        stories = [story("S1", "running"), story("S2", "running"), story("S3"), story("S4"), story("S5")]
        self.assertEqual(decide(manifest(*stories), max_parallel=1)["start"], [])

    def test_tip_is_found_through_a_longer_chain(self):
        chain = [story("S1", "done"), story("S2", "done", deps=["S1"]), story("S3", "done", deps=["S2"])]
        result = decide(manifest(*chain, story("S4", deps=["S1", "S3"])))
        self.assertEqual(result["start"], [run("S4", "ship/s3")])

    def test_active_story_reports_its_base(self):
        stories = [story("S1", "done", branch="ship/001-a"), story("S2", "needs_input", deps=["S1"])]
        self.assertEqual(decide(manifest(*stories)), decision("WAIT", active=[run("S2", "ship/001-a")]))

    def test_optional_bookkeeping_keys_are_accepted(self):
        kept = {"context": "context/001-a", "worktree": "/w/1", "pr": "https://example.test/pr/1", "blocked_reason": None}
        done = story("S1", "done", **kept)
        self.assertEqual(decide(manifest(done, story("S2")))["start"], [run("S2", "main")])


class StopTest(unittest.TestCase):
    def test_all_done_is_done(self):
        self.assertEqual(decide(manifest(story("S1", "done"), story("S2", "done"))), decision("DONE"))

    def test_blocked_story_strands_its_dependents_and_spares_the_rest(self):
        stories = [story("S1", "blocked"), story("S2", deps=["S1"]), story("S3", deps=["S2"]), story("S4")]
        result = decide(manifest(*stories), max_parallel=4)
        self.assertEqual(result, decision("RUN", start=[run("S4", "main")], blocked=["S1"], stranded=["S2", "S3"]))

    def test_nothing_left_to_run_behind_a_blocked_story_is_blocked(self):
        stories = [story("S1", "done"), story("S2", "blocked", deps=["S1"]), story("S3", deps=["S2"])]
        self.assertEqual(decide(manifest(*stories)), decision("BLOCKED", blocked=["S2"], stranded=["S3"]))

    def test_active_story_beside_a_blocked_one_is_waited_for(self):
        stories = [story("S1", "blocked"), story("S2", "running")]
        self.assertEqual(decide(manifest(*stories)), decision("WAIT", active=[run("S2", "main")], blocked=["S1"]))


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

    def test_parallel_cap_must_be_at_least_one(self):
        self.assertIn("max-parallel", failing(manifest(story("S1")), max_parallel=0))


class DependencyTest(unittest.TestCase):
    def test_depends_on_must_be_a_list(self):
        self.assertIn("story 'S2': depends_on", failing(manifest(story("S1"), {**story("S2"), "depends_on": "S1"})))

    def test_unknown_dependency_fails_loud(self):
        self.assertIn("story 'S1' depends on unknown story 'S9'", failing(manifest(story("S1", deps=["S9"]))))
        self.assertIn("story 'S1' depends on unknown story ['S9']", failing(manifest(story("S1", deps=[["S9"]]))))

    def test_self_dependency_fails_loud(self):
        self.assertIn("story 'S1' depends on itself", failing(manifest(story("S1", deps=["S1"]))))

    def test_dependency_listed_later_fails_loud(self):
        message = failing(manifest(story("S1", deps=["S2"]), story("S2")))
        self.assertIn("story 'S1' depends on 'S2', which is listed after it", message)

    def test_dependencies_on_separate_branches_fail_loud(self):
        message = failing(manifest(story("S1"), story("S2"), story("S3", deps=["S1", "S2"])))
        self.assertIn("story 'S3' depends on 'S1' and 'S2', which are on separate branches", message)
        siblings = [story("S1"), story("S2", deps=["S1"]), story("S3", deps=["S1"]), story("S4", deps=["S2", "S3"])]
        self.assertIn("story 'S4' depends on 'S2' and 'S3'", failing(manifest(*siblings)))


class ProgressTest(unittest.TestCase):
    def test_started_story_needs_a_ship_branch(self):
        for status in ("running", "needs_input", "blocked", "done"):
            entry = story("S1", status)
            del entry["branch"]
            self.assertIn("story 'S1': branch", failing(manifest(entry)))
        self.assertIn("ship/", failing(manifest(story("S1", "done", branch="main"))))
        self.assertIn("story 'S1': branch", failing(manifest(story("S1", "done", branch=7))))

    def test_story_started_before_its_dependency_finished_fails_loud(self):
        for status in ("running", "needs_input", "blocked", "done"):
            for dep_status in ("pending", "running", "needs_input", "blocked"):
                message = failing(manifest(story("S1", dep_status), story("S2", status, deps=["S1"])))
                self.assertIn(f"story 'S2' is {status} but its dependency 'S1' is not done", message)


class MainTest(unittest.TestCase):
    def write(self, tmp, payload):
        path = Path(tmp) / "fleet.json"
        path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        return str(path)

    def test_prints_the_decision_as_json_with_the_default_cap(self):
        stories = [story("S1"), story("S2"), story("S3")]
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([self.write(tmp, manifest(*stories))])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(out), decision("RUN", start=[run("S1", "main"), run("S2", "main")]))

    def test_max_parallel_reaches_the_decision(self):
        stories = [story("S1"), story("S2"), story("S3")]
        with TemporaryDirectory() as tmp:
            _, out, _ = run_main([self.write(tmp, manifest(*stories)), "--max-parallel", "3"])
        self.assertEqual(len(json.loads(out)["start"]), 3)

    def test_contract_violation_exits_two_with_prefix(self):
        with TemporaryDirectory() as tmp:
            path = self.write(tmp, manifest(story("S1")))
            for argv in ([self.write(tmp, {})], [path, "--max-parallel", "0"]):
                code, out, err = run_main(argv)
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
