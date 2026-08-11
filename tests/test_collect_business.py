from __future__ import annotations

import importlib.util
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "collect_business.py"
spec = importlib.util.spec_from_file_location("collect_business", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class BusinessCollectorTests(unittest.TestCase):
    def base_repo(self):
        return {
            "id": 1,
            "node_id": "R_test",
            "name": "demo",
            "full_name": "KAFKA2306/demo",
            "private": False,
            "archived": False,
            "html_url": "https://github.com/KAFKA2306/demo",
            "default_branch": "main",
        }

    def test_declared_offer_does_not_become_revenue(self):
        repo = self.base_repo()
        declarations = [{"path": "docs/business/demo.md", "blob_sha": "abc", "url": "https://example.test", "kind": "repository_owned_business_declaration"}]
        report = module.aggregate(repo, declarations, "complete", datetime(2026, 8, 12, tzinfo=timezone.utc))
        self.assertEqual(report["schema_version"], "kafka.results.business.v1")
        self.assertEqual(report["inventory"]["status"], "declared_business_surface_detected")
        self.assertEqual(report["inventory"]["tree_status"], "complete")
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
            declarations, tree_status = module.list_business_declarations(repo)
        finally:
            module.gh_get = original
        self.assertEqual(tree_status, "complete")
        self.assertEqual([d["path"] for d in declarations], ["docs/business/offer.md", "docs/services/service.md"])

    def test_truncated_tree_is_unknown_not_empty_inventory(self):
        repo = self.base_repo()
        original = module.gh_get
        module.gh_get = lambda path, token=None: {"truncated": True, "tree": []}
        try:
            declarations, tree_status = module.list_business_declarations(repo)
        finally:
            module.gh_get = original
        self.assertEqual(declarations, [])
        self.assertEqual(tree_status, "truncated")
        report = module.aggregate(repo, declarations, tree_status, datetime(2026, 8, 12, tzinfo=timezone.utc))
        self.assertEqual(report["inventory"]["status"], "unknown_tree_truncated")

    def test_git_tree_conflict_is_unknown_not_collection_failure(self):
        repo = self.base_repo()
        original = module.gh_get

        def conflict(path, token=None):
            raise urllib.error.HTTPError("https://api.github.test/tree", 409, "Conflict", None, None)

        module.gh_get = conflict
        try:
            declarations, tree_status = module.list_business_declarations(repo)
        finally:
            module.gh_get = original
        self.assertEqual(declarations, [])
        self.assertEqual(tree_status, "unavailable_conflict")
        report = module.aggregate(repo, declarations, tree_status, datetime(2026, 8, 12, tzinfo=timezone.utc))
        self.assertEqual(report["inventory"]["status"], "unknown_tree_unavailable")

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
