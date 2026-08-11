#!/usr/bin/env python3
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kafka_signal_score", ROOT / "scripts" / "score.py")
score = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(score)
POLICY = json.loads((ROOT / "audit" / "scoring-policy.json").read_text(encoding="utf-8"))


def record(*, browser_verified=True, console_errors=0, overflow=0, focus=True, viewports=None, scores=None):
    return {
        "repo": "KAFKA2306/example",
        "element": "EvidenceCard",
        "path": "web/EvidenceCard.tsx",
        "source_commit": "a" * 40,
        "scores": scores
        or {
            "visual_quality": 5,
            "task_completion": 5,
            "responsiveness": 5,
            "accessibility": 4,
            "interaction_quality": 4,
            "data_semantics": 5,
            "reusability": 4,
            "evidence_maintainability": 4,
        },
        "evidence": {
            "static": ["source path", "commit"],
            "browser": {
                "verified": browser_verified,
                "viewports": viewports if viewports is not None else [360, 768, 1440],
                "screenshots": ["mobile.webp", "desktop.webp"],
                "console_errors": console_errors,
                "unexpected_overflow": overflow,
                "keyboard_focus_verified": focus,
            },
        },
        "canonical_target": "components/evidence-card",
    }


class ScoringEngineTests(unittest.TestCase):
    def test_verified_s_candidate_can_flow_to_harvester(self):
        out = score.adjudicate(record(), POLICY)
        self.assertEqual(out["total"], 36)
        self.assertEqual(out["nominal_grade"], "S")
        self.assertEqual(out["grade"], "S")
        self.assertEqual(out["decision_status"], "verified")
        self.assertTrue(out["canonical_candidate"])

    def test_unverified_s_is_capped_and_blocked(self):
        out = score.adjudicate(record(browser_verified=False), POLICY)
        self.assertEqual(out["nominal_grade"], "S")
        self.assertEqual(out["grade"], "B")
        self.assertEqual(out["decision_status"], "provisional")
        self.assertFalse(out["canonical_candidate"])
        self.assertIsNone(out["canonical_target"])

    def test_browser_failure_blocks_promotion(self):
        out = score.adjudicate(record(console_errors=1), POLICY)
        self.assertEqual(out["nominal_grade"], "S")
        self.assertEqual(out["grade"], "B")
        self.assertFalse(out["canonical_candidate"])
        self.assertIn("browser console errors are not zero", out["defects"])

    def test_missing_required_viewport_blocks_promotion(self):
        out = score.adjudicate(record(viewports=[360, 1440]), POLICY)
        self.assertFalse(out["canonical_candidate"])
        self.assertTrue(any("768" in defect for defect in out["defects"]))

    def test_invalid_dimension_score_fails_closed(self):
        bad = record()
        bad["scores"]["visual_quality"] = 6
        with self.assertRaises(ValueError):
            score.adjudicate(bad, POLICY)


if __name__ == "__main__":
    unittest.main()
