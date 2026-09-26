# Durable game session, first implementation

`DurableSession` in `SW/DartScoreEngine/Input/store.py` is a single-writer
SQLite action journal around `GameService` and `InputCoordinator`. The same
`apply_action()` function handles live submitted actions, journal replay, and
the camera-free simulator. It uses only Python's standard library on Linux.

Run a persistent simulated session from the repository root:

```
python3 SW/simulate_game.py Testdata/Simulations/basic_game.jsonl --db runtime/game.sqlite3
python3 -m unittest discover -s tests -v
```

The `runtime/` directory is ignored by Git. Reopening this database rebuilds
the cumulative score, current turn, phase, accepted/ignored throw IDs, pending
review and camera health. Replaying the same example script with the same
generated `script-line-N` request IDs returns the recorded results rather than
applying them again. For a different script, use a fresh database or supply
globally unique `request_id` values in its JSON Lines actions.

Each accepted request is stored atomically with its canonical JSON action and
result. Reusing a request ID with different content fails. A failed write
restores the live objects from committed actions. On restart, every committed
action is replayed in order and checked against its stored result. A mismatch
or unsupported schema version stops startup rather than silently resetting
the game. SQLite WAL mode and full synchronous commits are enabled. A local
file lock rejects a second writer process for the same database.

`state()` returns the recoverable game, pending review details and camera
health. `accepted_score_events()` reads the committed scoring results in
order. Evidence references are journaled, but this PR does not save the image
bytes. Deleting an evidence image does not delete the game action.

## Current limits

- The legacy Pygame loop still uses an in-memory `GameService`; the persistent
  session is exercised by the simulator and is ready for the API adapter.
- There is no HTTP service, automatic backup, database migration, journal
  compaction, multi-process sharing, or cross-host replication yet. Replay
  time grows with the action count; measure it before long-running deployment.
- Run one engine writer process. Put the database on the Pi 5 SSD, not on the
  presentation Pi. Use SQLite's backup API for online backup rather than
  copying only the main database file while WAL is active.
- Pending review metadata and game actions persist. Actual still images and
  their manual deletion policy will be implemented separately.
