"""Contract tests for the camera- and UI-independent game core."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "SW"))

from DartScoreEngine.Game import GameService


class GameServiceTests(unittest.TestCase):
    def setUp(self):
        self.game = GameService()
        self.game.start_game()

    def test_three_darts_then_board_clear_preserves_total(self):
        first = self.game.record_hit("throw-1", 20)
        self.assertEqual((first.total, first.turn_total), (20, 20))
        self.game.record_hit("throw-2", 60)
        self.game.record_hit("throw-3", 0)  # An accepted miss uses a dart.
        self.assertIsNone(self.game.record_hit("throw-4", 5))
        self.assertEqual(self.game.snapshot().current_turn, (20, 60, 0))
        self.assertEqual(self.game.snapshot().total, 80)

        self.game.clear_board()
        self.assertEqual(self.game.snapshot().current_turn, ())
        self.assertEqual(self.game.snapshot().total, 80)
        self.game.record_hit("throw-5", 25)
        self.assertEqual(self.game.snapshot().total, 105)

    def test_duplicate_throw_id_never_counts_twice_even_after_board_clear(self):
        self.game.record_hit("same", 20)
        revision = self.game.snapshot().revision
        self.assertIsNone(self.game.record_hit("same", 20))
        self.assertEqual(self.game.snapshot().revision, revision)
        self.game.clear_board()
        self.assertIsNone(self.game.record_hit("same", 20))
        self.assertEqual(self.game.snapshot().total, 20)

    def test_paused_hits_and_board_clear_do_not_change_game(self):
        self.game.record_hit("first", 5)
        before = self.game.pause()
        self.assertIsNone(self.game.record_hit("during-pause", 20))
        self.game.clear_board()
        self.assertEqual(self.game.snapshot(), before)
        self.game.resume()
        self.assertEqual(self.game.snapshot().current_turn, (5,))
        self.game.record_hit("after-resume", 20)
        self.assertEqual(self.game.snapshot().total, 25)

    def test_validation_and_snapshot_isolation(self):
        for points in (None, True, -1, 23, 61, 2.5):
            with self.subTest(points=points), self.assertRaises(ValueError):
                self.game.record_hit("invalid", points)
        with self.assertRaises(ValueError):
            self.game.record_hit("", 20)
        with self.assertRaises(ValueError):
            self.game.start_game()
        original = self.game.snapshot()
        self.game.record_hit("valid", 20)
        self.assertEqual(original.current_turn, ())
        self.assertEqual(original.total, 0)


if __name__ == "__main__":
    unittest.main()
