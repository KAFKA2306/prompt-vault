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
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def render_app_js(db: dict[str, Any]) -> str:
    db_json = json.dumps(db, ensure_ascii=False)
    source = (STATIC_PATH / "app.js").read_text(encoding="utf-8")
    return source.replace("__DB_JSON__", db_json)


def write_dist() -> None:
    db = load_db()
    DIST_PATH.mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "artifacts").mkdir(parents=True, exist_ok=True)
    (DIST_PATH / "index.html").write_text((STATIC_PATH / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST_PATH / "style.css").write_text((STATIC_PATH / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DIST_PATH / "app.js").write_text(render_app_js(db), encoding="utf-8")
    for source in ARTIFACTS_PATH.glob("*.png"):
        shutil.copy2(source, DIST_PATH / "artifacts" / source.name)


def main() -> None:
    write_dist()


if __name__ == "__main__":
    main()
