from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"
STATIC_PATH = ROOT / "static"
DIST_PATH = ROOT / "dist"
ARTIFACTS_PATH = ROOT / "artifacts"


def load_db() -> dict[str, Any]:
    db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    block_ids = {b["id"] for b in db["blocks"]}
    for t in db["templates"]:
        for bid in t["blocks"]:
            if bid not in block_ids:
                raise ValueError(f"unknown block: {bid}")
        for a in t.get("artifacts", []):
            if not (ROOT / a["path"]).exists():
                raise ValueError(f"missing artifact: {a['path']}")

    for r in db.get("generated_prompts", []):
        if any(t["id"] == r["id"] for t in db["templates"]):
            continue
        db["templates"].append(
            {
                "id": r["id"],
                "title": r["title"],
                "kind": "generated",
                "blocks": r.get("block_ids", []),
                "generated_prompt": r["generated_prompt"],
                "generated_from": r.get("template_id"),
                "generated_at": r["created_at"],
            }
        )
    return db


def render_app_js(db: dict[str, Any]) -> str:
    return (
        (STATIC_PATH / "app.js").read_text(encoding="utf-8").replace("__DB_JSON__", json.dumps(db, ensure_ascii=False))
    )


def write_dist():
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
