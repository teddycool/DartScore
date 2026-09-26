# First GameService extraction

The one-player accumulating game now lives in `SW/DartScoreEngine/Game/service.py`.
It depends only on the Python standard library. The legacy `PlayStateLoop`
continues to detect board changes and renders with Pygame, but delegates
accepted scores, the current three-dart turn, the cumulative total and phase
to `GameService`. Its `_legacy_scoreboard()` method adapts a game snapshot to
the existing frontend's dictionary. The camera never imports game rules.

This is a small migration step, not the completed two-Pi system. The loop
starts the simple-score game automatically as before. `start_game`, `pause`,
`resume`, `record_hit` and `clear_board` are pure domain operations; there is
no HTTP API, persistence, uncertainty review, player selection, 301/501 or
two-camera resolver yet. A stable `throw_id` must come from a future resolver;
the old loop generates local sequential IDs for its single-camera candidates.

The service accepts only achievable single-dart numeric points. A zero-point
miss uses one dart. The fourth dart in a turn is ignored until the board is
cleared. Accepted IDs remain remembered across turns so the same throw cannot
change the total twice. Hits and board-clear calls while paused do not change
game state. The camera loop must refresh its comparison baseline before
resuming capture; this PR does not expose Pause in the legacy UI.

Run the domain tests without hardware or third-party packages:

```
python3 -m unittest discover -s tests -v
```

Next steps: define durable game and throw IDs, persist accepted changes and
pending uncertainty, then expose snapshots, commands and events through the
agreed API. Add game-type strategies for 301/501 independently of capture.
