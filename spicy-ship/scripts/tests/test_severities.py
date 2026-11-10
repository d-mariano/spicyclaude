"""Tests for the shared severity scale."""

import json
import unittest
from pathlib import Path

from severities import SEVERITIES, at_least

SCHEMA = Path(__file__).resolve().parents[2] / "skills" / "review-loop" / "references" / "findings.schema.json"


class SeveritiesTest(unittest.TestCase):
    """The shared severity scale: its order and the at_least comparison on the new lowest tier."""

    def test_scale_is_five_tiers_strictest_first(self):
        self.assertEqual(SEVERITIES, ("Critical", "High", "Medium", "Low", "Nit"))

    def test_low_meets_a_nit_floor(self):
        self.assertTrue(at_least("Low", "Nit"))

    def test_nit_does_not_meet_a_low_floor(self):
        self.assertFalse(at_least("Nit", "Low"))

    def test_findings_schema_lists_the_same_scale(self):
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(schema["$defs"]["finding"]["properties"]["severity"]["enum"], list(SEVERITIES))
