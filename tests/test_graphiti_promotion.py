import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from src.graphiti_promotion import build_promotion_candidate, promote_candidate
from src.prompt_db import PromptDB


def payload(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "id": "graphiti_reusable_retry",
        "title": "Retry only failed bounded work",
        "prompt": "Retry only the failed bounded operation and preserve successful evidence.",
        "source_kind": "lesson",
        "knowledge_state": "current",
        "provenance": {
            "source_repo": "KAFKA2306/example",
            "commit_sha": "a" * 40,
            "evidence": "tests/test_retry.py::test_retry_failed_only",
            "graphiti_id": "episode-42:fact-3",
            "promoted_at": datetime(2026, 9, 17, tzinfo=timezone.utc).isoformat(),
        },
    }
    value.update(overrides)
    return value


class GraphitiPromotionTest(unittest.TestCase):
    def test_valid_candidate_registers_in_existing_prompt_db(self) -> None:
        candidate = build_promotion_candidate(payload())
        db = PromptDB(blocks=[], templates=[])
        promoted = promote_candidate(db, candidate)

        self.assertEqual(db.templates, [])
        self.assertEqual(len(promoted.templates), 1)
        template = promoted.templates[0]
        self.assertEqual(template.id, candidate.id)
        self.assertEqual(template.kind, "generated")
        self.assertEqual(template.generated_prompt, candidate.prompt)
        self.assertIn("KAFKA2306/example@" + "a" * 40, template.summary)
        self.assertIn("episode-42:fact-3", template.summary)

    def test_missing_provenance_is_rejected(self) -> None:
        invalid = payload()
        invalid.pop("provenance")
        with self.assertRaises(ValidationError):
            build_promotion_candidate(invalid)

    def test_stale_graphiti_knowledge_is_rejected(self) -> None:
        for state in ("corrected", "superseded"):
            with self.subTest(state=state), self.assertRaisesRegex(ValidationError, "cannot promote"):
                build_promotion_candidate(payload(knowledge_state=state))

    def test_duplicate_candidate_does_not_create_second_authority(self) -> None:
        candidate = build_promotion_candidate(payload())
        promoted = promote_candidate(PromptDB(blocks=[], templates=[]), candidate)
        with self.assertRaisesRegex(ValueError, "template already exists"):
            promote_candidate(promoted, candidate)


if __name__ == "__main__":
    unittest.main()
