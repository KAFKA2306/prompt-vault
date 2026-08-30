from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_weekly_power_macro_intelligence.sh"
WORKFLOW = ROOT / ".github/workflows/weekly-macro-intelligence.yml"
VERIFIER = ROOT / "scripts/verify_weekly_power_macro_outputs.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("weekly_macro_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load weekly macro verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WeeklyPowerMacroContractTest(unittest.TestCase):
    def test_runner_shell_syntax(self) -> None:
        subprocess.run(["bash", "-n", str(RUNNER)], check=True)

    def test_report_validation_has_one_authority(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        verifier = VERIFIER.read_text(encoding="utf-8")
        self.assertNotIn("forbidden_pattern=", runner)
        self.assertNotIn("lint_report()", runner)
        self.assertIn("FORBIDDEN = re.compile", verifier)

        verifier_module = load_verifier()
        self.assertIsNotNone(verifier_module.FORBIDDEN.search("Fetch Failures"))
        self.assertIsNotNone(verifier_module.FORBIDDEN.search("file://local/path"))

    def test_runner_does_not_publish_fallback_reports(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        forbidden_fragments = (
            "source: collection_fallback",
            "agy_status: failed",
            "gh not found; skipping issue publish",
            "repo is empty; skipping issue publish",
            "issue_exists()",
            "|| true",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, runner)

    def test_workflow_does_not_ignore_push_failure(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("            git push\n", workflow)
        self.assertNotIn("git push || echo", workflow)


if __name__ == "__main__":
    unittest.main()
