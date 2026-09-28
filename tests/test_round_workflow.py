"""Camera-free round through the real engine and presentation HTTP servers."""

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


class RoundWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = DurableSession(Path(temp.name) / "round.sqlite3")
        self.engine = EngineServer(("127.0.0.1", 0), self.store, allow_dev_input=True)
        self.front = PresentationServer(
            ("127.0.0.1", 0), f"http://127.0.0.1:{self.engine.server_port}"
        )
        self.workers = [threading.Thread(target=server.serve_forever, daemon=True)
                        for server in (self.engine, self.front)]
        for worker in self.workers:
            worker.start()
        self.addCleanup(self.stop)
        self.sequence = 0

    def stop(self):
        for server, worker in zip((self.front, self.engine), reversed(self.workers)):
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
        self.store.close()

    def request(self, server, method, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=4)
        try:
            raw = json.dumps(body).encode() if body is not None else None
            connection.request(method, path, body=raw,
                               headers={"Content-Type": "application/json"} if raw else {})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def state(self):
        status, state = self.request(self.front, "GET", "/api/v1/state")
        self.assertEqual(status, 200)
        return state

    def command(self, kind, payload=None, expected_status=200):
        self.sequence += 1
        status, response = self.request(self.front, "POST", "/api/v1/commands", {
            "schema_version": 1, "request_id": f"command-{self.sequence}",
            "expected_revision": self.state()["revision"], "type": kind,
            "payload": payload or {},
        })
        self.assertEqual(status, expected_status, response)
        return response

    def detect(self, throw_id, kind, points):
        status, response = self.request(self.engine, "POST", "/api/v1/dev/actions", {
            "request_id": f"capture-{throw_id}", "throw_id": throw_id,
            "type": kind, "points": points,
            "captured_at": f"2026-09-28T12:00:{self.sequence:02d}Z",
        })
        self.sequence += 1
        self.assertEqual(status, 200, response)
        return response["result"]

    def assert_round(self, scored, pending, total):
        state = self.state()
        self.assertEqual(state["players"][0]["current_turn"], scored)
        self.assertEqual([item["throw_id"] for item in state["pending_throws"]], pending)
        self.assertEqual(state["players"][0]["total"], total)
        self.assertLessEqual(len(scored) + len(pending), 3)
        return state

    def test_review_three_darts_then_collect_and_continue(self):
        self.command("start_game", {"game_type": "simple_score"})
        self.detect("one", "uncertain", 15)
        self.detect("two", "uncertain", 20)
        self.detect("three", "uncertain", 25)
        self.assert_round([], ["one", "two", "three"], 0)
        self.command("next_round", expected_status=400)
        self.command("correct_throw", {"throw_id": "three", "points": 50}, expected_status=400)
        self.command("correct_throw", {"throw_id": "one", "points": 20})
        self.assert_round([20], ["two", "three"], 20)
        self.command("reject_throw", {"throw_id": "two"})
        self.assert_round([20], ["three"], 20)
        self.command("correct_throw", {"throw_id": "three", "points": 0})
        self.assert_round([20, 0], [], 20)
        self.command("next_round", expected_status=400)
        self.detect("replacement", "hit", 25)
        self.assert_round([20, 0, 25], [], 45)
        self.assertEqual(self.detect("extra", "hit", 50)["reason"], "turn_complete")
        self.command("pause_game")
        self.assertEqual(self.detect("while-paused", "hit", 60)["reason"], "game_not_playing")
        self.assert_round([20, 0, 25], [], 45)
        self.command("next_round", expected_status=400)
        self.command("resume_game")
        self.command("next_round")
        self.assert_round([], [], 45)
        self.detect("new-round", "hit", 50)
        self.assert_round([50], [], 95)
        self.assertEqual(self.request(self.front, "GET", "/api/v1/dev/actions")[0], 404)

    def test_confirmed_dart_waits_behind_uncertain_review(self):
        self.command("start_game")
        self.detect("one", "hit", 20)
        self.detect("two", "uncertain", 15)
        self.detect("three", "hit", 25)
        state = self.assert_round([20], ["two", "three"], 20)
        self.assertEqual([item["status"] for item in state["pending_throws"]],
                         ["uncertain", "confirmed"])
        response = self.command("confirm_throw", {"throw_id": "two"})
        self.assertEqual([item["throw_id"] for item in response["result"]["following_scores"]],
                         ["three"])
        self.assert_round([20, 15, 25], [], 60)
        self.command("next_round")
        self.assert_round([], [], 60)


if __name__ == "__main__":
    unittest.main()
