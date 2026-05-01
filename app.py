from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from build import generated_template_title, load_db, render_app_js

ROOT = Path(__file__).resolve().parent
STATIC_PATH = ROOT / "static"
PROMPTS_DIR = ROOT / "prompts"
ARTIFACTS_PATH = ROOT / "artifacts"
PROMPTS_PATH = ROOT / "db" / "prompts.json"
CODEX_MODEL = os.environ.get("PROMPT_VAULT_CODEX_MODEL", "").strip()
GEMINI_MODEL = os.environ.get("PROMPT_VAULT_GEMINI_MODEL", "gemini-1.5-flash").strip()
DEFAULT_GENERATION_PROMPT = """あなたは既存ブロックの構造を保ちながら、必要な部分だけを最小差分で更新する編集者です。
出力は JSON のみ。キーは title, block_updates, addition の 3 つだけにする。
title は毎回新しく定義する。固定の「生成版」や `テンプレート名 / ...` 形式は使わず、今回のシチュエーションだけで短く命名する。
title は、指示文のメタ表現ではなく、実際のレイアウト用途だけで短く命名する。
block_updates は、既存ブロックのうち文脈に合わないものだけを差し替えるための配列。各要素は {\"id\": \"...\", \"content\": \"...\"} にする。
addition は、既存ブロックに入らない新しい補足だけを書く。場面そのものをここに押し込まない。できるだけ空文字にする。新しい補足が 1 つだけ必要なときに限る。
既存ブロックは原則流用する。ただし元のシチュエーションと違う場合は、該当ブロックの content を柔軟に更新する。
ブロックの役割は壊さない。特に master_style / character / brand / negative / text_style は、明確な理由がない限り維持する。
scene / pose / background / text_content / effects は、ユーザー指示に合わせて更新してよい。
既存の構造を保ち、更新するブロックだけを書き換える。全体をひとつの一般文にまとめない。
JSON 以外の説明、箇条書き、Markdown、コードフェンスは出さない。

テンプレート名: {{template_title}}
テンプレート目的: {{template_purpose}}
テンプレートID: {{template_id}}
固定ブロックID: {{block_ids}}

固定ブロック（そのまま使う）:
{{source_blocks}}

ユーザー指示:
{{instruction}}

条件:
- 既存ブロックの役割は壊さない
- ユーザー指示に合わないブロックだけを更新する
- 更新しないブロックはそのまま使う
- 新しい追加分があるときだけ addition に入れる。addition は短くする
- addition は 1 フレーズまで
- 余計な短縮をしない
- 既存の構造を維持する。addition に場面全体を書かない
- 既存ブロックで足りるなら addition は空文字にする
- タイトルに ` / ` を入れない
- タイトルに「新しい」「生成版」「template」「generated」「案」「非スタンプ」「パターン」のような汎用語を入れない
"""


def _is_codex_available() -> bool:
    return shutil.which("codex") is not None


def _is_gemini_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def _generation_backend() -> str | None:
    backend = os.environ.get("PROMPT_VAULT_GENERATION_BACKEND", "").strip().lower()
    if backend in {"codex", "gemini"}:
        if backend == "codex" and _is_codex_available():
            return "codex"
        if backend == "gemini" and _is_gemini_available():
            return "gemini"
        return None
    if _is_codex_available():
        return "codex"
    if _is_gemini_available():
        return "gemini"
    return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        self._send(code, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _render_block_content(self, block: dict[str, Any]) -> str:
        parts = [
            f"## {block['title']}",
            f"ID: {block['id']}",
            f"カテゴリ: {block['category']}",
        ]
        if block.get("tags"):
            parts.append(f"タグ: {' '.join(f'#{tag}' for tag in block['tags'])}")
        if block.get("aliases"):
            parts.append(f"別名: {', '.join(block['aliases'])}")
        if block.get("related"):
            parts.append(f"関連: {', '.join(block['related'])}")
        if block.get("variant_of"):
            parts.append(f"派生元: {block['variant_of']}")
        parts.append(block["content"])
        return "\n".join(parts)

    def _generation_prompt_path(self, backend: str) -> Path | None:
        codex_path = PROMPTS_DIR / "frontend_codex.md"
        gemini_path = PROMPTS_DIR / "frontend_gemini.md"

        if backend == "gemini" and gemini_path.is_file():
            return gemini_path
        if codex_path.is_file():
            return codex_path
        if gemini_path.is_file():
            return gemini_path
        return None

    def _load_generation_prompt_source(self, backend: str) -> tuple[str, str | None]:
        path = self._generation_prompt_path(backend)
        if path and path.is_file():
            return path.read_text(encoding="utf-8"), str(path.relative_to(ROOT))
        return DEFAULT_GENERATION_PROMPT, None

    def _render_prompt_template(self, template_source: str, context: dict[str, str]) -> str:
        rendered = template_source
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    def _render_generation_prompt(self, template: dict[str, Any], block_ids: list[str], blocks_by_id: dict[str, dict[str, Any]], instruction: str, backend: str) -> tuple[str, str | None, str]:
        selected_blocks: list[str] = []
        for block_id in block_ids:
            if block_id in blocks_by_id and block_id not in selected_blocks:
                selected_blocks.append(block_id)
        if not selected_blocks:
            selected_blocks = list(template.get("blocks", []))

        source_blocks = "\n\n".join(
            f"- {blocks_by_id[block_id]['title']} [{blocks_by_id[block_id]['category']}] ({block_id}): {blocks_by_id[block_id]['content']}"
            for block_id in selected_blocks
        )
        source, source_path = self._load_generation_prompt_source(backend)
        rendered = self._render_prompt_template(source, {
            "template_title": template["title"],
            "template_purpose": str(template.get("purpose", "")),
            "template_id": template["id"],
            "block_ids": ", ".join(selected_blocks),
            "source_blocks": source_blocks,
            "instruction": instruction.strip(),
        })
        return rendered, source_path, hashlib.sha256(source.encode("utf-8")).hexdigest()

    def _parse_generation_json(self, text: str) -> dict[str, Any] | None:
        stripped = text.strip()
        if not stripped:
            return None

        candidates = [stripped]
        if stripped.startswith("```"):
            candidate = stripped.strip("`").strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            candidates.append(candidate)

        decoder = json.JSONDecoder()
        for candidate in candidates:
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                return payload

            for index, char in enumerate(candidate):
                if char != "{":
                    continue
                try:
                    payload, _ = decoder.raw_decode(candidate[index:])
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    return payload
        return None

    def _compose_generated_prompt(
        self,
        block_ids: list[str],
        blocks_by_id: dict[str, dict[str, Any]],
        block_updates: dict[str, str],
        addition: str,
    ) -> str:
        prefix_parts: list[str] = []
        suffix_parts: list[str] = []
        for block_id in block_ids:
            block = blocks_by_id.get(block_id)
            if not block:
                continue
            content = block_updates.get(block_id, block["content"]).strip()
            if not content:
                continue
            category = str(block.get("category", ""))
            if category == "ネガティブ" or block_id.startswith("negative"):
                suffix_parts.append(content)
            else:
                prefix_parts.append(content)

        addition = addition.strip()
        if addition:
            prefix_parts.append(addition)
        parts = [part for part in [*prefix_parts, *suffix_parts] if part]
        return "\n\n".join(parts)

    def _call_codex(self, prompt: str) -> str:
        if shutil.which("codex") is None:
            raise RuntimeError("codex CLI is not installed")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            output_path = Path(tmp.name)

        command = [
            "codex",
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--output-last-message",
            str(output_path),
        ]
        if CODEX_MODEL:
            command.extend(["--model", CODEX_MODEL])

        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
            input=prompt,
            timeout=180,
        )

        try:
            if completed.returncode != 0:
                raise RuntimeError((completed.stderr or completed.stdout or "codex exec failed").strip())
            if not output_path.exists():
                raise RuntimeError("codex exec did not write a response")
            return output_path.read_text(encoding="utf-8").strip()
        finally:
            if output_path.exists():
                output_path.unlink()

    def _call_gemini(self, prompt: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("gemini backend is not configured")

        body = json.dumps({
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024,
            },
        }).encode("utf-8")

        request = Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
        )

        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))

        candidates = payload.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            for part in content.get("parts", []):
                text = part.get("text")
                if text:
                    return text.strip()
        raise RuntimeError("Gemini returned no text")

    def _append_generation_record(self, record: dict[str, Any]) -> None:
        if os.environ.get("PROMPT_VAULT_PERSIST_GENERATIONS", "1").strip() == "0":
            return

        db = load_db()
        generated_prompts = db.setdefault("generated_prompts", [])
        generated_prompts.append(record)

        tmp_path = PROMPTS_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp_path.replace(PROMPTS_PATH)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            body = (STATIC_PATH / "index.html").read_bytes()
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)
            return

        if self.path == "/style.css":
            body = (STATIC_PATH / "style.css").read_bytes()
            self._send(HTTPStatus.OK, "text/css; charset=utf-8", body)
            return

        if self.path == "/app.js":
            body = render_app_js(load_db()).encode("utf-8")
            self._send(HTTPStatus.OK, "application/javascript; charset=utf-8", body)
            return

        if self.path == "/api/db":
            body = json.dumps(load_db(), ensure_ascii=False).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        if self.path == "/api/config":
            backend = _generation_backend()
            prompt_source = None
            prompt_hash = None
            if backend:
                prompt_text, prompt_source = self._load_generation_prompt_source(backend)
                prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            body = json.dumps({
                "generation_backend": backend,
                "codex_enabled": _is_codex_available(),
                "gemini_enabled": _is_gemini_available(),
                "codex_model": CODEX_MODEL or None,
                "gemini_model": GEMINI_MODEL if _is_gemini_available() else None,
                "generation_prompt_source": prompt_source,
                "generation_prompt_hash": prompt_hash,
            }, ensure_ascii=False).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        if self.path == "/llms.txt":
            body = (STATIC_PATH / "llms.txt").read_bytes()
            self._send(HTTPStatus.OK, "text/plain; charset=utf-8", body)
            return

        if self.path == "/robots.txt":
            body = (STATIC_PATH / "robots.txt").read_bytes()
            self._send(HTTPStatus.OK, "text/plain; charset=utf-8", body)
            return

        if self.path == "/sitemap.xml":
            body = (STATIC_PATH / "sitemap.xml").read_bytes()
            self._send(HTTPStatus.OK, "application/xml; charset=utf-8", body)
            return

        if self.path == "/.well-known/ucp":
            body = (STATIC_PATH / ".well-known" / "ucp").read_bytes()
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        if self.path == "/_headers":
            body = (STATIC_PATH / "_headers").read_bytes()
            self._send(HTTPStatus.OK, "text/plain; charset=utf-8", body)
            return

        if self.path.startswith("/artifacts/"):
            rel = self.path.removeprefix("/artifacts/")
            target = ARTIFACTS_PATH / rel
            if target.is_file():
                body = target.read_bytes()
                content_type = "image/png" if target.suffix.lower() == ".png" else "application/octet-stream"
                self._send(HTTPStatus.OK, content_type, body)
                return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/prompt-generate":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            request = self._read_json_body()
            db = load_db()
            blocks_by_id = {block["id"]: block for block in db["blocks"]}
            templates_by_id = {template["id"]: template for template in db["templates"]}

            template_id = str(request.get("template_id", "")).strip()
            template = templates_by_id.get(template_id)
            if not template:
                raise ValueError("unknown template_id")

            raw_block_ids = request.get("block_ids") or []
            if isinstance(raw_block_ids, str):
                block_ids = [item.strip() for item in raw_block_ids.replace("\n", ",").split(",") if item.strip()]
            else:
                block_ids = [str(item).strip() for item in raw_block_ids if str(item).strip()]
            if not block_ids:
                block_ids = list(template.get("blocks", []))

            instruction = str(request.get("instruction", "")).strip()
            if not instruction:
                raise ValueError("instruction is required")

            backend = _generation_backend()
            if not backend:
                raise RuntimeError("no generation backend available")
            prompt, prompt_source, prompt_hash = self._render_generation_prompt(template, block_ids, blocks_by_id, instruction, backend)
            if backend == "gemini":
                generation_output = self._call_gemini(prompt)
            else:
                generation_output = self._call_codex(prompt)

            parsed_output = self._parse_generation_json(generation_output) or {}
            generated_title = str(parsed_output.get("title") or "").strip() or generated_template_title(template["title"], instruction)
            raw_block_updates = parsed_output.get("block_updates") or []
            block_updates: dict[str, str] = {}
            if isinstance(raw_block_updates, list):
                for item in raw_block_updates:
                    if not isinstance(item, dict):
                        continue
                    block_id = str(item.get("id", "")).strip()
                    content = str(item.get("content", "")).strip()
                    if block_id and content and block_id in blocks_by_id:
                        block_updates[block_id] = content
            generated_addition = str(parsed_output.get("addition") or parsed_output.get("prompt") or "").strip()
            generated_prompt = self._compose_generated_prompt(block_ids, blocks_by_id, block_updates, generated_addition)
            now = datetime.now(timezone.utc)
            request_id = now.strftime("gen_%Y%m%d_%H%M%S_%f")
            record = {
                "id": request_id,
                "created_at": now.isoformat(),
                "template_id": template_id,
                "generated_template_id": f"generated_{request_id}",
                "block_ids": block_ids,
                "instruction": instruction,
                "title": generated_title,
                "generated_title": generated_title,
                "generated_title_candidate": parsed_output.get("title"),
                "generated_block_updates": raw_block_updates,
                "generated_addition": generated_addition,
                "generation_prompt_source": prompt_source,
                "generation_prompt_hash": prompt_hash,
                "model": CODEX_MODEL if backend == "codex" and CODEX_MODEL else GEMINI_MODEL,
                "backend": backend,
                "generated_prompt": generated_prompt,
                "status": "draft",
            }
            self._append_generation_record(record)
            generated_template = {
                "id": record["generated_template_id"],
                "title": generated_title,
                "kind": "generated",
                "purpose": instruction,
                "summary": instruction,
                "blocks": block_ids,
                "generated_prompt": generated_prompt,
                "generated_from": template_id,
                "generated_instruction": instruction,
                "generated_title_candidate": parsed_output.get("title"),
                "generated_block_updates": raw_block_updates,
                "generated_addition": generated_addition,
                "generation_prompt_source": prompt_source,
                "generation_prompt_hash": prompt_hash,
                "generated_at": now.isoformat(),
                "generated_request_id": request_id,
            }
            self._send_json(HTTPStatus.OK, {
                "request_id": request_id,
                "generated_prompt": generated_prompt,
                "generated_template": generated_template,
            })
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "message": str(exc)})
        except RuntimeError as exc:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "server_error", "message": str(exc)})
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace") if getattr(exc, "fp", None) else str(exc)
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "gemini_error", "message": body})
        except URLError as exc:
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "network_error", "message": str(exc)})
        except subprocess.TimeoutExpired:
            self._send_json(HTTPStatus.GATEWAY_TIMEOUT, {"error": "timeout", "message": "codex exec timed out"})
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "message": "invalid json"})

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
