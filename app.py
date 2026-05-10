from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.request import Request, urlopen

from build import load_db, render_app_js
from config import CONFIG, ROOT, root_path
from src.skills_index import load_skills_index

STATIC_PATH = root_path(CONFIG["paths"]["static"])
ARTIFACTS_PATH = root_path(CONFIG["paths"]["artifacts"])
DIST_PATH = root_path(CONFIG["paths"]["dist"])
DB_PATH = root_path(CONFIG["paths"]["db"])
CODEX_PATH = root_path(CONFIG["paths"]["prompts"])
SKILLS_INDEX_PATH = root_path(CONFIG["paths"]["skills_index"])


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, mime: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data: dict[str, Any]) -> None:
        self._send(code, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self) -> None:
        if self.path == "/api/db":
            return self._json(200, load_db().model_dump(exclude_none=True))

        if self.path == "/api/skills":
            return self._json(200, {"sections": load_skills_index(SKILLS_INDEX_PATH)})

        if self.path == "/docs/SKILLS.md":
            return self._send(200, "text/markdown; charset=utf-8", SKILLS_INDEX_PATH.read_bytes())

        # Static files
        p = self.path.split("?")[0]
        if p == "/":
            p = "/index.html"
        f = STATIC_PATH / p.lstrip("/")

        if f.exists() and f.is_file():
            ext = f.suffix.lower()
            mime = {
                ".html": "text/html",
                ".js": "application/javascript",
                ".css": "text/css",
                ".svg": "image/svg+xml",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".json": "application/json",
                ".webp": "image/webp",
                ".wav": "audio/wav",
            }.get(ext, "application/octet-stream")

            content = render_app_js(load_db(), load_skills_index(SKILLS_INDEX_PATH)).encode("utf-8") if p == "/app.js" else f.read_bytes()
            return self._send(200, mime, content)

        # Artifacts
        if p.startswith("/artifacts/"):
            # Try dist/ first, then root
            af = DIST_PATH / p.lstrip("/")
            if not af.exists():
                af = ROOT / p.lstrip("/")

            if af.exists():
                ext = af.suffix.lower()
                mime = {
                    ".webp": "image/webp",
                    ".png": "image/png",
                    ".wav": "audio/wav",
                }.get(ext, "application/octet-stream")
                return self._send(200, mime, af.read_bytes())

        self.send_error(404)
        return None

    def do_POST(self) -> None:
        if self.path != "/api/prompt-generate":
            return self.send_error(404)
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        db = load_db()
        tpl = next(t for t in db.templates if t.id == req["template_id"])
        blocks = {b.id: b for b in db.blocks}
        bids = req.get("block_ids") or tpl.blocks
        src = "\n".join(f"- {blocks[id].title} ({id}): {blocks[id].content}" for id in bids if id in blocks)
        prompt = (
            CODEX_PATH.read_text(encoding="utf-8")
            .replace("{{template_title}}", tpl.title)
            .replace("{{source_blocks}}", src)
            .replace("{{instruction}}", req["instruction"])
        )
        res = urlopen(
            Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{CONFIG['model']}:generateContent",
                data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            )
        )
        data = json.loads(res.read().decode("utf-8"))
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip().strip("`").removeprefix("json").strip()
        out = json.loads(raw)
        gen = "\n\n".join(
            [out.get("block_updates", {}).get(id, blocks[id].content) for id in bids if id in blocks]
            + ([out["addition"]] if out.get("addition") else [])
        )
        now = datetime.now(UTC).isoformat()
        res_data = {
            "id": f"gen_{now}",
            "title": out["title"],
            "kind": "generated",
            "blocks": bids,
            "generated_prompt": gen,
            "purpose": tpl.purpose,
            "created_at": now,
        }
        db.templates.append(res_data)
        DB_PATH.write_text(json.dumps(db.model_dump(exclude_none=True), ensure_ascii=False, indent=2), encoding="utf-8")
        return self._json(200, {"request_id": now, "generated_prompt": gen})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=CONFIG["app"]["port"], type=int)
    args = parser.parse_args()
    ThreadingHTTPServer((CONFIG["app"]["host"], args.port), Handler).serve_forever()
