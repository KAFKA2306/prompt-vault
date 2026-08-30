from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
WORKFLOW = WORKFLOW_DIR / "results-aggregate.yml"
CATEGORIES = (
    "code-quality",
    "data-quality",
    "reliability",
    "automation",
    "adoption",
    "business",
)


class ResultsPipelineContractTest(unittest.TestCase):
    def test_results_have_one_workflow_authority(self) -> None:
        workflows = sorted(path.name for path in WORKFLOW_DIR.glob("results-*.yml"))
        self.assertEqual(workflows, ["results-aggregate.yml"])

    def test_single_run_collects_and_aggregates_every_category(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for category in CATEGORIES:
            with self.subTest(category=category):
                self.assertIn(f"category: {category}", workflow)
        self.assertIn("needs: collect", workflow)
        self.assertIn("actions/download-artifact@v7", workflow)
        self.assertIn("merge-multiple: true", workflow)
        self.assertIn("scripts/results/validate_snapshot.py", workflow)

    def test_aggregate_does_not_mix_snapshots_from_other_runs(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("gh run list", workflow)
        self.assertNotIn("gh run download", workflow)
        self.assertNotIn("results-code-quality.yml", workflow)
        self.assertNotIn("results-data-quality.yml", workflow)
        self.assertNotIn("results-reliability.yml", workflow)
        self.assertNotIn("results-automation.yml", workflow)
        self.assertNotIn("results-adoption.yml", workflow)
        self.assertNotIn("results-business.yml", workflow)


if __name__ == "__main__":
    unittest.main()
