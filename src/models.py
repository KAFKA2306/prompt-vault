from typing import Any

from pydantic import BaseModel, Field, model_validator


class Artifact(BaseModel):
    path: str
    title: str = ""


class Block(BaseModel):
    id: str
    title: str
    content: str
    category: str = ""


class Template(BaseModel):
    id: str
    title: str
    blocks: list[str] = Field(default_factory=list)
    summary: str = ""
    artifacts: list[Artifact] = Field(default_factory=list)
    generated_prompt: str | None = None
    created_at: str | None = None


class PromptDB(BaseModel):
    blocks: list[Block]
    templates: list[Template]

    @model_validator(mode="before")
    @classmethod
    def migrate_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Handle legacy generated_prompts field
        if "generated_prompts" in data:
            generated = data.pop("generated_prompts", [])
            templates = data.get("templates", [])
            existing_ids = {t.get("id") if isinstance(t, dict) else t.id for t in templates}
            for g in generated:
                if g.get("id") not in existing_ids:
                    templates.append(g)
            data["templates"] = templates

        # Consolidate kind/purpose into summary for all templates
        for t in data.get("templates", []):
            if not isinstance(t, dict):
                continue
            kind = t.pop("kind", None)
            purpose = t.pop("purpose", None)
            
            # Use 'generated' label if generated_prompt exists
            if t.get("generated_prompt") and not kind:
                kind = "generated"

            parts = [p for p in [kind, purpose, t.get("summary")] if p and p not in ("standard", "")]
            if parts:
                t["summary"] = " / ".join(parts)
        
        return data
