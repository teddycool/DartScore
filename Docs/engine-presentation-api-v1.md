# Engine / presentation API contract (proposal)

Status: **agreed v1 target; camera-free simple-score HTTP slice implemented.** State, health, commands and SSE use the durable action journal. The Pi 4B proxy, two-camera integration, 301/501 rules, player configuration, board-hit sector data and evidence storage remain future work. JSON is UTF-8. Timestamps are UTC RFC 3339 strings. IDs are opaque strings. Scores and totals are integers.

## Rules

- All game interaction begins in the Pi 4B browser. The browser sends commands and renders responses; it never implements 301/501 rules or calculates, commits or repairs a score locally.
- Vision reports a physical board hit (segment, multiplier and points) or an uncertain candidate. The GameService applies the active game type, including player turn, bust and finish rules, to decide if and how the game total changes.
- A camera observation is not a scored throw. Two camera observations may resolve to one `throw_id`; no two accepted score events may share that ID.
- Every accepted change increases the game `revision` exactly once. Events carry the resulting revision; the full snapshot carries the latest revision.
- A client loads the snapshot on startup and whenever event revisions are discontinuous. Repeated events with the same or older revision are ignored by the client.
- Pending-review and camera-health changes can occur without advancing the game revision. Their SSE events carry `revision: null` and include a fresh `state` snapshot. Clients apply that snapshot even when the game revision is unchanged. SSE IDs are process-local; reconnects reload `/state`, with no missed-event replay.
- Accepted changes and their IDs must survive an engine restart. A failed or uncertain observation must not alter the score.
- `schema_version` is an integer. Unknown major versions/types must not be silently interpreted as known commands or scores.
- No raw video or calibration matrices are included in game state events.

## Read endpoints

### `GET /api/v1/state`

Returns HTTP 200 and a complete snapshot. Example shape:

```json
{
  "schema_version": 1,
  "revision": 17,
  "game_id": "game-42",
  "phase": "playing",
  "game_type": "501",
  "active_player_id": "player-1",
  "players": [
    {"player_id": "player-1", "name": "Player 1", "total": 241,
     "current_turn": [20, 13]}
  ],
  "pending_throw": null,
  "engine": {"state": "ready", "reason": null},
  "cameras": [
    {"camera_id": "cam-0", "state": "ready", "calibrated": true},
    {"camera_id": "cam-1", "state": "ready", "calibrated": true}
  ]
}
```

`phase`: `idle | playing | paused | finished`.
`engine.state`: `starting | calibrating | ready | attention | error`.
`camera.state`: `ready | unavailable | degraded`. A camera may be degraded without stopping a game; the game service decides whether an observation is sufficient.
The examples show the target two-camera state; the single-camera migration may return one item.

### `GET /api/v1/events`

Server-Sent Events (`text/event-stream`). Each event has an `id` equal to its opaque `event_id`, an `event` type and JSON `data`. Example:

```text
id: game-42:17
event: throw_scored
data: {"schema_version":1,"event_id":"game-42:17","type":"throw_scored","occurred_at":"2026-09-26T06:30:00Z","game_id":"game-42","revision":17,"throw_id":"throw-8","player_id":"player-1","board_hit":{"segment":20,"multiplier":1,"points":20},"turn_result":{"applied_points":20,"bust":false,"remaining":241},"decision":"automatic"}

```

Initial event types: `throw_scored`, `throw_pending`, `game_changed`, `engine_status_changed`. Every game mutation event carries `game_id` and `revision`; status-only events may have `revision: null` because they do not change the game. The client reconnects automatically, fetches `/state` after reconnect, and reconciles by revision. This avoids requiring unbounded event replay in v1. Heartbeats keep idle connections detectable.

A pending throw is an uncommitted board-hit candidate. It contains `throw_id`, proposed board segment/multiplier/points or `null`, and a reason; the game total remains unchanged until explicit confirmation. The GameService then applies the active game type. The vision component never supplies a player's remaining total. The pending item persists across presentation restarts until confirmed, corrected or rejected. During pause, camera monitoring may continue for health, but throw detection produces no game event, pending item, turn change or score change. Paused throws are never queued for resume; the capture comparison baseline is refreshed before scoring resumes. The evidence record on the Pi 5 links `throw_id` to camera IDs, timestamps, calibration versions and still-frame references, plus the final operator outcome; no image bytes are embedded in game events. The browser must visibly distinguish it from an accepted throw.

### `GET /api/v1/health`

Returns service health, API version, camera availability, calibration status, storage status and an engine reason code. Health does not imply a score was accepted. Response codes distinguish healthy, degraded and unavailable service; exact monitoring integration is deferred.

### `GET /api/v1/cameras/{camera_id}/snapshot`

Optional, later endpoint for a still image during mounting/calibration. It is not a live video contract. Unknown camera IDs return 404.

## Commands

`POST /api/v1/commands` with JSON:

```json
{
  "schema_version": 1,
  "request_id": "operator-4c681e9a",
  "expected_revision": 17,
  "type": "confirm_throw",
  "payload": {"throw_id": "throw-8", "board_hit": {"segment": 20, "multiplier": 1, "points": 20}}
}
```

Initial command types to define in implementation: `start_game` (payload includes `game_type`, player IDs and rule options), `confirm_throw`, `correct_throw`, `reject_throw`, `pause_game`, `resume_game`. The engine validates board-hit consistency and game rules before applying a confirmed or corrected hit. In v1, `correct_throw` targets a pending `throw_id` and supplies `points` with `label_quality: "points_only"`. The integer must be an achievable single-dart score: 0, singles 1–20, doubles of 1–20, triples of 1–20, 25, or 50. Sector/ring selection on a dartboard image is a later contract extension. The Pi 5 validates the submitted points and calculates all authoritative game-rule effects. `reject_throw` means false detection and is distinct from an accepted miss worth zero points. Only one resolution may commit for a given pending `throw_id`. Calibration and camera setup commands get their own review before implementation. A successful response includes `request_id`, `accepted: true`, `game_id` and the new `revision`. Invalid commands return structured code/message and do not change state.

The engine stores the result for each `request_id`: retrying the same request returns the same outcome, and reusing an ID with different content is rejected. `expected_revision` prevents stale controls from overwriting newer game state; a mismatch returns a conflict and the client reloads `/state`. Operator actions are restricted to the LAN service/proxy; authentication and authorization configuration must be decided before exposing the API beyond the trusted network.

## Failure and recovery acceptance criteria

1. A Pi 4B reboot or browser reload displays the current game from `/state` without resetting scores.
2. An SSE disconnect causes a reconnect and snapshot reconciliation; duplicate or missed events never double-count a throw.
3. Two observations of the same dart yield at most one accepted `throw_scored` event.
4. An uncertain throw does not change the total until confirmation; a rejected throw never changes it. In 301/501, a physical board hit can also cause a bust without reducing the remaining total.
5. Repeating a command with the same `request_id` does not repeat its effect.
6. Loss of a camera is visible in status and LEDs; the engine makes an explicit degraded/attention decision.
7. Correcting a pending hit commits at most one throw. Its physical hit, points-only label (if used), and game-rule effect remain distinguishable; a rejected false detection never becomes a zero-point throw.
8. Accepted game events and pending uncertain hits survive an engine restart, so an operator can resolve a pending hit after either Pi reboots.
9. Paused throws produce no game mutation or queued hit, including after resume.
10. Evidence images remain until manual deletion in v1; image-write failures are visible without silently changing game state.

Evidence images are retained on the Pi 5 until manual deletion in v1. The health/status response reports free disk space and image-write failures; removing the oldest images to maintain a specified free-space reserve is a later step. Game records are retained independently of image deletion.

## Current implementation notes

Run `python3 SW/serve_engine.py --db runtime/game.sqlite3` from the repository root. The server defaults to `127.0.0.1:8765`. `--host` may bind it to a trusted wired LAN; configure access controls before exposing it further. `GET /api/v1/state`, `/api/v1/health`, `/api/v1/events` and `POST /api/v1/commands` are available. Health reports free bytes and `image_write_status: "not_integrated"`; absent cameras appear as an empty list.

The current `start_game` payload accepts only `{}` or `{"game_type":"simple_score"}` and starts a one-player accumulating game. `confirm_throw` and `reject_throw` take `throw_id`; `correct_throw` takes `throw_id` and `points`. The state includes `pending_throws` in capture order and `pending_throw` as its first entry for clients that show one review at a time. A round has at most three scored and pending candidates combined; review proceeds in capture order. After three accepted darts, the operator removes the darts and sends `next_round` with an empty payload. It preserves the total and clears `current_turn`; it requires a playing game and all three darts, with no pending review. A zero-point miss counts as a dart, while rejecting a false detection frees a slot for another candidate. Unsupported game types and payload fields return HTTP 400; stale `expected_revision` returns HTTP 409. A retried `request_id` returns the stored action result and does not apply the command twice. The response revision shows the current state.

A confirmed candidate waiting behind an uncertain dart scores automatically when that earlier review is resolved. The resolution result includes `following_scores` for scores applied in the same action, in dart order. Pending candidates are sorted by `captured_at`, with arrival order breaking timestamp ties. A candidate whose timestamp predates an already scored dart is rejected because committed scores cannot be reordered. Use a fresh test database with this version; earlier experimental journal formats are not migrated.

For local end-to-end testing, `--dev-input` enables `POST /api/v1/dev/actions` with the simulator's `hit`, `uncertain`, `camera` or `clear_board` action plus `request_id`. It is restricted to loopback and disabled by default. The server holds the journal's single-writer lock; do not run `simulate_game.py --db` against the same database concurrently.

The API payloads are intentionally small. Frame transport, calibration storage, persistence technology and the web framework are internal implementation choices.
