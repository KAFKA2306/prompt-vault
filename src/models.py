from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Block:
    id: str
    title: str
    content: str
    category: str = ""
    family: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class Template:
    id: str
    title: str
    blocks: list[str]
    kind: str = "standard"
    purpose: str = ""
    summary: str = ""
    artifacts: list[dict[str, str]] = field(default_factory=list)
    generated_prompt: str | None = None
    generated_from: str | None = None
    generated_at: str | None = None


def parse_db(data: dict[str, Any]) -> tuple[dict[str, Block], list[Template]]:
    blocks = {b["id"]: Block(**{k: v for k, v in b.items() if k in Block.__annotations__}) for b in data["blocks"]}
    templates = [Template(**{k: v for k, v in t.items() if k in Template.__annotations__}) for t in data["templates"]]
    return blocks, templates
