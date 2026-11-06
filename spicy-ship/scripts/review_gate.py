#!/usr/bin/env python3
"""Decide the next step of a review loop from a round's findings file.

Validates the findings contract, drops findings under the shared confidence
gate of 80, then returns PASS, CONTINUE, EXHAUSTED or STALLED. Schema
violations exit 2 so a SubagentStop hook can reuse this script unchanged.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SEVERITIES = ("Critical", "High", "Medium", "Low")
CONFIDENCE_GATE = 80
VERDICTS = ("PASS", "CHANGES_REQUESTED")
PRIOR_STATUSES = ("resolved", "unresolved", "regressed")
REPORT_KEYS = ("reviewer", "target", "round", "verdict", "prior_findings", "findings")
FINDING_KEYS = ("id", "title", "severity", "confidence", "location", "category", "problem", "fix")
CATEGORIES = (
    "correctness", "security", "tests", "design", "ac-coverage", "mental-alignment",
    "code-quality", "documentation", "performance", "deps", "observability", "simplification",
)
ID_PATTERN = re.compile(r"^F[0-9]+$")
LOCATION_PATTERN = re.compile(r"^[^:]+(:[0-9]+(-[0-9]+)?)?$")


class GateError(Exception):
    """Raised when a findings file violates the contract. Never swallowed."""


def decide(current, prior=None, *, max_rounds=3, min_severity="High", fix_floor="Medium"):
    """Apply the review-loop algorithm to one round and return the decision as a dict."""
    _validate_report(current, "current")
    if current["round"] > 1 and prior is None:
        raise GateError(f"round {current['round']} needs --prior with round {current['round'] - 1}")
    if prior is not None:
        _validate_report(prior, "prior")
        if prior["round"] != current["round"] - 1:
            raise GateError(f"prior round is {prior['round']} but current round is {current['round']}")
        _reconcile_priors(current, prior)
    if current["round"] > max_rounds:
        raise GateError(f"round {current['round']} exceeds max_rounds {max_rounds}")

    confident = [f for f in current["findings"] if f["confidence"] >= CONFIDENCE_GATE]
    dropped = [f["id"] for f in current["findings"] if f["confidence"] < CONFIDENCE_GATE]
    blocking = [f for f in confident if _at_least(f["severity"], min_severity)]
    fixable = [f["id"] for f in confident if _at_least(f["severity"], fix_floor)]

    result = {
        "outcome": None,
        "round": current["round"],
        "max_rounds": max_rounds,
        "min_severity": min_severity,
        "blocking": [f["id"] for f in blocking],
        "fixable": fixable,
        "dropped_low_confidence": dropped,
        "critical": any(f["severity"] == "Critical" for f in blocking),
    }
    if not blocking:
        result["outcome"] = "PASS"
    elif current["round"] >= max_rounds:
        result["outcome"] = "EXHAUSTED"
    elif prior is not None and _blocking_fingerprints(prior, min_severity) == {fingerprint(f) for f in blocking}:
        result["outcome"] = "STALLED"
    else:
        result["outcome"] = "CONTINUE"
    return result


def fingerprint(finding):
    """Stable identity of a finding across rounds: category, file path and normalized title."""
    path = finding["location"].split(":", 1)[0]
    title = re.sub(r"\s+", " ", finding["title"].strip().lower())
    return hashlib.sha1(f"{finding['category']}|{path}|{title}".encode()).hexdigest()


def _reconcile_priors(current, prior):
    prior_ids = {f["id"] for f in prior["findings"]}
    statuses = {p["id"]: p["status"] for p in current["prior_findings"]}
    missing = sorted(prior_ids - set(statuses))
    if missing:
        raise GateError(f"current: prior findings {missing} have no status in prior_findings")
    phantom = sorted(set(statuses) - prior_ids)
    if phantom:
        raise GateError(f"current: prior_findings lists {phantom}, which are not in the prior round")
    current_ids = {f["id"] for f in current["findings"]}
    relisted_resolved = sorted(i for i, st in statuses.items() if st == "resolved" and i in current_ids)
    if relisted_resolved:
        raise GateError(f"current: {relisted_resolved} marked resolved but still listed in findings")


def _blocking_fingerprints(report, min_severity):
    return {
        fingerprint(f)
        for f in report["findings"]
        if f["confidence"] >= CONFIDENCE_GATE and _at_least(f["severity"], min_severity)
    }


def _at_least(severity, floor):
    return SEVERITIES.index(severity) <= SEVERITIES.index(floor)


def _validate_report(report, label):
    if not isinstance(report, dict):
        raise GateError(f"{label}: findings file must be a JSON object")
    missing = [k for k in REPORT_KEYS if k not in report]
    if missing:
        raise GateError(f"{label}: missing keys {missing}")
    if not isinstance(report["round"], int) or report["round"] < 1:
        raise GateError(f"{label}: round must be a positive integer")
    if report["verdict"] not in VERDICTS:
        raise GateError(f"{label}: verdict must be one of {VERDICTS}")
    if not isinstance(report["findings"], list) or not isinstance(report["prior_findings"], list):
        raise GateError(f"{label}: findings and prior_findings must be lists")
    ids = set()
    for finding in report["findings"]:
        _validate_finding(finding, label)
        if finding["id"] in ids:
            raise GateError(f"{label}: duplicate finding id {finding['id']!r}")
        ids.add(finding["id"])
    for prior in report["prior_findings"]:
        if not isinstance(prior, dict) or set(prior) != {"id", "status"}:
            raise GateError(f"{label}: prior_findings entries need exactly id and status")
        if prior["status"] not in PRIOR_STATUSES:
            raise GateError(f"{label}: prior status must be one of {PRIOR_STATUSES}")
        if prior["status"] != "resolved" and prior["id"] not in ids:
            raise GateError(f"{label}: prior finding {prior['id']!r} is {prior['status']} but not re-listed in findings")
    expected = "CHANGES_REQUESTED" if report["findings"] else "PASS"
    if report["verdict"] != expected:
        raise GateError(f"{label}: verdict {report['verdict']!r} does not match findings count {len(report['findings'])}")


def _validate_finding(finding, label):
    if not isinstance(finding, dict):
        raise GateError(f"{label}: each finding must be an object")
    missing = [k for k in FINDING_KEYS if k not in finding]
    if missing:
        raise GateError(f"{label}: finding {finding.get('id', '?')!r} missing keys {missing}")
    if finding["severity"] not in SEVERITIES:
        raise GateError(f"{label}: finding {finding['id']!r} severity must be one of {SEVERITIES}")
    if not isinstance(finding["confidence"], int) or not 0 <= finding["confidence"] <= 100:
        raise GateError(f"{label}: finding {finding['id']!r} confidence must be an integer 0-100")
    for key in ("id", "title", "location", "category", "problem", "fix"):
        if not isinstance(finding[key], str) or not finding[key].strip():
            raise GateError(f"{label}: finding {finding.get('id', '?')!r} {key} must be a non-empty string")
    if not ID_PATTERN.match(finding["id"]):
        raise GateError(f"{label}: finding id {finding['id']!r} must look like F12")
    if finding["category"] not in CATEGORIES:
        raise GateError(f"{label}: finding {finding['id']!r} category must be one of {CATEGORIES}")
    if not LOCATION_PATTERN.match(finding["location"]):
        raise GateError(f"{label}: finding {finding['id']!r} location must be path, path:line or path:start-end")


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"{path}: {exc}") from exc


def main(argv=None):
    """CLI entry point: print the decision as JSON; exit 2 on a contract violation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current", help="this round's findings JSON")
    parser.add_argument("--prior", help="previous round's findings JSON, for stall detection")
    parser.add_argument("--max-rounds", type=int, default=3)
    parser.add_argument("--min-severity", choices=SEVERITIES, default="High")
    parser.add_argument("--fix-floor", choices=SEVERITIES, default="Medium")
    args = parser.parse_args(argv)
    try:
        result = decide(
            _load(args.current),
            _load(args.prior) if args.prior else None,
            max_rounds=args.max_rounds,
            min_severity=args.min_severity,
            fix_floor=args.fix_floor,
        )
    except GateError as exc:
        print(f"review_gate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
