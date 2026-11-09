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


class DefaultsTest(unittest.TestCase):
    def test_defaults_when_nothing_set(self):
        cfg = resolve()
        self.assertEqual(cfg["review"]["plan"], {"max_rounds": 3, "min_severity": "High", "fix_floor": "Medium"})
        self.assertEqual(cfg["review"]["code"], cfg["review"]["plan"])
        self.assertEqual(cfg["questions"], {"mode": "auto", "escalate": ["irreversible"]})


class PrecedenceTest(unittest.TestCase):
    def test_project_file_beats_plugin_config(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"default": {"max_rounds": 5}}}))
            cfg = resolve(["--plugin-config", "maxReviewRounds=2"], project_file=f)
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 5)

    def test_env_beats_project_file(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"default": {"min_severity": "Low"}}}))
            cfg = resolve(env={"SPICY_REVIEW_MIN_SEVERITY": "Critical"}, project_file=f)
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
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"plan": {"max_rounds": 1}}}))
            cfg = resolve(project_file=f)
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
        with self.assertRaises(ship_config.ConfigError):
            resolve(["--min-severity=Nit"])

    def test_invalid_rounds_fails_loud(self):
        with self.assertRaises(ship_config.ConfigError):
            resolve(env={"SPICY_MAX_REVIEW_ROUNDS": "zero"})
        with self.assertRaises(ship_config.ConfigError):
            resolve(["--max-review-rounds=0"])

    def test_invalid_mode_fails_loud(self):
        with self.assertRaises(ship_config.ConfigError):
            resolve(["--questions=yolo"])

    def test_unknown_arg_fails_loud(self):
        with self.assertRaises(ship_config.ConfigError):
            resolve(["--max-rounds=3"])

    def test_unknown_project_key_fails_loud(self):
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text(json.dumps({"review": {"default": {"rounds": 3}}}))
            with self.assertRaises(ship_config.ConfigError):
                resolve(project_file=f)

    def test_fix_floor_above_min_severity_fails_loud(self):
        with self.assertRaises(ship_config.ConfigError):
            resolve(["--min-severity=Low", "--fix-floor=High"])



class EmptyValueTest(unittest.TestCase):
    def test_empty_flag_value_is_unset_not_cleared(self):
        cfg = resolve(["--escalate=", "--max-review-rounds="])
        self.assertEqual(cfg["questions"]["escalate"], ["irreversible"])
        self.assertEqual(cfg["review"]["code"]["max_rounds"], 3)


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
        import subprocess
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
        from unittest.mock import patch
        with TemporaryDirectory() as d:
            f = Path(d) / "spicyclaude.json"
            f.write_text("{}")
            with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
                with self.assertRaises(ship_config.ConfigError):
                    resolve(project_file=f)

    def test_missing_git_binary_fails_loud(self):
        from unittest.mock import patch
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


if __name__ == "__main__":
    unittest.main()
