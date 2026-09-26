"""Replay JSON Lines board-hit actions without cameras, GPIO or Pygame."""

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from DartScoreEngine.Game import GameService
from DartScoreEngine.Input import InputCoordinator
from DartScoreEngine.Input.actions import apply_action
from DartScoreEngine.Input.store import DurableSession


def simulate(lines, store=None):
    game = GameService() if store is None else store.game
    inputs = InputCoordinator(game) if store is None else store.inputs
    start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            action = json.loads(line)
            kind = action["type"]
            if kind in ("hit", "uncertain") and "captured_at" not in action:
                action["captured_at"] = (start_time + timedelta(seconds=line_number)).isoformat()
            result = apply_action(game, inputs, action) if store is None else store.apply(
                action.get("request_id", f"script-line-{line_number}"), action)
        except (KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
        if store is not None:
            game, inputs = store.game, store.inputs
        yield {"line": line_number, "action": kind, "result": result,
               "game": asdict(game.snapshot()), "pending_throw_ids": sorted(inputs.pending),
               "camera_health": dict(inputs.camera_health)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="JSON Lines action script")
    parser.add_argument("--db", type=Path, help="persist actions to this local SQLite file")
    args = parser.parse_args()
    if args.db is None:
        with args.script.open(encoding="utf-8") as lines:
            for record in simulate(lines):
                print(json.dumps(record, sort_keys=True))
    else:
        with DurableSession(args.db) as store, args.script.open(encoding="utf-8") as lines:
            for record in simulate(lines, store):
                print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
