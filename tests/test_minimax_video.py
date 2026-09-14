import importlib.util
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "minimax_video", ROOT / "scripts" / "minimax_video.py"
)
MINIMAX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MINIMAX)


class MiniMaxFixtureHandler(BaseHTTPRequestHandler):
    queries = 0
    requests = []
    fail_task = False

    def log_message(self, *_args):
        pass

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        self.__class__.requests.append(("POST", self.path, payload, self.headers.get("Authorization")))
        if self.path == "/v1/video_generation":
            self._json({"task_id": "task-123", "base_resp": {"status_code": 0, "status_msg": "success"}})
        else:
            self._json({"error": "unexpected"}, 404)

    def do_GET(self):
        self.__class__.requests.append(("GET", self.path, None, self.headers.get("Authorization")))
        if self.path == "/v1/query/video_generation?task_id=task-123":
            self.__class__.queries += 1
            if self.__class__.fail_task:
                self._json({"task_id": "task-123", "status": "Fail", "base_resp": {"status_code": 0}})
            elif self.__class__.queries == 1:
                self._json({"task_id": "task-123", "status": "Processing", "base_resp": {"status_code": 0}})
            else:
                self._json({"task_id": "task-123", "status": "Success", "file_id": "file-456", "base_resp": {"status_code": 0}})
        elif self.path == "/v1/files/retrieve?file_id=file-456":
            self._json({
                "file": {
                    "file_id": "file-456",
                    "filename": "output_aigc.mp4",
                    "purpose": "video_generation",
                    "download_url": f"http://127.0.0.1:{self.server.server_port}/download/video.mp4",
                },
                "base_resp": {"status_code": 0, "status_msg": "success"},
            })
        elif self.path == "/download/video.mp4":
            body = b"fake-mp4-content"
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._json({"error": "unexpected"}, 404)


class MiniMaxVideoTest(unittest.TestCase):
    def setUp(self):
        MiniMaxFixtureHandler.queries = 0
        MiniMaxFixtureHandler.requests = []
        MiniMaxFixtureHandler.fail_task = False
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), MiniMaxFixtureHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.api_base = f"http://127.0.0.1:{self.server.server_port}"
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / "clip.mp4"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()
        self.temp.cleanup()

    def test_cli_creates_polls_downloads_and_records_generation(self):
        with patch.dict(os.environ, {"MINIMAX_API_KEY": "fixture-key"}, clear=False):
            code = MINIMAX.main([
                "a paper fox walking through rain",
                "--api-base", self.api_base,
                "--output", str(self.output),
                "--poll-interval", "0",
                "--poll-timeout", "5",
            ])
        self.assertEqual(0, code)
        self.assertEqual(b"fake-mp4-content", self.output.read_bytes())
        metadata = json.loads(self.output.with_suffix(".mp4.json").read_text(encoding="utf-8"))
        self.assertEqual("MiniMax-Hailuo-2.3", metadata["model"])
        self.assertEqual("a paper fox walking through rain", metadata["prompt"])
        self.assertEqual(6, metadata["duration"])
        self.assertEqual("768P", metadata["resolution"])
        self.assertEqual("task-123", metadata["task_id"])
        self.assertEqual("file-456", metadata["file_id"])
        self.assertEqual("Success", metadata["status"])
        self.assertEqual(64, len(metadata["sha256"]))

        post = MiniMaxFixtureHandler.requests[0]
        self.assertEqual("POST", post[0])
        self.assertEqual("/v1/video_generation", post[1])
        self.assertEqual("Bearer fixture-key", post[3])
        self.assertEqual(
            {
                "model": "MiniMax-Hailuo-2.3",
                "prompt": "a paper fox walking through rain",
                "duration": 6,
                "resolution": "768P",
            },
            post[2],
        )
        paths = [request[1] for request in MiniMaxFixtureHandler.requests]
        self.assertGreaterEqual(paths.count("/v1/query/video_generation?task_id=task-123"), 2)
        self.assertIn("/v1/files/retrieve?file_id=file-456", paths)
        self.assertIn("/download/video.mp4", paths)

    def test_failed_task_returns_nonzero_and_writes_no_completed_artifact(self):
        MiniMaxFixtureHandler.fail_task = True
        with patch.dict(os.environ, {"MINIMAX_API_KEY": "fixture-key"}, clear=False):
            code = MINIMAX.main([
                "failure fixture",
                "--api-base", self.api_base,
                "--output", str(self.output),
                "--poll-interval", "0",
                "--poll-timeout", "5",
            ])
        self.assertEqual(1, code)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.output.with_suffix(".mp4.json").exists())

    def test_rejects_invalid_hailuo_duration_resolution_before_network(self):
        client = MINIMAX.MiniMaxClient("fixture-key", api_base=self.api_base)
        with self.assertRaisesRegex(MINIMAX.MiniMaxError, "10-second Hailuo videos require 768P"):
            MINIMAX.run_generation(
                client,
                model="MiniMax-Hailuo-2.3",
                prompt="invalid contract",
                duration=10,
                resolution="1080P",
                output=self.output,
                metadata=self.output.with_suffix(".json"),
                poll_interval=0,
                poll_timeout=1,
            )
        self.assertEqual([], MiniMaxFixtureHandler.requests)

    def test_missing_api_key_is_nonzero(self):
        with patch.dict(os.environ, {}, clear=True):
            code = MINIMAX.main(["no key", "--api-base", self.api_base, "--output", str(self.output)])
        self.assertEqual(1, code)
        self.assertEqual([], MiniMaxFixtureHandler.requests)


if __name__ == "__main__":
    unittest.main()
