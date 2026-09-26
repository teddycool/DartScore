"""The original one-player accumulating game, extracted from PlayStateLoop.

No camera, UI, GPIO, persistence, or network dependency belongs here. More
game types can be introduced behind this boundary in later changes.
"""

from dataclasses import dataclass


VALID_DART_POINTS = frozenset(
    {0, 25, 50}
    | set(range(1, 21))
    | {2 * n for n in range(1, 21)}
    | {3 * n for n in range(1, 21)}
)


@dataclass(frozen=True)
class GameSnapshot:
    game_type: str
    phase: str
    player_id: str
    total: int
    current_turn: tuple[int, ...]
    revision: int


@dataclass(frozen=True)
class ScoreEvent:
    throw_id: str
    points: int
    total: int
    turn_total: int
    revision: int


class GameService:
    """Single-player simple-score game with at most three darts per turn."""

    def __init__(self):
        self._phase = "idle"
        self._total = 0
        self._turn: list[int] = []
        self._revision = 0
        self._accepted_throw_ids: set[str] = set()

    def start_game(self) -> GameSnapshot:
        if self._phase in ("playing", "paused"):
            raise ValueError("A game is already active")
        self._phase = "playing"
        self._total = 0
        self._turn.clear()
        self._accepted_throw_ids.clear()
        self._revision += 1
        return self.snapshot()

    def pause(self) -> GameSnapshot:
        if self._phase == "playing":
            self._phase = "paused"
            self._revision += 1
        return self.snapshot()

    def resume(self) -> GameSnapshot:
        if self._phase == "paused":
            self._phase = "playing"
            self._revision += 1
        return self.snapshot()

    def record_hit(self, throw_id: str, points: int) -> ScoreEvent | None:
        """Accept one physical throw, or ignore a duplicate/inactive throw.

        A zero-point miss counts as a dart. The caller must supply a stable
        throw ID; observations from two cameras must share that ID.
        """
        if not isinstance(throw_id, str) or not throw_id:
            raise ValueError("throw_id must be a non-empty string")
        if isinstance(points, bool) or not isinstance(points, int) or points not in VALID_DART_POINTS:
            raise ValueError("points must be an achievable single-dart score")
        if self._phase != "playing" or throw_id in self._accepted_throw_ids or len(self._turn) == 3:
            return None
        self._accepted_throw_ids.add(throw_id)
        self._turn.append(points)
        self._total += points
        self._revision += 1
        return ScoreEvent(throw_id, points, self._total, sum(self._turn), self._revision)

    def clear_board(self) -> GameSnapshot:
        """Start the next turn when darts have been removed from the board."""
        if self._phase == "playing" and self._turn:
            self._turn.clear()
            self._revision += 1
        return self.snapshot()

    def snapshot(self) -> GameSnapshot:
        return GameSnapshot("simple_score", self._phase, "player1", self._total,
                            tuple(self._turn), self._revision)
