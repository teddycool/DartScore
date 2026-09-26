"""The simulator and future resolver must share these input semantics."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SW"))

from DartScoreEngine.Game import GameService
from DartScoreEngine.Input import BoardHitCandidate, InputCoordinator
from simulate_game import simulate


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def hit(throw_id, points, status="confirmed"):
    return BoardHitCandidate(throw_id, NOW, "test", status, points,
                             camera_ids=("cam-0", "cam-1"))


class BoardHitInputTests(unittest.TestCase):
    def setUp(self):
        self.game = GameService()
        self.game.start_game()
        self.inputs = InputCoordinator(self.game)

    def test_confirmed_hit_and_duplicate_do_not_double_score(self):
        candidate = hit("one", 60)
        first = self.inputs.submit(candidate)
        self.assertEqual((first.outcome, first.score_event.total), ("scored", 60))
        self.assertEqual(self.inputs.submit(candidate), first)
        with self.assertRaises(ValueError):
            self.inputs.submit(hit("one", 20))
        self.assertEqual(self.game.snapshot().total, 60)

    def test_uncertain_correction_and_rejection_are_distinct_from_miss(self):
        self.assertEqual(self.inputs.submit(hit("uncertain", 5, "uncertain")).outcome, "pending")
        self.assertEqual(self.game.snapshot().total, 0)
        blocked = self.inputs.submit(hit("later", 20))
        self.assertEqual((blocked.outcome, blocked.reason), ("ignored", "pending_review"))
        with self.assertRaises(ValueError):
            self.inputs.resolve("uncertain", "correct", 23)
        self.assertIn("uncertain", self.inputs.pending)
        corrected = self.inputs.resolve("uncertain", "correct", 20)
        self.assertEqual(corrected.score_event.total, 20)
        self.assertEqual(self.inputs.resolve("uncertain", "correct", 20), corrected)
        with self.assertRaises(ValueError):
            self.inputs.resolve("uncertain", "reject")

        self.inputs.submit(hit("false", None, "uncertain"))
        self.assertEqual(self.inputs.resolve("false", "reject").outcome, "rejected")
        self.assertEqual(self.game.snapshot().total, 20)
        self.inputs.submit(hit("miss", 0))
        self.assertEqual(self.game.snapshot().current_turn, (20, 0))

    def test_pause_ignores_throw_id_permanently_and_health_is_separate(self):
        self.game.pause()
        candidate = hit("paused", 20)
        self.assertEqual(self.inputs.submit(candidate).outcome, "ignored")
        self.inputs.set_camera_health("cam-1", "unavailable")
        paused_state = self.game.snapshot()
        self.game.resume()
        self.assertEqual(self.inputs.submit(candidate).outcome, "ignored")
        self.assertEqual(self.game.snapshot().total, 0)
        self.assertEqual(self.inputs.camera_health["cam-1"], "unavailable")
        self.assertEqual(paused_state.current_turn, ())

    def test_pending_cannot_be_resolved_during_pause(self):
        self.inputs.submit(hit("pending", 5, "uncertain"))
        self.game.pause()
        with self.assertRaises(ValueError):
            self.inputs.resolve("pending", "confirm")
        self.game.resume()
        self.assertEqual(self.inputs.resolve("pending", "confirm").score_event.points, 5)

    def test_contract_validation(self):
        with self.assertRaises(ValueError):
            BoardHitCandidate("one", datetime(2026, 1, 1), "test", "confirmed", 20)
        with self.assertRaises(ValueError):
            hit("one", None)
        with self.assertRaises(ValueError):
            hit("one", True)
        with self.assertRaises(ValueError):
            hit("one", 20, "unknown")

    def test_example_script_reaches_expected_state(self):
        with (ROOT / "Testdata/Simulations/basic_game.jsonl").open() as lines:
            records = list(simulate(lines))
        self.assertEqual(records[-1]["game"]["total"], 80)
        self.assertEqual(records[-1]["game"]["current_turn"], ())
        self.assertEqual(records[-1]["pending_throw_ids"], [])
        self.assertEqual(records[-1]["camera_health"]["cam-1"], "unavailable")
        self.assertEqual(records[7]["result"]["outcome"], "ignored")
        self.assertEqual(records[12]["result"]["outcome"], "rejected")


if __name__ == "__main__":
    unittest.main()
