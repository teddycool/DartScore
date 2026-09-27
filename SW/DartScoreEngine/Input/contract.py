"""Route physical board-hit candidates to the independent GameService.

This boundary has no camera, web, GPIO, or presentation dependency. Pending
reviews and camera health are in memory until persistence is implemented.
"""

from dataclasses import dataclass
from datetime import datetime

from DartScoreEngine.Game import GameService, ScoreEvent
from DartScoreEngine.Game.service import VALID_DART_POINTS


@dataclass(frozen=True)
class BoardHitCandidate:
    throw_id: str
    captured_at: datetime
    source: str
    status: str  # confirmed | uncertain
    points: int | None
    camera_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.throw_id or not self.source:
            raise ValueError("throw_id and source are required")
        if self.captured_at.tzinfo is None or self.captured_at.utcoffset() is None:
            raise ValueError("captured_at must include a timezone")
        if self.status not in ("confirmed", "uncertain"):
            raise ValueError("status must be confirmed or uncertain")
        if self.points is None:
            if self.status == "confirmed":
                raise ValueError("confirmed hit requires points")
        elif isinstance(self.points, bool) or not isinstance(self.points, int) or self.points not in VALID_DART_POINTS:
            raise ValueError("points must be an achievable single-dart score")


@dataclass(frozen=True)
class InputResult:
    outcome: str  # scored | pending | rejected | ignored
    throw_id: str
    score_event: ScoreEvent | None = None
    reason: str | None = None
    following_scores: tuple[ScoreEvent, ...] = ()


class InputCoordinator:
    """Accept at most one resolution for each throw ID.

    Reserve up to three slots for scored and pending throws together. Resolve
    pending throws in arrival order so corrected scores keep their dart order.
    """

    def __init__(self, game: GameService):
        self.game = game
        self.pending: dict[str, BoardHitCandidate] = {}
        self.camera_health: dict[str, str] = {}
        self._candidates: dict[str, BoardHitCandidate] = {}
        self._results: dict[str, InputResult] = {}
        self._resolutions: dict[str, tuple[str, int | None]] = {}

    def submit(self, candidate: BoardHitCandidate) -> InputResult:
        previous = self._candidates.get(candidate.throw_id)
        if previous is not None:
            if previous != candidate:
                raise ValueError("throw_id already used for a different candidate")
            return self._results[candidate.throw_id]

        state = self.game.snapshot()
        if state.phase != "playing":
            result = InputResult("ignored", candidate.throw_id, reason="game_not_playing")
        elif len(state.current_turn) + len(self.pending) == 3:
            result = InputResult("ignored", candidate.throw_id, reason="turn_complete")
        elif candidate.status == "uncertain" or self.pending:
            # A confirmed hit behind an unresolved candidate must wait as well;
            # committing it now would put scores in the wrong dart order.
            self.pending[candidate.throw_id] = candidate
            result = InputResult("pending", candidate.throw_id)
        else:
            event = self.game.record_hit(candidate.throw_id, candidate.points)
            result = InputResult("scored", candidate.throw_id, event) if event else InputResult(
                "ignored", candidate.throw_id, reason="game_rejected")

        self._candidates[candidate.throw_id] = candidate
        self._results[candidate.throw_id] = result
        return result

    def restore_legacy_ignored(self, candidate: BoardHitCandidate) -> InputResult:
        """Replay an old journal entry that ignored a hit during review."""
        if candidate.throw_id in self._candidates:
            raise ValueError("legacy ignored throw ID already used")
        result = InputResult("ignored", candidate.throw_id, reason="pending_review")
        self._candidates[candidate.throw_id] = candidate
        self._results[candidate.throw_id] = result
        return result

    def resolve(self, throw_id: str, decision: str, points: int | None = None) -> InputResult:
        """Confirm proposed points, correct them, or reject a false detection."""
        if decision not in ("confirm", "correct", "reject"):
            raise ValueError("decision must be confirm, correct or reject")
        signature = (decision, points)
        if throw_id in self._resolutions:
            if self._resolutions[throw_id] != signature:
                raise ValueError("throw already resolved differently")
            return self._results[throw_id]
        candidate = self.pending.get(throw_id)
        if candidate is None:
            raise ValueError("no pending throw with this ID")
        if throw_id != next(iter(self.pending)):
            raise ValueError("resolve pending throws in dart order")
        if self.game.snapshot().phase != "playing":
            raise ValueError("resume the game before resolving a pending throw")
        if decision == "correct":
            if isinstance(points, bool) or not isinstance(points, int) or points not in VALID_DART_POINTS:
                raise ValueError("correction must be an achievable single-dart score")
            accepted_points = points
        elif decision == "confirm":
            if points is not None or candidate.points is None:
                raise ValueError("confirm requires proposed points and no override")
            accepted_points = candidate.points
        else:
            if points is not None:
                raise ValueError("reject does not accept points")
            accepted_points = None

        if decision != "reject":
            event = self.game.record_hit(throw_id, accepted_points)
            if event is None:
                raise RuntimeError("pending throw could not be committed")
        del self.pending[throw_id]
        following = []
        while self.pending:
            next_id, next_candidate = next(iter(self.pending.items()))
            if next_candidate.status != "confirmed":
                break
            scored = self.game.record_hit(next_id, next_candidate.points)
            if scored is None:
                raise RuntimeError("queued confirmed throw could not be committed")
            following.append(scored)
            del self.pending[next_id]
            self._results[next_id] = InputResult("scored", next_id, scored)
            self._resolutions[next_id] = ("confirm", None)
        result = InputResult("rejected" if decision == "reject" else "scored", throw_id,
                             None if decision == "reject" else event,
                             following_scores=tuple(following))
        self._results[throw_id] = result
        self._resolutions[throw_id] = signature
        return result

    def set_camera_health(self, camera_id: str, state: str) -> None:
        if not camera_id or state not in ("ready", "degraded", "unavailable"):
            raise ValueError("invalid camera ID or state")
        self.camera_health[camera_id] = state

    def clear_board(self):
        if self.pending:
            raise ValueError("resolve the pending throw before clearing the board")
        return self.game.clear_board()
