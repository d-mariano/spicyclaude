"""Tests for ship_config: config precedence and fail-loud validation."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import ship_config


def resolve(argv=(), env=None, project_file=None):
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


if __name__ == "__main__":
    unittest.main()
