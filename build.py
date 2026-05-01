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


def generated_template_title(source_title: str, instruction: str, limit: int = 28) -> str:
    compact_instruction = " ".join(instruction.split()).strip()
    if compact_instruction and len(compact_instruction) > limit:
        compact_instruction = compact_instruction[:limit].rstrip() + "…"
    if not compact_instruction:
        compact_instruction = "生成版"
    if source_title:
        return f"{source_title} / {compact_instruction}"
    return compact_instruction


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

    for template in db["templates"]:
        if template.get("kind") != "generated":
            continue
        source_template = next((item for item in db["templates"] if item["id"] == template.get("generated_from")), None)
        source_title = source_template["title"] if source_template else template.get("generated_from", "generated")
        generated_instruction = template.get("generated_instruction") or template.get("summary") or template.get("purpose") or ""
        normalized_title = generated_template_title(source_title, generated_instruction)
        template["title"] = normalized_title
        template["generated_title"] = normalized_title

    generated_prompts = db.get("generated_prompts", [])
    generated_templates = []
    existing_template_ids = {template["id"] for template in db["templates"]}
    for record in generated_prompts:
        generated_template_id = record.get("generated_template_id") or f"generated_{record.get('id', '')}"
        if not generated_template_id or generated_template_id in existing_template_ids:
            continue

        source_template = next((template for template in db["templates"] if template["id"] == record.get("template_id")), None)
        source_title = source_template["title"] if source_template else record.get("template_id", "generated")
        generated_title = record.get("generated_title") or record.get("title") or generated_template_title(source_title, record.get("instruction", ""))
        generated_templates.append({
            "id": generated_template_id,
            "title": generated_title,
            "generated_title": generated_title,
            "kind": "generated",
            "purpose": record.get("instruction") or (source_template.get("purpose") if source_template else ""),
            "summary": record.get("instruction") or "生成結果",
            "blocks": record.get("block_ids") or (source_template.get("blocks") if source_template else []),
            "generated_prompt": record.get("generated_prompt", ""),
            "generated_addition": record.get("generated_addition", ""),
            "generation_prompt_source": record.get("generation_prompt_source"),
            "generation_prompt_hash": record.get("generation_prompt_hash"),
            "generated_from": record.get("template_id"),
            "generated_instruction": record.get("instruction"),
            "generated_at": record.get("created_at"),
            "generated_request_id": record.get("id"),
        })
        existing_template_ids.add(generated_template_id)

    if generated_templates:
        db["templates"] = [*db["templates"], *generated_templates]
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
