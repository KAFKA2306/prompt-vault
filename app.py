from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from build import render_static

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "prompts.json"


def load_db() -> dict[str, Any]:
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            body = render_static(load_db()).encode("utf-8")
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)
            return

        if self.path == "/api/db":
            body = json.dumps(load_db(), ensure_ascii=False).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Prompt Vault running on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
