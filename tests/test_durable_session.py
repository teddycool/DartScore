"""Restart and failure tests for the SQLite game action journal."""

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SW"))

from DartScoreEngine.Input.store import DurableSession, StorageCorruptionError
from simulate_game import simulate


STAMP = "2026-09-26T10:00:00+00:00"


def hit(throw_id, points, uncertain=False):
    return {"type": "uncertain" if uncertain else "hit", "throw_id": throw_id,
            "points": points, "captured_at": STAMP, "source": "test",
            "camera_ids": ["cam-0", "cam-1"], "evidence_refs": ["image-1"]}


class DurableSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "game.sqlite3"

    def test_restart_recovers_score_pending_health_and_throw_ids(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            scored = store.apply("hit-1", hit("throw-1", 20))
            self.assertNotIn("following_scores", scored)  # Old journal result shape remains valid.
            store.apply("camera-1", {"type": "camera", "camera_id": "cam-1", "state": "degraded"})
            store.apply("pending", hit("throw-2", 5, uncertain=True))
            self.assertEqual(store.state()["game"]["total"], 20)

        with DurableSession(self.db) as store:
            self.assertEqual(store.state()["game"]["total"], 20)
            self.assertIn("throw-2", store.state()["pending"])
            self.assertEqual(store.state()["pending"]["throw-2"]["evidence_refs"], ("image-1",))
            self.assertEqual(store.state()["camera_health"]["cam-1"], "degraded")
            self.assertEqual(store.apply("hit-1", hit("throw-1", 20)), scored)
            with self.assertRaises(ValueError):
                store.apply("hit-1", hit("throw-1", 60))
            corrected = store.apply("correct", {"type": "correct", "throw_id": "throw-2", "points": 60})
            self.assertEqual(corrected["score_event"]["total"], 80)
            self.assertEqual(len(store.accepted_score_events()), 2)

        with DurableSession(self.db) as store:
            self.assertEqual(store.state()["game"]["total"], 80)
            self.assertEqual(store.state()["pending"], {})
            duplicate = store.apply("same-throw-new-request", hit("throw-1", 20))
            self.assertEqual(duplicate["score_event"]["total"], 20)
            self.assertEqual(store.state()["game"]["total"], 80)
            self.assertEqual(len(store.accepted_score_events()), 2)

    def test_paused_throw_stays_ignored_after_restart(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            store.apply("pause", {"type": "pause"})
            ignored = store.apply("paused-hit", hit("throw-paused", 20))
            self.assertEqual(ignored["outcome"], "ignored")
        with DurableSession(self.db) as store:
            store.apply("resume", {"type": "resume"})
            again = store.apply("duplicate-id", hit("throw-paused", 20))
            self.assertEqual(again["outcome"], "ignored")
            self.assertEqual(store.state()["game"]["total"], 0)

    def test_three_pending_darts_survive_restart_and_rejection_frees_slot(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            for index in range(3):
                self.assertEqual(store.apply(f"candidate-{index}", hit(f"dart-{index}", 5, True))["outcome"],
                                 "pending")
            self.assertEqual(store.apply("fourth", hit("dart-fourth", 20))["reason"], "turn_complete")
        with DurableSession(self.db) as store:
            self.assertEqual(list(store.state()["pending"]), ["dart-0", "dart-1", "dart-2"])
            store.apply("reject-first", {"type": "reject", "throw_id": "dart-0"})
            self.assertEqual(store.apply("replacement", hit("replacement", 20))["outcome"], "pending")
            for index in (1, 2):
                store.apply(f"correct-{index}", {"type": "correct", "throw_id": f"dart-{index}",
                                                 "points": 25})
            store.apply("confirm-replacement", {"type": "confirm", "throw_id": "replacement"})
            self.assertEqual(store.state()["game"]["current_turn"], (25, 25, 20))

    def test_legacy_hit_ignored_during_review_remains_ignored_on_replay(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            store.apply("uncertain", hit("first", 5, True))
            store.apply("later", hit("old-ignored", 20))
        # This is the result shape saved by the previous one-pending-at-a-time engine.
        old_result = {"outcome": "ignored", "throw_id": "old-ignored",
                      "score_event": None, "reason": "pending_review"}
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE actions SET result=? WHERE request_id='later'",
                         (json.dumps(old_result, sort_keys=True, separators=(",", ":")),))
        with DurableSession(self.db) as store:
            self.assertEqual(list(store.state()["pending"]), ["first"])
            store.apply("confirm-first", {"type": "confirm", "throw_id": "first"})
            self.assertEqual(store.apply("repeat-old", hit("old-ignored", 20))["reason"],
                             "pending_review")
            self.assertEqual(store.state()["game"]["total"], 5)

    def test_failed_write_restores_memory_and_allows_retry(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            store._conn.execute("""CREATE TEMP TRIGGER refuse_hit BEFORE INSERT ON actions
                WHEN NEW.request_id='blocked' BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
            store._conn.commit()
            with self.assertRaises(sqlite3.DatabaseError):
                store.apply("blocked", hit("throw-1", 20))
            self.assertEqual(store.state()["game"]["total"], 0)
            store._conn.execute("DROP TRIGGER refuse_hit")
            store.apply("blocked", hit("throw-1", 20))
            self.assertEqual(store.state()["game"]["total"], 20)

    def test_single_writer_lock_and_corrupt_journal_fail_closed(self):
        with DurableSession(self.db) as store:
            store.apply("start", {"type": "start"})
            with self.assertRaises(BlockingIOError):
                DurableSession(self.db)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE actions SET result=? WHERE request_id='start'",
                         (json.dumps({"outcome": "wrong"}),))
        with self.assertRaises(StorageCorruptionError):
            DurableSession(self.db)

    def test_simulator_script_can_reopen_database(self):
        script = ROOT / "Testdata/Simulations/basic_game.jsonl"
        with DurableSession(self.db) as store, script.open() as lines:
            records = list(simulate(lines, store))
            self.assertEqual(records[-1]["game"]["total"], 80)
        with DurableSession(self.db) as store:
            self.assertEqual(store.state()["game"]["total"], 80)
            self.assertEqual(len(store.accepted_score_events()), 3)


if __name__ == "__main__":
    unittest.main()
