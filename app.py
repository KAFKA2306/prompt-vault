from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import yaml
from build import load_db, render_app_js

ROOT = Path(__file__).resolve().parent
STATIC_PATH, ARTIFACTS_PATH = ROOT / "static", ROOT / "artifacts"
DB_PATH, CONFIG_PATH = ROOT / "db" / "prompts.json", ROOT / "config.yaml"
CONFIG = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


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
        routes = {
            "/": ("index.html", "text/html"),
            "/style.css": ("style.css", "text/css"),
            "/app.js": ("app.js", "js"),
        }
        if self.path in routes:
            name, mime = routes[self.path]
            if mime == "js":
                return self._send(200, "application/javascript", render_app_js(load_db()).encode("utf-8"))
            return self._send(200, f"{mime}; charset=utf-8", (STATIC_PATH / name).read_bytes())
        if self.path == "/api/db":
            return self._json(200, load_db())
        if self.path == "/api/config":
            return self._json(200, {"backend": "gemini", "model": CONFIG["model"]})
        if self.path.startswith("/artifacts/"):
            f = ARTIFACTS_PATH / self.path.removeprefix("/artifacts/")
            if f.exists():
                return self._send(200, "image/png", f.read_bytes())
        self.send_error(404)
        return None

    def do_POST(self) -> None:
        if self.path != "/api/prompt-generate":
            return self.send_error(404)
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        db = load_db()
        tpl = next(t for t in db["templates"] if t["id"] == req["template_id"])
        blocks = {b["id"]: b for b in db["blocks"]}
        bids = req.get("block_ids") or tpl["blocks"]
        src = "\n".join(f"- {blocks[id]['title']} ({id}): {blocks[id]['content']}" for id in bids)
        prompt = (
            CONFIG["generation_prompt"]
            .replace("{{template_title}}", tpl["title"])
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
        out = json.loads(
            json.loads(res.read().decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"]
            .strip()
            .strip("`")
            .removeprefix("json")
            .strip()
        )
        gen = "\n\n".join(
            [out.get("block_updates", {}).get(id, blocks[id]["content"]) for id in bids if id in blocks]
            + ([out["addition"]] if out.get("addition") else [])
        )
        now = datetime.now(UTC).isoformat()
        db.setdefault("generated_prompts", []).append(
            {"id": f"gen_{now}", "created_at": now, "title": out["title"], "generated_prompt": gen}
        )
        DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        self._json(200, {"request_id": now, "generated_prompt": gen})
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=8787, type=int)
    args = parser.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
