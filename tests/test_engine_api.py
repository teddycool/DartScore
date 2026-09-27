"""Exercise the HTTP boundary without a camera or browser."""

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


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "session.sqlite3"
        self.store = DurableSession(self.db)
        self.server = EngineServer(("127.0.0.1", 0), self.store, allow_dev_input=True)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=2)
        self.store.close()

    def request(self, method, path, data=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        raw = json.dumps(data).encode() if data is not None else None
        conn.request(method, path, body=raw,
                     headers={"Content-Type": "application/json"} if raw else {})
        response = conn.getresponse()
        status, payload = response.status, json.loads(response.read())
        conn.close()
        return status, payload

    def command(self, kind, request_id, revision, payload=None):
        return self.request("POST", "/api/v1/commands", {
            "schema_version": 1, "type": kind, "request_id": request_id,
            "expected_revision": revision, "payload": payload or {}})

    def test_commands_conflicts_retries_and_restart(self):
        status, start = self.command("start_game", "start", 0, {"game_type": "simple_score"})
        self.assertEqual(status, 200)
        self.assertEqual(start["revision"], 1)
        self.assertEqual(self.command("start_game", "start", 0, {"game_type": "simple_score"})[0], 200)
        self.assertEqual(self.command("pause_game", "stale", 0)[0], 409)
        self.assertEqual(self.command("start_game", "301", 1, {"game_type": "301"})[0], 400)
        _, paused = self.command("pause_game", "pause", 1)
        self.assertEqual(paused["revision"], 2)
        _, state = self.request("GET", "/api/v1/state")
        self.assertEqual(state["phase"], "paused")
        game_id = state["game_id"]
        self.assertEqual(self.request("GET", "/api/v1/health")[1]["storage"]["image_write_status"], "not_integrated")
        self.stop()
        with DurableSession(self.db) as reopened:
            self.assertEqual(reopened.game_id, game_id)
            self.assertEqual(reopened.state()["game"]["revision"], 2)

    def test_pending_correction_and_sse(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request("GET", "/api/v1/events")
        stream = connection.getresponse()
        self.assertEqual(stream.status, 200)
        self.assertIn(b"event: game_changed", stream.fp.readline() + stream.fp.readline())
        self.command("start_game", "start", 0)
        self.request("POST", "/api/v1/dev/actions", {
            "request_id": "candidate", "type": "uncertain", "throw_id": "throw-1",
            "captured_at": "2026-09-26T12:00:00Z", "source": "test", "points": 20})
        self.assertEqual(self.request("GET", "/api/v1/state")[1]["players"][0]["total"], 0)
        _, scored = self.command("correct_throw", "correct", 1, {"throw_id": "throw-1", "points": 50})
        self.assertEqual(scored["revision"], 2)
        self.assertEqual(self.request("GET", "/api/v1/state")[1]["players"][0]["total"], 50)
        self.assertEqual(self.command("reject_throw", "reject", 2, {"throw_id": "throw-1"})[0], 400)
        connection.close()

    def test_three_dart_round_advances_only_after_review_and_survives_restart(self):
        self.command("start_game", "start", 0)
        self.assertEqual(self.command("next_round", "too-early", 1)[0], 400)

        def candidate(request_id, kind, points):
            return self.request("POST", "/api/v1/dev/actions", {
                "request_id": request_id, "type": kind, "throw_id": request_id,
                "captured_at": "2026-09-26T12:00:00Z", "points": points})

        candidate("one", "hit", 20)
        candidate("two", "hit", 0)
        candidate("three", "uncertain", 15)
        self.assertEqual(self.command("next_round", "review-first", 3)[0], 400)
        self.assertEqual(candidate("blocked", "hit", 5)[1]["result"]["reason"], "turn_complete")
        _, resolved = self.command("correct_throw", "resolve", 3, {"throw_id": "three", "points": 25})
        self.assertEqual(resolved["revision"], 4)
        self.assertEqual(self.request("GET", "/api/v1/state")[1]["players"][0]["current_turn"], [20, 0, 25])
        self.assertEqual(candidate("fourth", "hit", 60)[1]["result"]["reason"], "turn_complete")
        self.command("pause_game", "pause", 4)
        self.assertEqual(self.command("next_round", "while-paused", 5)[0], 400)
        self.command("resume_game", "resume", 5)
        self.assertEqual(self.command("next_round", "stale", 5)[0], 409)
        status, advanced = self.command("next_round", "advance", 6)
        self.assertEqual((status, advanced["revision"], advanced["result"]["outcome"]),
                         (200, 7, "round_started"))
        self.assertEqual(self.command("next_round", "advance", 6)[1]["revision"], 7)
        state = self.request("GET", "/api/v1/state")[1]
        self.assertEqual((state["players"][0]["current_turn"], state["players"][0]["total"]), ([], 45))
        self.assertEqual(candidate("new", "hit", 50)[1]["revision"], 8)
        self.stop()
        with DurableSession(self.db) as reopened:
            self.assertEqual(reopened.state()["game"]["current_turn"], (50,))
            self.assertEqual(reopened.state()["game"]["total"], 95)

    def test_three_uncertain_darts_are_reviewable_in_order_after_restart(self):
        self.command("start_game", "start", 0)
        for index in range(3):
            status, response = self.request("POST", "/api/v1/dev/actions", {
                "request_id": f"capture-{index}", "type": "uncertain", "throw_id": f"dart-{index}",
                "captured_at": "2026-09-26T12:00:00Z", "points": 5})
            self.assertEqual((status, response["result"]["outcome"]), (200, "pending"))
        _, state = self.request("GET", "/api/v1/state")
        self.assertEqual([item["throw_id"] for item in state["pending_throws"]],
                         ["dart-0", "dart-1", "dart-2"])
        self.assertEqual(state["players"][0]["current_turn"], [])
        self.assertEqual(self.command("correct_throw", "out-of-order", 1,
                                      {"throw_id": "dart-2", "points": 25})[0], 400)
        for index, points in enumerate((20, 0, 25)):
            status, response = self.command("correct_throw", f"review-{index}", 1 + index,
                                            {"throw_id": f"dart-{index}", "points": points})
            self.assertEqual((status, response["result"]["outcome"]), (200, "scored"))
        _, state = self.request("GET", "/api/v1/state")
        self.assertEqual(state["pending_throws"], [])
        self.assertEqual((state["players"][0]["current_turn"], state["players"][0]["total"]),
                         ([20, 0, 25], 45))
        self.stop()
        with DurableSession(self.db) as reopened:
            self.assertEqual(reopened.state()["game"]["current_turn"], (20, 0, 25))

    def test_confirmed_third_dart_commits_after_second_review(self):
        self.command("start_game", "start", 0)
        for index, kind, points in ((1, "hit", 20), (2, "uncertain", 15), (3, "hit", 25)):
            self.request("POST", "/api/v1/dev/actions", {
                "request_id": f"capture-{index}", "type": kind, "throw_id": f"dart-{index}",
                "captured_at": "2026-09-26T12:00:00Z", "points": points})
        _, state = self.request("GET", "/api/v1/state")
        self.assertEqual([item["status"] for item in state["pending_throws"]],
                         ["uncertain", "confirmed"])
        _, response = self.command("confirm_throw", "confirm-second", 2, {"throw_id": "dart-2"})
        self.assertEqual([item["throw_id"] for item in response["result"]["following_scores"]], ["dart-3"])
        _, state = self.request("GET", "/api/v1/state")
        self.assertEqual(state["pending_throws"], [])
        self.assertEqual((state["players"][0]["current_turn"], state["players"][0]["total"]),
                         ([20, 15, 25], 60))
        self.assertEqual([event["throw_id"] for event in self.store.accepted_score_events()],
                         ["dart-1", "dart-2", "dart-3"])


if __name__ == "__main__":
    unittest.main()
