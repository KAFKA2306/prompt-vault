from __future__ import annotations

import json
from pathlib import Path
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
    def migrate_fields(cls, data: Any) -> Any:  # noqa: ANN401
        if not isinstance(data, dict):
            return data

        if "generated_prompts" in data:
            generated = data.pop("generated_prompts", [])
            templates = data.get("templates", [])
            existing_ids = {
                t.get("id") if isinstance(t, dict) else (t.id if hasattr(t, "id") else None) for t in templates
            }
            for item in generated:
                if item.get("id") not in existing_ids:
                    item["kind"] = "generated"
                    templates.append(item)
            data["templates"] = templates

        return data


class EntityRule(BaseModel):
    aliases: list[str] = Field(default_factory=list)
    required_blocks: list[str] = Field(default_factory=list)
    default_negative_blocks: list[str] = Field(default_factory=list)
    hard_locks: list[str] = Field(default_factory=list)
    soft_traits: list[str] = Field(default_factory=list)
    override_policy: str = ""


class IntentRule(BaseModel):
    aliases: list[str] = Field(default_factory=list)
    preferred_blocks: list[str] = Field(default_factory=list)
    context_rules: list[dict[str, Any]] = Field(default_factory=list)


class MachineRule(BaseModel):
    id: str
    priority: int
    applies_to: list[str] = Field(default_factory=list)
    level: Literal["must", "default", "warning"]
    instruction: str


class MachineRulesDB(BaseModel):
    version: int
    updated_at: str
    load_order: list[str] = Field(default_factory=list)
    entities: dict[str, EntityRule] = Field(default_factory=dict)
    intents: dict[str, IntentRule] = Field(default_factory=dict)
    composition: dict[str, Any] = Field(default_factory=dict)
    rules: list[MachineRule] = Field(default_factory=list)


def load_json_db(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json_db(path: Path, db: dict[str, Any]) -> None:
    path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_prompt_db(path: Path) -> PromptDB:
    return PromptDB.model_validate_json(path.read_text(encoding="utf-8"))


def load_machine_rules(path: Path) -> MachineRulesDB:
    return MachineRulesDB.model_validate_json(path.read_text(encoding="utf-8"))
