from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "collect_adoption.py"
spec = importlib.util.spec_from_file_location("collect_adoption", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class AdoptionCollectorTests(unittest.TestCase):
    def test_public_surface_keeps_usage_unknown_and_proxies_separate(self):
        repo = {
            "id": 1,
            "node_id": "R_test",
            "name": "demo",
            "full_name": "KAFKA2306/demo",
            "owner": {"login": "KAFKA2306"},
            "private": False,
            "archived": False,
            "has_pages": True,
            "homepage": "https://example.test/demo",
            "html_url": "https://github.com/KAFKA2306/demo",
            "stargazers_count": 12,
            "forks_count": 3,
            "updated_at": "2026-08-12T00:00:00Z",
            "pushed_at": "2026-08-12T00:00:00Z",
        }
        report = module.aggregate(repo, datetime(2026, 8, 12, tzinfo=timezone.utc))
        self.assertEqual(report["schema_version"], "kafka.results.adoption.v1")
        self.assertEqual(report["service_inventory"]["status"], "public_surface_detected")
        self.assertIsNone(report["observed_usage"]["page_views"]["value"])
        self.assertEqual(report["observed_usage"]["page_views"]["status"], "not_instrumented")
        self.assertEqual(report["proxy_metrics"]["github_stars"]["value"], 12)
        self.assertEqual(report["proxy_metrics"]["github_stars"]["kind"], "proxy")
        self.assertEqual(report["proxy_metrics"]["github_stars"]["not_equivalent_to"], "users_or_usage")
        self.assertTrue(report["measurement_contract"]["real_usage_and_proxy_separated"])
        self.assertFalse(report["measurement_contract"]["unobserved_usage_is_zero"])

    def test_pages_url_is_not_invented_when_repository_metadata_only_says_has_pages(self):
        repo = {
            "id": 2,
            "node_id": "R_pages",
            "name": "pages-only",
            "full_name": "KAFKA2306/pages-only",
            "owner": {"login": "KAFKA2306"},
            "private": False,
            "archived": False,
            "has_pages": True,
            "homepage": None,
            "html_url": "https://github.com/KAFKA2306/pages-only",
            "stargazers_count": 0,
            "forks_count": 0,
            "updated_at": None,
            "pushed_at": None,
        }
        report = module.aggregate(repo, datetime(2026, 8, 12, tzinfo=timezone.utc))
        pages = [s for s in report["service_inventory"]["surfaces"] if s["kind"] == "github_pages"]
        self.assertEqual(len(pages), 1)
        self.assertIsNone(pages[0]["url"])
        self.assertEqual(pages[0]["url_status"], "not_resolved_from_repository_metadata")

    def test_repository_listing_paginates_until_short_page(self):
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
        self.assertEqual(int(parse_qs(urlparse(calls[1]).query)["page"][0]), 2)


if __name__ == "__main__":
    unittest.main()
