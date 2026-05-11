from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Artifact(BaseModel):
    path: str
    title: str = ""


class Block(BaseModel):
    id: str
    title: str
    content: str
    role: str
    category: str = ""


class Template(BaseModel):
    id: str
    title: str
    blocks: list[str] = Field(default_factory=list)
    kind: Literal[
        "announcement",
        "brand",
        "comic",
        "design_sheet",
        "news",
        "reaction",
        "sheet",
        "social",
        "stamp",
        "system",
        "generated",
    ] = "social"
    purpose: str = ""
    summary: str = ""
    artifacts: list[Artifact] = Field(default_factory=list)
    generated_prompt: str | None = None
    voice_caption: str | None = None
    voice_script: str | None = None
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
            existing_ids = {
                t.get("id") if isinstance(t, dict) else (t.id if hasattr(t, "id") else None) for t in templates
            }
            for g in generated:
                if g.get("id") not in existing_ids:
                    g["kind"] = "generated"
                    templates.append(g)
            data["templates"] = templates

        return data
