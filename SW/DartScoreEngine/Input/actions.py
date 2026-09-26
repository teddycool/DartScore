"""Apply a JSON-compatible action to the in-memory game and input boundary."""

from dataclasses import asdict
from datetime import datetime

from DartScoreEngine.Game import GameService
from .contract import BoardHitCandidate, InputCoordinator


def apply_action(game: GameService, inputs: InputCoordinator, action: dict) -> dict:
    """Return a JSON-compatible result; raise before accepting invalid input."""
    if not isinstance(action, dict):
        raise ValueError("action must be an object")
    try:
        kind = action["type"]
        if kind == "start":
            game.start_game()
            return {"outcome": "started"}
        if kind in ("hit", "uncertain"):
            captured_at = datetime.fromisoformat(action["captured_at"].replace("Z", "+00:00"))
            candidate = BoardHitCandidate(
                throw_id=action["throw_id"], captured_at=captured_at,
                source=action.get("source", "simulator"),
                status="confirmed" if kind == "hit" else "uncertain",
                points=action.get("points"),
                camera_ids=tuple(action.get("camera_ids", ())),
                evidence_refs=tuple(action.get("evidence_refs", ())),
            )
            return asdict(inputs.submit(candidate))
        if kind in ("confirm", "correct", "reject"):
            return asdict(inputs.resolve(action["throw_id"], kind, action.get("points")))
        if kind == "pause":
            game.pause()
            return {"outcome": "paused"}
        if kind == "resume":
            game.resume()
            return {"outcome": "resumed"}
        if kind == "clear_board":
            inputs.clear_board()
            return {"outcome": "board_cleared"}
        if kind == "camera":
            inputs.set_camera_health(action["camera_id"], action["state"])
            return {"outcome": "camera_status_changed"}
        raise ValueError(f"unknown action type: {kind}")
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"invalid {kind} action: {exc}") from exc
