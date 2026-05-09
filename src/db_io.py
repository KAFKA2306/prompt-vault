from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models import PromptDB


def load_json_db(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json_db(path: Path, db: dict[str, Any]) -> None:
    path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_prompt_db(path: Path) -> PromptDB:
    return PromptDB.model_validate_json(path.read_text(encoding="utf-8"))
