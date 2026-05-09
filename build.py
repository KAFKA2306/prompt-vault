import json
import shutil
from pathlib import Path

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from src.models import PromptDB
from config import CONFIG, ROOT, root_path

DB_PATH = root_path(CONFIG["paths"]["db"])
STATIC_PATH = root_path(CONFIG["paths"]["static"])
DIST_PATH = root_path(CONFIG["paths"]["dist"])
ARTIFACTS_PATH = root_path(CONFIG["paths"]["artifacts"])
PROMPTS_PATH = root_path(CONFIG["paths"]["prompts"]).parent


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
    # Rewrite artifact paths to .webp ONLY if Pillow is available
    if HAS_PILLOW:
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

    # Inject commit hash for observability
    try:
        import subprocess

        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        sha = "unknown"

    for f in ["index.html", "style.css"]:
        content = (STATIC_PATH / f).read_text(encoding="utf-8")
        if f == "index.html":
            content = content.replace("</body>", f"<!-- Build: {sha} -->\n</body>")
        (DIST_PATH / f).write_text(content, encoding="utf-8")

    (DIST_PATH / "app.js").write_text(render_app_js(db), encoding="utf-8")
    (DIST_PATH / "config.json").write_text(
        json.dumps({"model": CONFIG["ai"]["model"]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Copy other static assets
    for s in STATIC_PATH.rglob("*"):
        if s.is_file() and s.name not in ["index.html", "style.css", "app.js"]:
            dest = DIST_PATH / s.relative_to(STATIC_PATH)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)

    # Copy prompt templates for Pages Functions
    for s in PROMPTS_PATH.rglob("*"):
        if s.is_file():
            dest = DIST_PATH / s.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)

    # Convert to WebP if Pillow is available, otherwise copy PNG
    active_artifacts = {a.path for t in db.templates for a in t.artifacts}
    if HAS_PILLOW:
        print("Converting artifacts to WebP...")
        for s in ARTIFACTS_PATH.glob("*.png"):
            rel_path = f"artifacts/{s.name}"
            if rel_path in active_artifacts:
                dest = DIST_PATH / "artifacts" / s.with_suffix(".webp").name
                with Image.open(s) as img:
                    img.save(dest, "WEBP", quality=80)
    else:
        print("Pillow not found. Falling back to PNG copy...")
        for s in ARTIFACTS_PATH.glob("*.png"):
            rel_path = f"artifacts/{s.name}"
            if rel_path in active_artifacts:
                shutil.copy2(s, DIST_PATH / "artifacts" / s.name)


if __name__ == "__main__":
    write_dist()
