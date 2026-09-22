#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_API_BASE = "https://api.minimax.io"
TERMINAL_SUCCESS = "Success"
TERMINAL_FAILURE = "Fail"
ACTIVE_STATUSES = {"Preparing", "Queueing", "Processing"}


class MiniMaxError(RuntimeError):
    pass


class MiniMaxClient:
    def __init__(self, api_key: str, api_base: str = DEFAULT_API_BASE, timeout: float = 60.0):
        if not api_key.strip():
            raise MiniMaxError("MINIMAX_API_KEY is required")
        self.api_key = api_key
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.api_base}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MiniMaxError(f"MiniMax HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise MiniMaxError(f"MiniMax request failed: {exc.reason}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MiniMaxError("MiniMax returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise MiniMaxError("MiniMax returned a non-object JSON response")
        base_resp = data.get("base_resp")
        if isinstance(base_resp, dict) and base_resp.get("status_code") not in (None, 0):
            raise MiniMaxError(
                f"MiniMax API error {base_resp.get('status_code')}: {base_resp.get('status_msg', 'unknown error')}"
            )
        return data

    def create_text_video(self, *, model: str, prompt: str, duration: int, resolution: str) -> str:
        data = self._request_json(
            "POST",
            "/v1/video_generation",
            payload={
                "model": model,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
            },
        )
        task_id = data.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise MiniMaxError("MiniMax create response did not contain task_id")
        return task_id

    def query_video(self, task_id: str) -> dict[str, Any]:
        return self._request_json(
            "GET", "/v1/query/video_generation", query={"task_id": task_id}
        )

    def retrieve_file(self, file_id: str) -> dict[str, Any]:
        data = self._request_json(
            "GET", "/v1/files/retrieve", query={"file_id": file_id}
        )
        file_data = data.get("file")
        if not isinstance(file_data, dict):
            raise MiniMaxError("MiniMax file response did not contain file metadata")
        return file_data

    def download(self, url: str, output: Path) -> str:
        request = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                content = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MiniMaxError(f"Video download HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise MiniMaxError(f"Video download failed: {exc.reason}") from exc
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(content)
        return hashlib.sha256(content).hexdigest()


def validate_generation_args(model: str, prompt: str, duration: int, resolution: str) -> None:
    if not prompt.strip():
        raise MiniMaxError("prompt must not be empty")
    if len(prompt) > 2000:
        raise MiniMaxError("prompt must be at most 2000 characters")
    if duration not in {6, 10}:
        raise MiniMaxError("duration must be 6 or 10 seconds")
    if resolution not in {"720P", "768P", "1080P"}:
        raise MiniMaxError("resolution must be 720P, 768P, or 1080P")
    if model in {"MiniMax-Hailuo-2.3", "MiniMax-Hailuo-02"}:
        if duration == 10 and resolution != "768P":
            raise MiniMaxError("10-second Hailuo videos require 768P")
        if duration == 6 and resolution not in {"768P", "1080P"}:
            raise MiniMaxError("6-second Hailuo videos require 768P or 1080P")
    elif duration != 6 or resolution not in {"720P", "1080P"}:
        raise MiniMaxError("non-Hailuo text-to-video models support 6 seconds at 720P or 1080P")


def run_generation(
    client: MiniMaxClient,
    *,
    model: str,
    prompt: str,
    duration: int,
    resolution: str,
    output: Path,
    metadata: Path,
    poll_interval: float,
    poll_timeout: float,
    sleep_fn=time.sleep,
    monotonic_fn=time.monotonic,
) -> dict[str, Any]:
    validate_generation_args(model, prompt, duration, resolution)
    task_id = client.create_text_video(
        model=model, prompt=prompt, duration=duration, resolution=resolution
    )
    deadline = monotonic_fn() + poll_timeout
    status = ""
    file_id = ""
    while True:
        state = client.query_video(task_id)
        status = str(state.get("status", ""))
        if status == TERMINAL_SUCCESS:
            file_id = str(state.get("file_id", ""))
            if not file_id:
                raise MiniMaxError("successful task did not contain file_id")
            break
        if status == TERMINAL_FAILURE:
            raise MiniMaxError(f"MiniMax video task {task_id} failed")
        if status not in ACTIVE_STATUSES:
            raise MiniMaxError(f"MiniMax video task {task_id} returned unknown status: {status!r}")
        if monotonic_fn() >= deadline:
            raise MiniMaxError(f"MiniMax video task {task_id} timed out after {poll_timeout:g}s")
        sleep_fn(poll_interval)

    file_data = client.retrieve_file(file_id)
    download_url = file_data.get("download_url")
    if not isinstance(download_url, str) or not download_url:
        raise MiniMaxError("MiniMax file metadata did not contain download_url")
    sha256 = client.download(download_url, output)
    record = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "task_id": task_id,
        "file_id": file_id,
        "status": status,
        "output": str(output),
        "sha256": sha256,
    }
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and download a MiniMax text-to-video clip without a GUI."
    )
    parser.add_argument("prompt", help="Text-to-video prompt (max 2000 characters)")
    parser.add_argument("--model", default="MiniMax-Hailuo-2.3")
    parser.add_argument("--duration", type=int, default=6)
    parser.add_argument("--resolution", default="768P")
    parser.add_argument("--output", type=Path, default=Path("output/minimax-video.mp4"))
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--poll-interval", type=float, default=10.0)
    parser.add_argument("--poll-timeout", type=float, default=1800.0)
    parser.add_argument("--request-timeout", type=float, default=60.0)
    parser.add_argument(
        "--api-base",
        default=os.environ.get("MINIMAX_API_BASE", DEFAULT_API_BASE),
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    metadata = args.metadata or args.output.with_suffix(args.output.suffix + ".json")
    try:
        client = MiniMaxClient(
            os.environ.get("MINIMAX_API_KEY", ""),
            api_base=args.api_base,
            timeout=args.request_timeout,
        )
        record = run_generation(
            client,
            model=args.model,
            prompt=args.prompt,
            duration=args.duration,
            resolution=args.resolution,
            output=args.output,
            metadata=metadata,
            poll_interval=args.poll_interval,
            poll_timeout=args.poll_timeout,
        )
    except MiniMaxError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
