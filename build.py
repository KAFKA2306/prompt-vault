from __future__ import annotations

import json
import shutil
from pathlib import Path

from src.models import PromptDB, Template

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"
STATIC_PATH = ROOT / "static"
DIST_PATH = ROOT / "dist"
ARTIFACTS_PATH = ROOT / "artifacts"


def load_db() -> PromptDB:
    db = PromptDB.model_validate_json(DB_PATH.read_text(encoding="utf-8"))
    block_ids = {b.id for b in db.blocks}
    for t in db.templates:
        for bid in t.blocks:
            if bid not in block_ids:
                raise ValueError(f"unknown block: {bid}")
        for a in t.artifacts:
            if not (ROOT / a.path).exists():
                raise ValueError(f"missing artifact: {a.path}")
        if t.kind == "generated" and not t.artifacts:
            print(f"Warning: generated template '{t.id}' has no artifacts")

    return db


def render_app_js(db: PromptDB) -> str:
    db_json = db.model_dump(exclude_none=True)
    return (
        (STATIC_PATH / "app.js")
        .read_text(encoding="utf-8")
        .replace("__DB_JSON__", json.dumps(db_json, ensure_ascii=False))
    )


def write_dist() -> None:
    db = load_db()
    if DIST_PATH.exists():
        shutil.rmtree(DIST_PATH)
    DIST_PATH.mkdir(exist_ok=True)
    (DIST_PATH / "artifacts").mkdir(exist_ok=True)
    for f in ["index.html", "style.css"]:
        (DIST_PATH / f).write_text((STATIC_PATH / f).read_text(encoding="utf-8"), encoding="utf-8")
    (DIST_PATH / "app.js").write_text(render_app_js(db), encoding="utf-8")
    for s in STATIC_PATH.rglob("*"):
        if s.is_file() and s.name not in ["index.html", "style.css", "app.js"]:
            dest = DIST_PATH / s.relative_to(STATIC_PATH)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)
    for s in ARTIFACTS_PATH.glob("*.png"):
        shutil.copy2(s, DIST_PATH / "artifacts" / s.name)


if __name__ == "__main__":
    write_dist()
