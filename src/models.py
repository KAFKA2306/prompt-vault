from __future__ import annotations

from pydantic import BaseModel, Field


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
    blocks: list[str]
    kind: str = "standard"
    purpose: str = ""
    summary: str = ""
    artifacts: list[Artifact] = Field(default_factory=list)
    generated_prompt: str | None = None


class PromptDB(BaseModel):
    blocks: list[Block]
    templates: list[Template]
