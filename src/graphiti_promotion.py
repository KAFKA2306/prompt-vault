from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.prompt_db import PromptDB, Template


class PromotionProvenance(BaseModel):
    source_repo: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    evidence: str = Field(min_length=1)
    graphiti_id: str = Field(min_length=1)
    promoted_at: datetime


class PromotionCandidate(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    provenance: PromotionProvenance
    knowledge_state: Literal["current", "corrected", "superseded"] = "current"
    source_kind: Literal["fact", "lesson", "correction"]

    @model_validator(mode="after")
    def reject_stale_knowledge(self) -> "PromotionCandidate":
        if self.knowledge_state != "current":
            raise ValueError(f"cannot promote {self.knowledge_state} Graphiti knowledge")
        return self


def build_promotion_candidate(payload: dict[str, object]) -> PromotionCandidate:
    """Validate one reusable candidate without copying raw Graphiti knowledge."""
    return PromotionCandidate.model_validate(payload)


def promote_candidate(db: PromptDB, candidate: PromotionCandidate) -> PromptDB:
    """Register an approved candidate through the existing PromptDB authority."""
    if any(template.id == candidate.id for template in db.templates):
        raise ValueError(f"template already exists: {candidate.id}")

    template = Template(
        id=candidate.id,
        title=candidate.title,
        kind="generated",
        purpose="Promoted reusable Graphiti knowledge",
        summary=(
            f"source={candidate.provenance.source_repo}@{candidate.provenance.commit_sha}; "
            f"graphiti={candidate.provenance.graphiti_id}; evidence={candidate.provenance.evidence}"
        ),
        generated_prompt=candidate.prompt,
        created_at=candidate.provenance.promoted_at.isoformat(),
    )
    return db.model_copy(update={"templates": [*db.templates, template]})
