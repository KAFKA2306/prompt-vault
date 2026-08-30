import json
import shutil
from pathlib import Path

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from config import CONFIG, ROOT, root_path
from src.ideation import compile_ideation_profile
from src.prompt_db import PromptDB, load_prompt_db
from src.skills import load_skills_index

DB_PATH = root_path(CONFIG["paths"]["db"])
TWEETSDB_PATH = root_path(CONFIG["paths"]["tweetsdb"])
STATIC_PATH = root_path(CONFIG["paths"]["static"])
DIST_PATH = root_path(CONFIG["paths"]["dist"])
ARTIFACTS_PATH = root_path(CONFIG["paths"]["artifacts"])
DESIGNS_PATH = ROOT / "designs"
GENERATED_ASSETS_PATH = ROOT / "assets" / "generated"
PROMPTS_PATH = root_path(CONFIG["paths"]["prompts"]).parent
SKILLS_INDEX_PATH = root_path(CONFIG["paths"]["skills_index"])
KAFKA_SIGNAL_PATH = ROOT / "design-systems" / "kafka-signal"
KAFKA_SIGNAL_PUBLIC_FILES = (
    "components.html",
    "components.manifest.json",
    "tokens.css",
)


def load_db() -> PromptDB:
    db = load_prompt_db(DB_PATH)
    block_ids = {b.id for b in db.blocks}
    for t in db.templates:
        for bid in t.blocks:
            if bid not in block_ids:
                raise ValueError(f"unknown block: {bid}")
        for a in t.artifacts:
            if not (ROOT / a.path).exists():
                raise ValueError(f"missing artifact: {a.path}")
    return db


def is_png(path: Path) -> bool:
    return path.suffix.lower() == ".png"


def render_app_js(db: PromptDB, skills_index: list[dict[str, object]]) -> str:
    db_json = db.model_dump(exclude_none=True)
    if HAS_PILLOW:
        for t in db_json.get("templates", []):
            for a in t.get("artifacts", []):
                if a["path"].endswith(".png"):
                    a["path"] = a["path"].replace(".png", ".webp")

    return (
        (STATIC_PATH / "app.js")
        .read_text(encoding="utf-8")
        .replace("__DB_JSON__", json.dumps(db_json, ensure_ascii=False))
        .replace("__SKILLS_JSON__", json.dumps(skills_index, ensure_ascii=False))
    )


def copy_kafka_signal_catalog() -> None:
    destination = DIST_PATH / "kafka-signal"
    destination.mkdir(parents=True, exist_ok=True)
    for name in KAFKA_SIGNAL_PUBLIC_FILES:
        source = KAFKA_SIGNAL_PATH / name
        if not source.is_file():
            raise FileNotFoundError(f"missing KAFKA SIGNAL public file: {source}")
        shutil.copy2(source, destination / name)


def copy_canonical_designs() -> None:
    if not DESIGNS_PATH.is_dir():
        raise FileNotFoundError(f"missing canonical designs directory: {DESIGNS_PATH}")
    shutil.copytree(DESIGNS_PATH, DIST_PATH / "designs")


def copy_generated_assets() -> None:
    if not GENERATED_ASSETS_PATH.is_dir():
        raise FileNotFoundError(f"missing generated assets directory: {GENERATED_ASSETS_PATH}")
    shutil.copytree(GENERATED_ASSETS_PATH, DIST_PATH / "assets" / "generated")


def write_dist() -> None:
    db = load_db()
    skills_index = load_skills_index(SKILLS_INDEX_PATH)
    if DIST_PATH.exists():
        shutil.rmtree(DIST_PATH)
    DIST_PATH.mkdir(exist_ok=True)
    (DIST_PATH / "artifacts").mkdir(exist_ok=True)

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

    (DIST_PATH / "app.js").write_text(render_app_js(db, skills_index), encoding="utf-8")
    (DIST_PATH / "config.json").write_text(
        json.dumps({"model": CONFIG["model"]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for s in STATIC_PATH.rglob("*"):
        if s.is_file() and s.name not in ["index.html", "style.css", "app.js"]:
            dest = DIST_PATH / s.relative_to(STATIC_PATH)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)

    for s in PROMPTS_PATH.rglob("*"):
        if s.is_file():
            dest = DIST_PATH / s.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dest)

    skills_dest = DIST_PATH / "docs" / "SKILLS.md"
    skills_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILLS_INDEX_PATH, skills_dest)

    copy_kafka_signal_catalog()
    copy_canonical_designs()
    copy_generated_assets()

    active_artifacts = {a.path for t in db.templates for a in t.artifacts}
    if HAS_PILLOW:
        print("Converting artifacts to WebP...")
        for s in ARTIFACTS_PATH.iterdir():
            if not s.is_file():
                continue
            rel_path = f"artifacts/{s.name}"
            if rel_path in active_artifacts:
                if is_png(s):
                    dest = DIST_PATH / "artifacts" / s.with_suffix(".webp").name
                    with Image.open(s) as img:
                        img.save(dest, "WEBP", quality=80)
                else:
                    shutil.copy2(s, DIST_PATH / "artifacts" / s.name)
    else:
        print("Pillow not found. Falling back to PNG copy...")
        for s in ARTIFACTS_PATH.iterdir():
            if not s.is_file():
                continue
            rel_path = f"artifacts/{s.name}"
            if rel_path in active_artifacts:
                shutil.copy2(s, DIST_PATH / "artifacts" / s.name)

    ideation_output = DIST_PATH / "data" / "ideation_profile.json"
    profile = compile_ideation_profile(TWEETSDB_PATH, ideation_output)
    print(
        "Compiled Kafka ideation profile: "
        f"{profile['meta']['source_record_count']} records -> "
        f"{profile['meta']['exemplar_count']} exemplars"
    )


if __name__ == "__main__":
    write_dist()
