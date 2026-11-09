"""Tests for ship_config: config precedence and fail-loud validation."""

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import ship_config


ABSENT = Path("/nonexistent/spicyclaude.json")


def run_main(argv, env=None, project=None):
    """Run ship_config.main in a hermetic environment and return (exit code, stdout, stderr)."""
    with TemporaryDirectory() as tmp:
        if project is not None:
            (Path(tmp) / ".claude").mkdir()
            (Path(tmp) / ".claude" / "spicyclaude.json").write_text(json.dumps(project))
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": tmp, **(env or {})}, clear=True):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ship_config.main(argv)
    return code, out.getvalue(), err.getvalue()


def resolve(argv=(), env=None, project_file=ABSENT):
    return ship_config.resolve(list(argv), env or {}, project_file)


def resolve_project(payload, argv=(), env=None):
    """Resolve with payload written as the project file; payload may be any JSON value or raw text."""
    with TemporaryDirectory() as d:
        f = Path(d) / "spicyclaude.json"
        f.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        return resolve(argv, env, f)


def failing(fn, *args, **kwargs):
    """Call fn expecting ConfigError and return its message."""
    try:
        fn(*args, **kwargs)
    except ship_config.ConfigError as exc:
        return str(exc)
    raise AssertionError("ConfigError not raised")


class DefaultsTest(unittest.TestCase):
    def test_defaults_when_nothing_set(self):
        cfg = resolve()
        self.assertEqual(cfg["review"]["plan"], {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"})
        self.assertEqual(cfg["review"]["code"], cfg["review"]["plan"])
        self.assertEqual(cfg["questions"], {"mode": "auto", "escalate": ["irreversible"]})


class PrecedenceTest(unittest.TestCase):
    def test_project_file_beats_plugin_config(self):
        cfg = resolve_project({"review": {"default": {"max_rounds": 5}}}, ["--plugin-config", "maxReviewRounds=2"])
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 5)

    def test_env_beats_project_file(self):
        cfg = resolve_project({"review": {"default": {"min_severity": "Low"}}}, env={"SPICY_REVIEW_MIN_SEVERITY": "Critical"})
        self.assertEqual(cfg["review"]["plan"]["min_severity"], "Critical")

    def test_args_beat_env(self):
        cfg = resolve(["--max-review-rounds=1"], env={"SPICY_MAX_REVIEW_ROUNDS": "4"})
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 1)

    def test_plugin_config_beats_defaults(self):
        cfg = resolve(["--plugin-config", "minReviewSeverity=Medium", "--plugin-config", "questionMode=batch"])
        self.assertEqual(cfg["review"]["plan"]["min_severity"], "Medium")
        self.assertEqual(cfg["questions"]["mode"], "batch")

    def test_empty_plugin_config_value_is_unset(self):
        cfg = resolve(["--plugin-config", "maxReviewRounds="])
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 3)


class CrossSourcePrecedenceTest(unittest.TestCase):
    def test_argument_default_beats_project_reviewer_value(self):
        cfg = resolve_project({"review": {"plan": {"max_rounds": 1}}}, argv=["--max-review-rounds=5"])
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 5)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 5)

    def test_env_default_beats_project_reviewer_value(self):
        cfg = resolve_project({"review": {"code": {"min_severity": "Medium"}}}, env={"SPICY_REVIEW_MIN_SEVERITY": "Critical"})
        self.assertEqual(cfg["review"]["code"]["min_severity"], "Critical")

    def test_project_reviewer_value_beats_plugin_default(self):
        cfg = resolve_project({"review": {"plan": {"max_rounds": 1}}}, argv=["--plugin-config", "maxReviewRounds=4"])
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 1)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 4)

    def test_reviewer_beats_default_within_one_source(self):
        cfg = resolve(["--max-review-rounds=5", "--plan-rounds=2"])
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 2)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 5)


class PerReviewerTest(unittest.TestCase):
    def test_per_reviewer_arg_overrides_default_for_that_reviewer_only(self):
        cfg = resolve(["--plan-rounds=2", "--code-min-severity=Critical"])
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 2)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 3)
        self.assertEqual(cfg["review"]["code"]["min_severity"], "Critical")
        self.assertEqual(cfg["review"]["plan"]["min_severity"], "High")

    def test_per_reviewer_env(self):
        cfg = resolve(env={"SPICY_PLAN_MAX_ROUNDS": "1", "SPICY_CODE_MIN_SEVERITY": "Critical"})
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 1)
        self.assertEqual(cfg["review"]["code"]["min_severity"], "Critical")

    def test_project_file_per_reviewer_section(self):
        cfg = resolve_project({"review": {"plan": {"max_rounds": 1}}})
        self.assertEqual(cfg["review"]["plan"]["max_rounds"], 1)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 3)


class QuestionsTest(unittest.TestCase):
    def test_questions_mode_and_escalate_from_args(self):
        cfg = resolve(["--questions=raise", "--escalate=irreversible,external"])
        self.assertEqual(cfg["questions"], {"mode": "raise", "escalate": ["irreversible", "external"]})

    def test_escalate_none_clears_guard(self):
        cfg = resolve(["--escalate=none"])
        self.assertEqual(cfg["questions"]["escalate"], [])


class ValidationTest(unittest.TestCase):
    def test_invalid_severity_fails_loud(self):
        self.assertIn("--min-severity", failing(resolve, ["--min-severity=Nit"]))

    def test_invalid_rounds_fails_loud(self):
        self.assertIn("SPICY_MAX_REVIEW_ROUNDS", failing(resolve, env={"SPICY_MAX_REVIEW_ROUNDS": "zero"}))
        self.assertIn("at least 1", failing(resolve, ["--max-review-rounds=0"]))

    def test_invalid_mode_fails_loud(self):
        self.assertIn("--questions", failing(resolve, ["--questions=yolo"]))

    def test_unknown_arg_fails_loud(self):
        self.assertIn("--max-rounds", failing(resolve, ["--max-rounds=3"]))

    def test_flag_without_value_fails_loud(self):
        self.assertIn("--questions", failing(resolve, ["--questions"]))

    def test_plugin_config_without_value_fails_loud(self):
        self.assertIn("--plugin-config", failing(resolve, ["--plugin-config"]))

    def test_unknown_plugin_option_fails_loud(self):
        self.assertIn("bogus", failing(resolve, ["--plugin-config", "bogus=1"]))

    def test_unknown_project_key_fails_loud(self):
        self.assertIn("rounds", failing(resolve_project, {"review": {"default": {"rounds": 3}}}))

    def test_unknown_top_level_project_key_fails_loud(self):
        self.assertIn("revew", failing(resolve_project, {"revew": {}}))

    def test_unknown_review_section_fails_loud(self):
        self.assertIn("docs", failing(resolve_project, {"review": {"docs": {}}}))

    def test_unknown_questions_key_fails_loud(self):
        self.assertIn("modes", failing(resolve_project, {"questions": {"modes": "auto"}}))

    def test_invalid_json_project_file_fails_loud(self):
        self.assertIn("not valid JSON", failing(resolve_project, "{not json"))

    def test_fix_floor_above_min_severity_fails_loud(self):
        self.assertIn("fix_floor", failing(resolve, ["--min-severity=Low", "--fix-floor=High"]))



class EmptyValueTest(unittest.TestCase):
    def test_empty_flag_value_is_unset_not_cleared(self):
        cfg = resolve(["--escalate=", "--max-review-rounds="])
        self.assertEqual(cfg["questions"]["escalate"], ["irreversible"])
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 3)

    def test_empty_env_value_is_unset(self):
        cfg = resolve(env={"SPICY_REVIEW_MIN_SEVERITY": "", "SPICY_MAX_REVIEW_ROUNDS": "", "SPICY_QUESTION_ESCALATE": ""})
        self.assertEqual(cfg["review"]["plan"], {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"})
        self.assertEqual(cfg["questions"]["escalate"], ["irreversible"])

    def test_empty_project_value_is_unset(self):
        cfg = resolve_project({"review": {"default": {"min_severity": "", "max_rounds": ""}}, "questions": {"mode": "", "escalate": ""}})
        self.assertEqual(cfg["review"]["plan"], {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"})
        self.assertEqual(cfg["questions"], {"mode": "auto", "escalate": ["irreversible"]})

    def test_explicit_empty_escalate_list_in_project_file_clears_guard(self):
        cfg = resolve_project({"questions": {"escalate": []}})
        self.assertEqual(cfg["questions"]["escalate"], [])


class StrictTypesTest(unittest.TestCase):
    def test_float_rounds_fail_loud(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"default": {"max_rounds": 2.9}}}))
            with self.assertRaises(ship_config.ConfigError):
                resolve(project_file=f)

    def test_bool_rounds_fail_loud(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"default": {"max_rounds": True}}}))
            with self.assertRaises(ship_config.ConfigError):
                resolve(project_file=f)

    def test_non_object_sections_fail_loud(self):
        for payload in ({"review": [1]}, {"review": {"default": "nope"}}, {"questions": 3}, [1]):
            with TemporaryDirectory() as d:
                f = Path(d) / "spicyclaude.json"
                f.write_text(json.dumps(payload))
                with self.assertRaises(ship_config.ConfigError):
                    resolve(project_file=f)


class ProjectRootTest(unittest.TestCase):
    def test_project_file_anchored_on_claude_project_dir(self):
        with TemporaryDirectory() as d:
            (Path(d) / ".claude").mkdir()
            (Path(d) / ".claude" / "spicyclaude.json").write_text(json.dumps({"review": {"default": {"max_rounds": 1}}}))
            self.assertEqual(ship_config.project_file({"CLAUDE_PROJECT_DIR": d}), Path(d) / ".claude" / "spicyclaude.json")

    def test_project_file_falls_back_to_git_toplevel(self):
        with TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            nested = Path(d) / "pkg" / "api"
            nested.mkdir(parents=True)
            self.assertEqual(ship_config.project_file({}, cwd=nested).resolve(), (Path(d) / ".claude" / "spicyclaude.json").resolve())

    def test_no_project_root_fails_loud(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ship_config.ConfigError):
                ship_config.project_file({}, cwd=Path(d))


class ProjectFileErrorsTest(unittest.TestCase):
    def test_directory_at_project_file_path_fails_loud(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ship_config.ConfigError):
                resolve(project_file=Path(d))

    def test_dangling_symlink_fails_loud(self):
        with TemporaryDirectory() as d:
            link = Path(d) / "spicyclaude.json"
            link.symlink_to(Path(d) / "missing.json")
            with self.assertRaises(ship_config.ConfigError):
                resolve(project_file=link)

    def test_unreadable_project_file_fails_loud(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text("{}")
            with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
                with self.assertRaises(ship_config.ConfigError):
                    resolve(project_file=f)

    def test_missing_git_binary_fails_loud(self):
        with patch.object(ship_config.subprocess, "run", side_effect=FileNotFoundError("git")):
            with self.assertRaises(ship_config.ConfigError):
                ship_config.project_file({})

class GateFlagsTest(unittest.TestCase):
    DEFAULT_LINE = "--max-rounds 3 --min-severity High --fix-floor Medium"
    EXPECTED_DEFAULTS = {
        "review": {
            "plan": {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"},
            "code": {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"},
        },
        "questions": {"mode": "auto", "escalate": ["irreversible"]},
    }

    def test_plan_prints_one_line_of_gate_flags(self):
        self.assertEqual(run_main(["--gate-flags=plan"]), (0, self.DEFAULT_LINE + "\n", ""))

    def test_code_reads_the_code_section(self):
        code_line = "--max-rounds 5 --min-severity High --fix-floor Medium\n"
        self.assertEqual(run_main(["--code-rounds=5", "--gate-flags=code"]), (0, code_line, ""))
        self.assertEqual(run_main(["--code-rounds=5", "--gate-flags=plan"]), (0, self.DEFAULT_LINE + "\n", ""))

    def test_cli_flag_applies(self):
        line = "--max-rounds 2 --min-severity High --fix-floor Medium\n"
        self.assertEqual(run_main(["--plan-rounds=2", "--gate-flags=plan"]), (0, line, ""))

    def test_env_applies(self):
        line = "--max-rounds 3 --min-severity Critical --fix-floor Medium\n"
        self.assertEqual(run_main(["--gate-flags=code"], env={"SPICY_CODE_MIN_SEVERITY": "Critical"}), (0, line, ""))

    def test_project_file_applies(self):
        line = "--max-rounds 1 --min-severity High --fix-floor Medium\n"
        project = {"review": {"plan": {"max_rounds": 1}}}
        self.assertEqual(run_main(["--gate-flags=plan"], project=project), (0, line, ""))

    def test_plugin_config_applies(self):
        line = "--max-rounds 4 --min-severity High --fix-floor Medium\n"
        argv = ["--plugin-config", "maxReviewRounds=4", "--gate-flags=plan"]
        self.assertEqual(run_main(argv), (0, line, ""))

    def test_unknown_reviewer_fails_loud(self):
        for flag in ("--gate-flags=docs", "--gate-flags=Plan", "--gate-flags=", "--gate-flags"):
            with self.subTest(flag=flag):
                code, out, err = run_main([flag])
                self.assertEqual(code, 1)
                self.assertEqual(out, "")
                self.assertIn("--gate-flags must be one of plan, code", err)

    def test_invalid_config_with_gate_flags_fails_loud(self):
        code, out, err = run_main(["--gate-flags=plan", "--min-severity=Nit"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("severity must be one of", err)

    def test_cli_entry_point_defaults_to_sys_argv(self):
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, ship_config.__file__, "--gate-flags=plan"],
                env={"CLAUDE_PROJECT_DIR": tmp},
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.DEFAULT_LINE + "\n")

    def test_without_gate_flags_prints_full_json(self):
        code, out, err = run_main([])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, json.dumps(self.EXPECTED_DEFAULTS, indent=2) + "\n")



class GateFlagsFromTest(unittest.TestCase):
    FROZEN = {
        "review": {
            "plan": {"max_rounds": 2, "min_severity": "Medium", "fix_floor": "Low"},
            "code": {"max_rounds": 4, "min_severity": "Critical", "fix_floor": "Critical"},
        },
        "questions": {"mode": "raise", "escalate": []},
    }

    def frozen(self, tmp, payload=None):
        path = Path(tmp) / "ship-config.json"
        path.write_text(json.dumps(self.FROZEN if payload is None else payload))
        return str(path)

    def test_from_renders_the_frozen_section_and_ignores_live_sources(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main(["--gate-flags=plan", f"--from={self.frozen(tmp)}"], env={"SPICY_PLAN_MAX_ROUNDS": "9"})
        self.assertEqual((code, out, err), (0, "--max-rounds 2 --min-severity Medium --fix-floor Low\n", ""))

    def test_from_reads_the_code_section_too(self):
        with TemporaryDirectory() as tmp:
            code, out, _ = run_main(["--gate-flags=code", f"--from={self.frozen(tmp)}"])
        self.assertEqual((code, out), (0, "--max-rounds 4 --min-severity Critical --fix-floor Critical\n"))

    def test_from_rejects_other_flags(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main(["--gate-flags=plan", f"--from={self.frozen(tmp)}", "--plan-rounds=7"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("--plan-rounds", err)

    def test_from_without_gate_flags_fails_loud(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([f"--from={self.frozen(tmp)}"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("only applies together with --gate-flags", err)

    def test_from_missing_file_fails_loud(self):
        code, out, err = run_main(["--gate-flags=plan", "--from=/nonexistent/ship-config.json"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("/nonexistent/ship-config.json", err)

    def test_from_file_missing_section_fails_loud(self):
        with TemporaryDirectory() as tmp:
            path = self.frozen(tmp, {"review": {"plan": self.FROZEN["review"]["plan"]}, "questions": {}})
            code, out, err = run_main(["--gate-flags=code", f"--from={path}"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("review.code", err)

    def test_from_file_with_invalid_value_fails_loud(self):
        with TemporaryDirectory() as tmp:
            bad = json.loads(json.dumps(self.FROZEN))
            bad["review"]["plan"]["max_rounds"] = "many"
            code, out, err = run_main(["--gate-flags=plan", f"--from={self.frozen(tmp, bad)}"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("max_rounds", err)

    def test_empty_from_fails_loud(self):
        code, out, err = run_main(["--gate-flags=plan", "--from="])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("--from needs the path", err)

    def test_from_malformed_files_fail_loud(self):
        cases = {
            "{not json": "cannot read",
            "[1, 2]": "has no review.plan section",
            '{"review": {"plan": []}}': "has no review.plan section",
            '{"review": {"plan": {"max_rounds": 2}}}': "is missing ['min_severity', 'fix_floor']",
        }
        for payload, fragment in cases.items():
            with self.subTest(payload=payload), TemporaryDirectory() as tmp:
                path = Path(tmp) / "ship-config.json"
                path.write_text(payload)
                code, out, err = run_main(["--gate-flags=plan", f"--from={path}"])
                self.assertEqual((code, out), (1, ""))
                self.assertIn(fragment, err)

    def test_printed_line_is_accepted_by_review_gate(self):
        import review_gate
        flags = run_main(["--gate-flags=plan"])[1].split()
        with TemporaryDirectory() as tmp:
            findings = Path(tmp) / "r1.json"
            findings.write_text(json.dumps({"reviewer": "r", "target": "t", "round": 1, "prior_findings": [], "findings": []}))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(review_gate.main([str(findings), *flags]), 0)


if __name__ == "__main__":
    unittest.main()
