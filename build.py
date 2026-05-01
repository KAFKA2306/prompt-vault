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
    block_nodes = set()
    block_ids = set()
    for block in db["blocks"]:
        block_id = block["id"]
        if block_id in block_ids:
            raise ValueError(f"duplicate block id: {block_id}")
        block_ids.add(block_id)
        block_nodes.add(block_id)
    template_ids = set()
    for template in db["templates"]:
        template_id = template["id"]
        if template_id in template_ids:
            raise ValueError(f"duplicate template id: {template_id}")
        template_ids.add(template_id)
    all_nodes = block_nodes | template_ids
    for block in db["blocks"]:
        block_id = block["id"]
        for related_id in block.get("related", []):
            if related_id not in all_nodes:
                raise ValueError(f"unknown related id in {block_id}: {related_id}")
        variant_of = block.get("variant_of")
        if variant_of and variant_of not in all_nodes:
            raise ValueError(f"unknown variant_of id in {block_id}: {variant_of}")
    for template in db["templates"]:
        template_id = template["id"]
        for block_id in template["blocks"]:
            if block_id not in block_ids:
                raise ValueError(f"unknown block id in {template_id}: {block_id}")
        for node_id in template.get("uses", []):
            if node_id not in all_nodes:
                raise ValueError(f"unknown uses id in {template_id}: {node_id}")
        artifact_paths = set()
        for artifact in template.get("artifacts", []):
            artifact_path = artifact["path"]
            if artifact_path in artifact_paths:
                raise ValueError(f"duplicate artifact path in {template_id}: {artifact_path}")
            artifact_paths.add(artifact_path)
            absolute_path = ROOT / artifact_path
            if not absolute_path.exists():
                raise ValueError(f"missing artifact in {template_id}: {artifact_path}")
    return db


def render_app_js(db: dict[str, Any]) -> str:
    db_json = json.dumps(db, ensure_ascii=False)
    source = (STATIC_PATH / "app.js").read_text(encoding="utf-8")
    return source.replace("__DB_JSON__", db_json)


def write_dist() -> None:
    db = load_db()
    if DIST_PATH.exists():
        shutil.rmtree(DIST_PATH)
    DIST_PATH.mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "artifacts").mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "index.html").write_text((STATIC_PATH / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST_PATH / "style.css").write_text((STATIC_PATH / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST_PATH / "app.js").write_text(render_app_js(db), encoding="utf-8")
    for source in STATIC_PATH.rglob("*"):
        if not source.is_file() or source.name in {"index.html", "style.css", "app.js"}:
            continue
        relative_path = source.relative_to(STATIC_PATH)
        destination = DIST_PATH / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for source in ARTIFACTS_PATH.glob("*.png"):
        shutil.copy2(source, DIST_PATH / "artifacts" / source.name)


def main() -> None:
    write_dist()


if __name__ == "__main__":
    main()
