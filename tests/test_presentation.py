"""The Pi 4B proxy preserves API results and streams engine events."""

import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SW"))

from DartScoreEngine.Api.server import EngineServer
from DartScoreEngine.Input.store import DurableSession
from Presentation.server import PresentationServer


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = DurableSession(Path(self.temp.name) / "game.sqlite3")
        self.engine = EngineServer(("127.0.0.1", 0), self.store, allow_dev_input=True)
        self.engine_worker = threading.Thread(target=self.engine.serve_forever, daemon=True)
        self.engine_worker.start()
        self.front = PresentationServer(("127.0.0.1", 0), f"http://127.0.0.1:{self.engine.server_port}")
        self.front_worker = threading.Thread(target=self.front.serve_forever, daemon=True)
        self.front_worker.start()
        self.addCleanup(self.stop)

    def stop(self):
        for server, worker in ((self.front, self.front_worker), (self.engine, self.engine_worker)):
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
        self.store.close()

    def request(self, method, path, body=None, front=True):
        port = self.front.server_port if front else self.engine.server_port
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=4)
        conn.request(method, path, body=json.dumps(body).encode() if body is not None else None,
                     headers={"Content-Type": "application/json"} if body is not None else {})
        response = conn.getresponse()
        status, result = response.status, response.read()
        conn.close()
        return status, result

    def test_web_assets_and_command_proxy(self):
        for asset in ("/", "/app.js", "/style.css"):
            status, content = self.request("GET", asset)
            self.assertEqual(status, 200)
            self.assertTrue(content)
        status, body = self.request("GET", "/api/v1/state")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["phase"], "idle")
        command = {"schema_version": 1, "request_id": "start-1", "expected_revision": 0,
                   "type": "start_game", "payload": {"game_type": "simple_score"}}
        self.assertEqual(self.request("POST", "/api/v1/commands", command)[0], 200)
        self.assertEqual(self.request("POST", "/api/v1/commands", command)[0], 200)
        self.assertEqual(self.request("GET", "/api/v1/state")[1],
                         self.request("GET", "/api/v1/state", front=False)[1])
        self.assertEqual(self.request("GET", "/api/v1/dev/actions")[0], 404)
        self.assertEqual(self.request("POST", "/api/v1/commands", {**command, "request_id": "stale"})[0], 409)

    def test_sse_and_unavailable_engine(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.front.server_port, timeout=4)
        conn.request("GET", "/api/v1/events")
        response = conn.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.getheader("Content-Type"), "text/event-stream; charset=utf-8")
        self.assertTrue(response.fp.readline().startswith(b"id: "))
        self.assertEqual(response.fp.readline().strip(), b"event: game_changed")
        conn.close()
        self.front.engine_url = "http://127.0.0.1:1"
        status, body = self.request("GET", "/api/v1/state")
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(body)["error"]["code"], "engine_unavailable")


if __name__ == "__main__":
    unittest.main()
