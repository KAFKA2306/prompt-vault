from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "collect_business.py"
spec = importlib.util.spec_from_file_location("collect_business", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class BusinessCollectorTests(unittest.TestCase):
    def test_declared_offer_does_not_become_revenue(self):
        repo = {
            "id": 1,
            "node_id": "R_test",
            "name": "demo",
            "full_name": "KAFKA2306/demo",
            "private": False,
            "archived": False,
            "html_url": "https://github.com/KAFKA2306/demo",
            "default_branch": "main",
        }
        declarations = [{"path": "docs/business/demo.md", "blob_sha": "abc", "url": "https://example.test", "kind": "repository_owned_business_declaration"}]
        report = module.aggregate(repo, declarations, datetime(2026, 8, 12, tzinfo=timezone.utc))
        self.assertEqual(report["schema_version"], "kafka.results.business.v1")
        self.assertEqual(report["inventory"]["status"], "declared_business_surface_detected")
        for metric in report["metrics"].values():
            self.assertIsNone(metric["value"])
            self.assertEqual(metric["status"], "not_instrumented")
        self.assertFalse(report["measurement_contract"]["unobserved_business_metric_is_zero"])
        self.assertFalse(report["measurement_contract"]["free_usage_or_downloads_counted_as_revenue"])

    def test_business_declarations_only_use_repository_owned_conventional_paths(self):
        repo = {"full_name": "KAFKA2306/demo", "default_branch": "main"}
        original = module.gh_get

        def fake_get(path, token=None):
            return {
                "truncated": False,
                "tree": [
                    {"type": "blob", "path": "docs/business/offer.md", "sha": "1"},
                    {"type": "blob", "path": "docs/services/service.md", "sha": "2"},
                    {"type": "blob", "path": "README.md", "sha": "3"},
                    {"type": "blob", "path": "issues/business.md", "sha": "4"},
                ],
            }

        module.gh_get = fake_get
        try:
            declarations = module.list_business_declarations(repo)
        finally:
            module.gh_get = original
        self.assertEqual([d["path"] for d in declarations], ["docs/business/offer.md", "docs/services/service.md"])

    def test_truncated_tree_fails_closed_without_inventing_inventory(self):
        repo = {"full_name": "KAFKA2306/demo", "default_branch": "main"}
        original = module.gh_get
        module.gh_get = lambda path, token=None: {"truncated": True, "tree": []}
        try:
            declarations = module.list_business_declarations(repo)
        finally:
            module.gh_get = original
        self.assertEqual(declarations, [])

    def test_repository_listing_paginates(self):
        calls = []
        original = module.gh_get

        def fake_get(path, token=None):
            calls.append(path)
            page = int(parse_qs(urlparse(path).query)["page"][0])
            if page == 1:
                return [{"name": str(i)} for i in range(100)]
            if page == 2:
                return [{"name": "last"}]
            return []

        module.gh_get = fake_get
        try:
            repos = module.list_owner_repositories("KAFKA2306")
        finally:
            module.gh_get = original
        self.assertEqual(len(repos), 101)
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
