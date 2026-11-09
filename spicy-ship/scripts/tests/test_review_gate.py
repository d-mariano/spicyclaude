"""Tests for review_gate: schema checks and loop decisions."""

import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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
        "prior_findings": list(prior),
        "findings": findings,
    }


def rejected(*ids):
    return [{"id": i, "resolution": "rejected", "note": "disagree"} for i in ids]


def fixed(*ids):
    return [{"id": i, "resolution": "fixed", "note": "done"} for i in ids]


def all_rejected(prior):
    """A fixes file in which the fixer rejected every finding of the prior round."""
    return rejected(*[f["id"] for f in prior["findings"]])


def decide(current, prior=None, fixes=None, max_rounds=3, min_severity="High", fix_floor="Medium"):
    return review_gate.decide(current, prior, fixes, max_rounds=max_rounds, min_severity=min_severity, fix_floor=fix_floor)


def run_main(argv):
    """Run review_gate.main and return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = review_gate.main(argv)
    return code, out.getvalue(), err.getvalue()


def failing(*args, **kwargs):
    """Call decide expecting GateError and return its message."""
    try:
        decide(*args, **kwargs)
    except GateError as exc:
        return str(exc)
    raise AssertionError("GateError not raised")


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
        prior = report(2, [finding("F1", "High", location="src/a.py:3")], prior=[{"id": "F1", "status": "unresolved"}])
        result = decide(report(3, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}]), prior, all_rejected(prior))
        self.assertEqual(result["outcome"], "EXHAUSTED")
        self.assertFalse(result["critical"])

    def test_exhausted_with_critical_is_flagged(self):
        prior = report(2, [finding("F1", "Critical", location="src/a.py:3")], prior=[{"id": "F1", "status": "unresolved"}])
        result = decide(report(3, [finding("F1", "Critical")], prior=[{"id": "F1", "status": "unresolved"}]), prior, all_rejected(prior))
        self.assertEqual(result["outcome"], "EXHAUSTED")
        self.assertTrue(result["critical"])

    def test_exhausted_beats_stalled(self):
        prior = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        result = decide(report(3, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}]), prior, all_rejected(prior))
        self.assertEqual(result["outcome"], "EXHAUSTED")

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
    def test_not_stalled_when_blocking_set_changes(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F2", "High", title="Race on write", location="src/b.py:3")], prior=[{"id": "F1", "status": "resolved"}])
        self.assertEqual(decide(current, prior, all_rejected(prior))["outcome"], "CONTINUE")

    def test_fingerprint_ignores_line_numbers_and_case(self):
        a = review_gate.fingerprint(finding("F1", title="Null Deref", location="src/a.py:10"))
        b = review_gate.fingerprint(finding("F9", title="null  deref", location="src/a.py:99"))
        self.assertEqual(a, b)


class PriorFindingsTest(unittest.TestCase):
    def test_unresolved_prior_must_reappear_in_findings(self):
        prior = report(1, [finding("F1")])
        current = report(2, [], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertIn("not re-listed", failing(current, prior, rejected("F1")))

    def test_regressed_prior_counts_as_blocking_when_relisted(self):
        prior = report(1, [finding("F1", "Medium")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "regressed"}])
        self.assertEqual(decide(current, prior, all_rejected(prior))["blocking"], ["F1"])


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
        prior = report(3, [finding("F1")], prior=[{"id": "F1", "status": "unresolved"}])
        current = report(4, [finding("F1")], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertIn("exceeds max_rounds", failing(current, prior, rejected("F1")))

    def test_duplicate_ids_fail_loud(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1"), finding("F1")]))




class PriorReconciliationTest(unittest.TestCase):
    def test_round_two_without_prior_fails_loud(self):
        with self.assertRaises(GateError):
            decide(report(2, [finding("F1")]))

    def test_prior_finding_without_status_fails_loud(self):
        prior = report(1, [finding("F1"), finding("F2", title="Race on write", location="src/b.py:3")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, all_rejected(prior))

    def test_resolved_prior_still_listed_fails_loud(self):
        prior = report(1, [finding("F1")])
        current = report(2, [finding("F1")], prior=[{"id": "F1", "status": "resolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, all_rejected(prior))

    def test_phantom_prior_id_fails_loud(self):
        prior = report(1, [finding("F1")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}, {"id": "F7", "status": "resolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, all_rejected(prior))

    def test_all_priors_resolved_passes(self):
        prior = report(1, [finding("F1")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}])
        self.assertEqual(decide(current, prior, all_rejected(prior))["outcome"], "PASS")


class FindingShapeTest(unittest.TestCase):
    def test_id_must_match_pattern(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("bogus-id")]))

    def test_category_must_be_in_enum(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1", category="vibes")]))

    def test_location_must_be_path_with_optional_line_range(self):
        with self.assertRaises(GateError):
            decide(report(1, [finding("F1", location="C:\\x\\a.py:3:4")]))
        self.assertEqual(decide(report(1, [finding("F1", location="src/a.py:3-9")]))["outcome"], "CONTINUE")
        self.assertEqual(decide(report(1, [finding("F1", location="src/a.py")]))["outcome"], "CONTINUE")


class StallByIdTest(unittest.TestCase):
    def test_stalled_when_same_id_is_reraised_with_reworded_title(self):
        prior = report(1, [finding("F1", "High", title="Refresh token stored in plaintext")])
        current = report(2, [finding("F1", "High", title="Plaintext refresh token persisted")], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, all_rejected(prior))["outcome"], "STALLED")

    def test_stalled_when_renumbered_but_same_fingerprint(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F2", "High", location="src/a.py:40")], prior=[{"id": "F1", "status": "resolved"}])
        self.assertEqual(decide(current, prior, all_rejected(prior))["outcome"], "STALLED")

    def test_remaining_rejected_finding_stalls_even_after_other_was_fixed(self):
        prior = report(1, [finding("F1", "High"), finding("F2", "High", title="Race on write", location="src/b.py:3")])
        current = report(2, [finding("F2", "High", title="Race on write", location="src/b.py:3")], prior=[{"id": "F1", "status": "resolved"}, {"id": "F2", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, fixed("F1") + rejected("F2"))["outcome"], "STALLED")
        self.assertEqual(decide(current, prior, fixed("F1", "F2"))["outcome"], "CONTINUE")

    def test_new_blocking_finding_alongside_rejected_repeat_continues(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High"), finding("F2", "High", title="Race on write", location="src/b.py:3")], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, rejected("F1"))["outcome"], "CONTINUE")

    def test_duplicate_prior_ids_fail_loud(self):
        prior = report(1, [finding("F1")])
        current = report(2, [finding("F1")], prior=[{"id": "F1", "status": "unresolved"}, {"id": "F1", "status": "unresolved"}])
        self.assertIn("more than once", failing(current, prior, rejected("F1")))


class StallNeedsRejectionTest(unittest.TestCase):
    def test_repeated_id_after_attempted_fix_continues(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, fixed("F1"))["outcome"], "CONTINUE")

    def test_repeated_id_after_rejection_stalls(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, rejected("F1"))["outcome"], "STALLED")

    def test_mixed_resolutions_continue(self):
        prior = report(1, [finding("F1", "High"), finding("F2", "High", title="Race on write", location="src/b.py:3")])
        current = report(2, [finding("F1", "High"), finding("F2", "High", title="Race on write", location="src/b.py:3")],
                         prior=[{"id": "F1", "status": "unresolved"}, {"id": "F2", "status": "unresolved"}])
        self.assertEqual(decide(current, prior, rejected("F1") + fixed("F2"))["outcome"], "CONTINUE")

    def test_prior_without_fixes_fails_loud(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        with self.assertRaises(GateError):
            review_gate.decide(current, prior, None)

    def test_fixes_for_unknown_id_fail_loud(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, rejected("F1", "F9"))

    def test_malformed_fixes_fail_loud(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, [{"id": "F1", "resolution": "maybe", "note": "x"}])


class FixesCompletenessTest(unittest.TestCase):
    def test_missing_entry_for_fixable_prior_finding_fails_loud(self):
        prior = report(1, [finding("F1", "High"), finding("F2", "High", title="Race on write", location="src/b.py:3")])
        current = report(2, [finding("F2", "High", title="Race on write", location="src/b.py:3")], prior=[{"id": "F1", "status": "resolved"}, {"id": "F2", "status": "unresolved"}])
        with self.assertRaises(GateError) as ctx:
            decide(current, prior, fixed("F1"))
        self.assertIn("F2", str(ctx.exception))

    def test_entries_not_required_below_fix_floor_or_confidence_gate(self):
        prior = report(1, [finding("F1", "High"), finding("F2", "Low", title="Naming", location="src/c.py:1"), finding("F3", "Critical", confidence=50, title="Maybe", location="src/d.py:1")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}, {"id": "F2", "status": "resolved"}, {"id": "F3", "status": "resolved"}])
        self.assertEqual(decide(current, prior, fixed("F1"))["outcome"], "PASS")

    def test_duplicate_ids_in_fixes_fail_loud(self):
        prior = report(1, [finding("F1", "High")])
        current = report(2, [finding("F1", "High")], prior=[{"id": "F1", "status": "unresolved"}])
        with self.assertRaises(GateError):
            decide(current, prior, fixed("F1") + rejected("F1"))

    def test_fixes_without_prior_fails_loud(self):
        with self.assertRaises(GateError):
            review_gate.decide(report(1, [finding("F1")]), None, fixed("F1"))


class ConfidenceBoundaryTest(unittest.TestCase):
    def test_confidence_exactly_80_is_kept(self):
        result = decide(report(1, [finding("F1", "High", confidence=80)]))
        self.assertEqual((result["outcome"], result["dropped_low_confidence"]), ("CONTINUE", []))

    def test_confidence_exactly_80_prior_finding_needs_a_fix_entry(self):
        prior = report(1, [finding("F1", "High", confidence=80)])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}])
        self.assertIn("F1", failing(current, prior, []))


class FingerprintTest(unittest.TestCase):
    def test_path_is_part_of_the_fingerprint(self):
        a = review_gate.fingerprint(finding("F1", location="src/a.py:1"))
        b = review_gate.fingerprint(finding("F1", location="src/b.py:1"))
        self.assertNotEqual(a, b)

    def test_category_is_part_of_the_fingerprint(self):
        a = review_gate.fingerprint(finding("F1", category="correctness"))
        b = review_gate.fingerprint(finding("F1", category="security"))
        self.assertNotEqual(a, b)

    def test_same_title_in_another_file_is_not_a_repeat(self):
        prior = report(1, [finding("F1", "High", location="src/a.py:1")])
        current = report(2, [finding("F2", "High", location="src/b.py:1")], prior=[{"id": "F1", "status": "resolved"}])
        self.assertEqual(decide(current, prior, rejected("F1"))["outcome"], "CONTINUE")


class ExactShapeTest(unittest.TestCase):
    def test_unexpected_report_key_fails_loud(self):
        bad = report(1, [finding("F1")])
        bad["verdict"] = "PASS"
        self.assertIn("verdict", failing(bad))

    def test_unexpected_finding_key_fails_loud(self):
        bad = finding("F1")
        bad["fingerprint"] = "abc"
        self.assertIn("fingerprint", failing(report(1, [bad])))

    def test_empty_reviewer_or_target_fails_loud(self):
        bad = report(1, [finding("F1")], reviewer="")
        self.assertIn("reviewer", failing(bad))
        bad = report(1, [finding("F1")])
        bad["target"] = " "
        self.assertIn("target", failing(bad))

    def test_non_string_reviewer_fails_loud(self):
        bad = report(1, [finding("F1")])
        bad["reviewer"] = 5
        self.assertIn("reviewer", failing(bad))

    def test_unexpected_prior_findings_key_fails_loud(self):
        prior = report(1, [finding("F1")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved", "note": "x"}])
        self.assertIn("id and status", failing(current, prior, rejected("F1")))

    def test_unexpected_fixes_key_fails_loud(self):
        prior = report(1, [finding("F1")])
        current = report(2, [], prior=[{"id": "F1", "status": "resolved"}])
        fixes = [{"id": "F1", "resolution": "fixed", "note": "done", "fingerprint": "abc"}]
        self.assertIn("exactly id, resolution and note", failing(current, prior, fixes))


class MainTest(unittest.TestCase):
    def write(self, tmp, name, payload):
        path = Path(tmp) / name
        path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        return str(path)

    def test_round_one_prints_the_decision_and_exits_zero(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([self.write(tmp, "r1.json", report(1, [finding("F1")]))])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(out)["outcome"], "CONTINUE")

    def test_contract_violation_exits_two_with_prefix(self):
        with TemporaryDirectory() as tmp:
            code, out, err = run_main([self.write(tmp, "r1.json", {})])
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("review_gate: "))

    def test_missing_and_invalid_files_exit_two(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(run_main(["/nonexistent/r1.json"])[0], 2)
            self.assertEqual(run_main([self.write(tmp, "r1.json", "{not json")])[0], 2)
            r2 = self.write(tmp, "r2.json", report(2, [finding("F1")], prior=[{"id": "F1", "status": "unresolved"}]))
            self.assertEqual(run_main([r2, "--prior", "/nonexistent/r1.json", "--fixes", "/nonexistent/f.json"])[0], 2)

    def test_gate_options_reach_the_decision(self):
        with TemporaryDirectory() as tmp:
            r1 = self.write(tmp, "r1.json", report(1, [finding("F1", "Medium"), finding("F2", "Low", title="Naming", location="src/b.py:1")]))
            code, out, _ = run_main([r1, "--max-rounds", "1", "--min-severity", "Medium", "--fix-floor", "Low"])
        decision = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(
            (decision["outcome"], decision["max_rounds"], decision["min_severity"], decision["blocking"], decision["fixable"]),
            ("EXHAUSTED", 1, "Medium", ["F1"], ["F1", "F2"]),
        )

    def test_fixes_without_prior_exits_two(self):
        with TemporaryDirectory() as tmp:
            r1 = self.write(tmp, "r1.json", report(1, [finding("F1")]))
            f1 = self.write(tmp, "f1.json", rejected("F1"))
            code, out, err = run_main([r1, "--fixes", f1])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("--fixes without --prior", err)

    def test_script_entry_point_via_subprocess(self):
        with TemporaryDirectory() as tmp:
            r1 = self.write(tmp, "r1.json", report(1, []))
            done = subprocess.run([sys.executable, "-I", review_gate.__file__, r1], capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        self.assertEqual(json.loads(done.stdout)["outcome"], "PASS")


if __name__ == "__main__":
    unittest.main()
