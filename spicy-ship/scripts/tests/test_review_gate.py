"""Tests for review_gate: schema checks and loop decisions."""

import unittest

import review_gate
from review_gate import GateError


def finding(fid, severity="High", confidence=90, title="Null deref", location="src/a.py:10", category="correctness"):
    return {
        "id": fid,
        "title": title,
        "severity": severity,
        "confidence": confidence,
        "location": location,
        "category": category,
        "problem": "p",
        "fix": "f",
    }


def report(round_no, findings, prior=(), reviewer="code-reviewer"):
    return {
        "reviewer": reviewer,
        "target": "src",
        "round": round_no,
        "verdict": "CHANGES_REQUESTED" if findings else "PASS",
        "prior_findings": list(prior),
        "findings": findings,
    }


def decide(current, prior=None, max_rounds=3, min_severity="High", fix_floor="Medium"):
    return review_gate.decide(current, prior, max_rounds=max_rounds, min_severity=min_severity, fix_floor=fix_floor)


class OutcomeTest(unittest.TestCase):
    def test_pass_when_nothing_at_or_above_floor(self):
        result = decide(report(1, [finding("F1", "Medium"), finding("F2", "Low")]))
        self.assertEqual(result["outcome"], "PASS")
        self.assertEqual(result["blocking"], [])
        self.assertEqual(result["fixable"], ["F1"])

    def test_continue_when_blocking_and_rounds_remain(self):
        result = decide(report(1, [finding("F1", "High")]))
        self.assertEqual(result["outcome"], "CONTINUE")
        self.assertEqual(result["blocking"], ["F1"])

    def test_exhausted_at_max_round(self):
        result = decide(report(3, [finding("F1", "High")]))
        self.assertEqual(result["outcome"], "EXHAUSTED")
        self.assertFalse(result["critical"])

    def test_exhausted_with_critical_is_flagged(self):
        result = decide(report(3, [finding("F1", "Critical")]))
        self.assertEqual(result["outcome"], "EXHAUSTED")
        self.assertTrue(result["critical"])

    def test_low_confidence_findings_are_dropped_before_gating(self):
        result = decide(report(1, [finding("F1", "Critical", confidence=79)]))
        self.assertEqual(result["outcome"], "PASS")
        self.assertEqual(result["dropped_low_confidence"], ["F1"])

    def test_min_severity_floor_is_configurable(self):
        result = decide(report(1, [finding("F1", "Medium")]), min_severity="Medium")
        self.assertEqual(result["outcome"], "CONTINUE")

    def test_fix_floor_lists_everything_at_or_above_it(self):
        result = decide(report(1, [finding("F1", "High"), finding("F2", "Medium"), finding("F3", "Low")]))
        self.assertEqual(result["fixable"], ["F1", "F2"])


class StallTest(unittest.TestCase):
    def test_stalled_when_blocking_set_repeats_prior_round(self):
        prior = report(1, [finding("F1", "High", location="src/a.py:10")])
        current = report(2, [finding("F1", "High", location="src/a.py:14")], prior=[{"id": "F1", "status": "unresolved"}])
        result = decide(current, prior)
        self.assertEqual(result["outcome"], "STALLED")

    def test_not_stalled_when_blocking_set_changes(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F2", "High", title="Race on write", location="src/b.py:3")], prior=[{"id": "F1", "status": "resolved"}])
        self.assertEqual(decide(current, prior)["outcome"], "CONTINUE")

    def test_fingerprint_ignores_line_numbers_and_case(self):
        a = review_gate.fingerprint(finding("F1", title="Null Deref", location="src/a.py:10"))
        b = review_gate.fingerprint(finding("F9", title="null  deref", location="src/a.py:99"))
        self.assertEqual(a, b)


class PriorFindingsTest(unittest.TestCase):
    def test_unresolved_prior_must_reappear_in_findings(self):
        current = report(2, [], prior=[{"id": "F1", "status": "unresolved"}])
        with self.assertRaises(GateError):
            decide(current)

    def test_regressed_prior_counts_as_blocking_when_relisted(self):
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "regressed"}])
        self.assertEqual(decide(current)["blocking"], ["F1"])


class SchemaTest(unittest.TestCase):
    def test_invalid_severity_fails_loud(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1", "nit")]))

    def test_missing_required_field_fails_loud(self):
        bad = finding("F1")
        del bad["fix"]
        with self.assertRaises(GateError):
            decide(report(1, [bad]))

    def test_confidence_out_of_range_fails_loud(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1", confidence=101)]))

    def test_round_mismatch_with_prior_fails_loud(self):
        with self.assertRaises(GateError):
            decide(report(3, [finding("F1")]), report(1, []))

    def test_round_above_max_fails_loud(self):
        with self.assertRaises(GateError):
            decide(report(4, [finding("F1")]))

    def test_duplicate_ids_fail_loud(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1"), finding("F1")]))

    def test_verdict_must_match_findings(self):
        bad = report(1, [finding("F1")])
        bad["verdict"] = "PASS"
        with self.assertRaises(GateError):
            decide(bad)


if __name__ == "__main__":
    unittest.main()
