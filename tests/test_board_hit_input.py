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
        queued = self.inputs.submit(hit("later", 20))
        self.assertEqual(queued.outcome, "pending")
        self.assertEqual(list(self.inputs.pending), ["uncertain", "later"])
        with self.assertRaises(ValueError):
            self.inputs.resolve("uncertain", "correct", 23)
        self.assertIn("uncertain", self.inputs.pending)
        corrected = self.inputs.resolve("uncertain", "correct", 20)
        self.assertEqual(corrected.score_event.total, 20)
        self.assertEqual([event.throw_id for event in corrected.following_scores], ["later"])
        self.assertEqual(self.inputs.resolve("uncertain", "correct", 20), corrected)
        with self.assertRaises(ValueError):
            self.inputs.resolve("uncertain", "reject")

        self.assertEqual(self.inputs.resolve("later", "confirm").score_event.total, 40)

        self.inputs.submit(hit("false", None, "uncertain"))
        self.assertEqual(self.inputs.resolve("false", "reject").outcome, "rejected")
        self.assertEqual(self.game.snapshot().total, 40)
        self.inputs.submit(hit("miss", 0))
        self.assertEqual(self.game.snapshot().current_turn, (20, 20, 0))

    def test_three_uncertain_darts_can_all_be_corrected_after_capture(self):
        for index in range(3):
            self.assertEqual(self.inputs.submit(hit(f"dart-{index}", 5, "uncertain")).outcome, "pending")
        self.assertEqual(self.inputs.submit(hit("fourth", 20)).reason, "turn_complete")
        self.assertEqual(self.game.snapshot().current_turn, ())
        with self.assertRaisesRegex(ValueError, "dart order"):
            self.inputs.resolve("dart-2", "correct", 25)
        for index, score in enumerate((20, 0, 25)):
            self.assertEqual(self.inputs.resolve(f"dart-{index}", "correct", score).outcome, "scored")
        self.assertEqual(self.game.snapshot().current_turn, (20, 0, 25))
        self.assertEqual(self.game.snapshot().total, 45)

    def test_confirmed_third_dart_scores_when_second_review_is_resolved(self):
        self.inputs.submit(hit("first", 20))
        self.inputs.submit(hit("second", 15, "uncertain"))
        self.assertEqual(self.inputs.submit(hit("third", 25)).outcome, "pending")
        self.assertEqual(list(self.inputs.pending), ["second", "third"])
        result = self.inputs.resolve("second", "confirm")
        self.assertEqual([event.points for event in result.following_scores], [25])
        self.assertEqual(self.game.snapshot().current_turn, (20, 15, 25))
        self.assertEqual(self.inputs.pending, {})
        self.assertEqual(self.inputs.submit(hit("third", 25)).outcome, "scored")

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
