# Manual API testing without cameras

Use a separate local database. The developer hit endpoint is disabled on the Pi
services and works only with an engine started on loopback with `--dev-input`.
Run these from the repository root in separate terminals:

```sh
python3 SW/serve_engine.py --db runtime/manual-test.sqlite3 --dev-input
python3 SW/serve_presentation.py
```

Open <http://127.0.0.1:8080>. Start a game with the page button, or use the
`start_game` command below. A database keeps its game state after restart; use
a different test DB filename when you want a new game.

## Send one random dart

```sh
python3 scripts/send_test_throw.py
```

Each invocation sends exactly one dart with a fresh request/throw ID and UTC
timestamp. It chooses one achievable dart score (including zero) and marks the
candidate `uncertain` with a 30% probability. The command prints both its
choice and the engine's outcome. To test the extremes, use
`--uncertain-percent 100` or `--uncertain-percent 0`. A dart ignored because
the game is paused or the round is full still used its generated ID; simply
run the script again after resuming or advancing the round.

## Send a specific hit or uncertain candidate

Use this shell function in a terminal; it creates fresh IDs each time:

```sh
test_dart() {
  local kind="$1" points="$2" id timestamp
  id=$(python3 -c 'import uuid; print(uuid.uuid4())')
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  curl -sS -X POST http://127.0.0.1:8765/api/v1/dev/actions \
    -H 'Content-Type: application/json' \
    -d "{\"request_id\":\"$id\",\"throw_id\":\"$id\",\"type\":\"$kind\",\"captured_at\":\"$timestamp\",\"points\":$points}"
  echo
}
test_dart hit 20
test_dart uncertain 15
test_dart hit 25
```

The commands above score dart #1 immediately, hold dart #2 for review, and
hold the confirmed dart #3 behind it. Resolving dart #2 commits the third dart
automatically. Use `test_dart uncertain 5` three times to review every dart.

## Inspect state and send game commands

```sh
curl -sS http://127.0.0.1:8765/api/v1/state | python3 -m json.tool
```

Define this helper in the same terminal. It fetches the latest game revision
and generates a new request ID for every command:

```sh
game_command() {
  local kind="$1" payload="$2" revision id body
  if [ -z "$payload" ]; then payload='{}'; fi
  revision=$(curl -fsS http://127.0.0.1:8765/api/v1/state |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["revision"])') || return
  id=$(python3 -c 'import uuid; print(uuid.uuid4())')
  body=$(python3 -c 'import json,sys; print(json.dumps({"schema_version":1,"request_id":sys.argv[1],"expected_revision":int(sys.argv[2]),"type":sys.argv[3],"payload":json.loads(sys.argv[4])}))' \
    "$id" "$revision" "$kind" "$payload") || return
  curl -sS -X POST http://127.0.0.1:8765/api/v1/commands \
    -H 'Content-Type: application/json' -d "$body" | python3 -m json.tool
}
```

Examples (replace `THROW_ID` with the ID printed by the test dart command or
shown under `pending_throw` in `/state`):

```sh
game_command start_game '{"game_type":"simple_score"}'
game_command confirm_throw '{"throw_id":"THROW_ID"}'
game_command correct_throw '{"throw_id":"THROW_ID","points":25}'
game_command reject_throw '{"throw_id":"THROW_ID"}'
game_command pause_game
game_command resume_game
game_command next_round
```

`confirm_throw` accepts the pending proposal. `correct_throw` replaces it with
a valid single-dart score; `reject_throw` marks it as a false detection and
frees that round slot. A zero-point accepted hit still occupies a dart slot.
`next_round` requires three accepted darts, no pending review, and a playing
game. It clears the three slots while preserving the total. During pause,
submitted throws are ignored. Run commands one at a time; a concurrent browser
action can cause a revision conflict, in which case reload `/state` and retry
with a new request ID.

## Rehearse a full round in the browser

Use the separate `runtime/manual-test.sqlite3` database above so existing game
data is untouched. Run the engine and presentation on your development computer
as shown at the top of this page. Open the scoreboard at
<http://127.0.0.1:8080>, click **Start game**, then run these commands in a
terminal with `test_dart` defined:

```sh
test_dart uncertain 15
test_dart uncertain 20
test_dart uncertain 25
```

Check that darts #1–#3 need review and the total has not changed. At the board,
correct dart #1 to 20 in the browser, reject dart #2 as a false detection, and
correct dart #3 to 0 (an accepted miss). The page should now show `[20, 0, —]`
and a total of 20. The rejected detection freed one slot, so send a replacement:

```sh
test_dart hit 25
```

The page should show `[20, 0, 25]`, total 45, and **Remove darts / Next round**.
Click it only after collecting the darts. The round clears but the total stays
45. Send `test_dart hit 50` and check that dart #1 of the new round scores 50,
for a total of 95. Reload the page between steps if you want to verify that
the display always reconstructs its state from the engine. The Pi 4B proxy
cannot submit simulated hits; the developer input must be sent directly to a
loopback engine running with `--dev-input`.

For a repeatable automated check of the same engine-to-presentation HTTP path,
run `python3 -m unittest discover -s tests -p test_round_workflow.py -v` from
the repo root. It starts both servers on temporary loopback ports, uses a fresh
temporary SQLite database, and checks review order, correction, rejection,
accepted zero, queued confirmed hits, pause, round advance, and proxy isolation.
