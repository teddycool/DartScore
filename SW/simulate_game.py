"""Replay JSON Lines board-hit actions without cameras, GPIO or Pygame."""

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from DartScoreEngine.Game import GameService
from DartScoreEngine.Input import BoardHitCandidate, InputCoordinator


def simulate(lines):
    game = GameService()
    inputs = InputCoordinator(game)
    start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            action = json.loads(line)
            kind = action["type"]
            if kind == "start":
                game.start_game()
                result = {"outcome": "started"}
            elif kind in ("hit", "uncertain"):
                candidate = BoardHitCandidate(
                    throw_id=action["throw_id"],
                    captured_at=start_time + timedelta(seconds=line_number),
                    source="simulator",
                    status="confirmed" if kind == "hit" else "uncertain",
                    points=action.get("points"),
                    camera_ids=tuple(action.get("camera_ids", ())),
                    evidence_refs=tuple(action.get("evidence_refs", ())),
                )
                result = asdict(inputs.submit(candidate))
            elif kind in ("confirm", "correct", "reject"):
                result = asdict(inputs.resolve(action["throw_id"], kind, action.get("points")))
            elif kind == "pause":
                game.pause()
                result = {"outcome": "paused"}
            elif kind == "resume":
                game.resume()
                result = {"outcome": "resumed"}
            elif kind == "clear_board":
                inputs.clear_board()
                result = {"outcome": "board_cleared"}
            elif kind == "camera":
                inputs.set_camera_health(action["camera_id"], action["state"])
                result = {"outcome": "camera_status_changed"}
            else:
                raise ValueError(f"unknown action type: {kind}")
        except (KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
        yield {"line": line_number, "action": kind, "result": result,
               "game": asdict(game.snapshot()), "pending_throw_ids": sorted(inputs.pending),
               "camera_health": dict(inputs.camera_health)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="JSON Lines action script")
    args = parser.parse_args()
    with args.script.open(encoding="utf-8") as lines:
        for record in simulate(lines):
            print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
