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
    kind: str = "standard"
    purpose: str = ""
    summary: str = ""
    artifacts: list[Artifact] = Field(default_factory=list)
    generated_prompt: str | None = None
    created_at: str | None = None


class PromptDB(BaseModel):
    blocks: list[Block]
    templates: list[Template]

    @model_validator(mode="before")
    @classmethod
    def migrate_generated(cls, data: Any) -> Any:
        if isinstance(data, dict) and "generated_prompts" in data:
            generated = data.pop("generated_prompts", [])
            templates = data.get("templates", [])
            existing_ids = {t.get("id") if isinstance(t, dict) else t.id for t in templates}
            for g in generated:
                if g.get("id") not in existing_ids:
                    g["kind"] = "generated"
                    templates.append(g)
            data["templates"] = templates
        return data
