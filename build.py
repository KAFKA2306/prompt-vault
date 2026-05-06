import json
import shutil
from pathlib import Path
from PIL import Image

from src.models import PromptDB

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
    return db


def render_app_js(db: PromptDB) -> str:
    db_json = db.model_dump(exclude_none=True)
    # Rewrite artifact paths to .webp for the frontend
    for t in db_json.get("templates", []):
        for a in t.get("artifacts", []):
            if a["path"].endswith(".png"):
                a["path"] = a["path"].replace(".png", ".webp")

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

    # Copy other static assets
    for s in STATIC_PATH.rglob("*"):
        if s.is_file() and s.name not in ["index.html", "style.css", "app.js"]:
            dest = DIST_PATH / s.relative_to(STATIC_PATH)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)

    # Convert and copy artifacts to WebP
    print("Converting artifacts to WebP...")
    active_artifacts = {a.path for t in db.templates for a in t.artifacts}
    for s in ARTIFACTS_PATH.glob("*.png"):
        rel_path = f"artifacts/{s.name}"
        if rel_path in active_artifacts:
            dest = DIST_PATH / "artifacts" / s.with_suffix(".webp").name
            with Image.open(s) as img:
                img.save(dest, "WEBP", quality=80)


if __name__ == "__main__":
    write_dist()
