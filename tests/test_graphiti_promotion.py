from datetime import datetime, timezone

import pytest
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


def test_valid_candidate_registers_in_existing_prompt_db() -> None:
    candidate = build_promotion_candidate(payload())
    db = PromptDB(blocks=[], templates=[])

    promoted = promote_candidate(db, candidate)

    assert db.templates == []
    assert len(promoted.templates) == 1
    template = promoted.templates[0]
    assert template.id == candidate.id
    assert template.kind == "generated"
    assert template.generated_prompt == candidate.prompt
    assert "KAFKA2306/example@" + "a" * 40 in template.summary
    assert "episode-42:fact-3" in template.summary


def test_missing_provenance_is_rejected() -> None:
    invalid = payload()
    invalid.pop("provenance")
    with pytest.raises(ValidationError):
        build_promotion_candidate(invalid)


@pytest.mark.parametrize("state", ["corrected", "superseded"])
def test_stale_graphiti_knowledge_is_rejected(state: str) -> None:
    with pytest.raises(ValidationError, match="cannot promote"):
        build_promotion_candidate(payload(knowledge_state=state))


def test_duplicate_candidate_does_not_create_second_authority() -> None:
    candidate = build_promotion_candidate(payload())
    promoted = promote_candidate(PromptDB(blocks=[], templates=[]), candidate)
    with pytest.raises(ValueError, match="template already exists"):
        promote_candidate(promoted, candidate)
