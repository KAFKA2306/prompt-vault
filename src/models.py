from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    path: str
    title: str = ""


class Block(BaseModel):
    id: str
    title: str
    content: str
    category: str = ""
    family: str = ""
    tags: list[str] = Field(default_factory=list)
    variant_of: str | None = None
    aliases: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    notes: str | None = None


class Template(BaseModel):
    id: str
    title: str
    blocks: list[str]
    kind: str = "standard"
    purpose: str = ""
    summary: str = ""
    steps: list[str] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    family: str = ""
    visibility: str = "public"
    notes: str | None = None
    generated_prompt: str | None = None
    generated_from: str | None = None
    generated_at: str | None = None


class PromptDB(BaseModel):
    blocks: list[Block]
    templates: list[Template]
    generated_prompts: list[dict[str, Any]] = Field(default_factory=list)
