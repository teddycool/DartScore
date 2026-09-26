# Engine / presentation API contract (proposal)

Status: **v1 proposal**, no endpoints implemented yet. Review this contract before extracting game logic. The Pi 5 owns the API; the Pi 4B proxies it under the same paths for its local browser. JSON is UTF-8. Timestamps are UTC RFC 3339 strings. IDs are opaque strings. Scores and totals are integers.

## Rules

- The engine is authoritative. The browser never calculates, commits or repairs a score locally.
- A camera observation is not a scored throw. Two camera observations may resolve to one `throw_id`; no two accepted score events may share that ID.
- Every accepted change increases the game `revision` exactly once. Events carry the resulting revision; the full snapshot carries the latest revision.
- A client loads the snapshot on startup and whenever event revisions are discontinuous. Repeated events with the same or older revision are ignored by the client.
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
data: {"schema_version":1,"event_id":"game-42:17","type":"throw_scored","occurred_at":"2026-09-26T06:30:00Z","game_id":"game-42","revision":17,"throw_id":"throw-8","player_id":"player-1","score":20,"total":241,"decision":"automatic"}

```

Initial event types: `throw_scored`, `throw_pending`, `game_changed`, `engine_status_changed`. Every game mutation event carries `game_id` and `revision`; status-only events may have `revision: null` because they do not change the game. The client reconnects automatically, fetches `/state` after reconnect, and reconciles by revision. This avoids requiring unbounded event replay in v1. Heartbeats keep idle connections detectable.

A pending throw is an uncommitted candidate. It contains `throw_id`, proposed score or `null`, and a reason; the score remains unchanged until explicit confirmation. The browser must visibly distinguish it from an accepted throw.

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
  "payload": {"throw_id": "throw-8", "score": 20}
}
```

Initial command types to define in implementation: `start_game`, `confirm_throw`, `reject_throw`, `pause_game`, `resume_game`. Calibration and camera setup commands get their own review before implementation. A successful response includes `request_id`, `accepted: true`, `game_id` and the new `revision`. Invalid commands return structured code/message and do not change state.

The engine stores the result for each `request_id`: retrying the same request returns the same outcome, and reusing an ID with different content is rejected. `expected_revision` prevents stale controls from overwriting newer game state; a mismatch returns a conflict and the client reloads `/state`. Operator actions are restricted to the LAN service/proxy; authentication and authorization configuration must be decided before exposing the API beyond the trusted network.

## Failure and recovery acceptance criteria

1. A Pi 4B reboot or browser reload displays the current game from `/state` without resetting scores.
2. An SSE disconnect causes a reconnect and snapshot reconciliation; duplicate or missed events never double-count a throw.
3. Two observations of the same dart yield at most one accepted `throw_scored` event.
4. An uncertain throw does not change the total until confirmation; a rejected throw never changes it.
5. Repeating a command with the same `request_id` does not repeat its effect.
6. Loss of a camera is visible in status and LEDs; the engine makes an explicit degraded/attention decision.
7. Accepted game events survive an engine restart; pending observations may be discarded with a visible status.

The API payloads are intentionally small. Frame transport, calibration storage, persistence technology and the web framework are internal implementation choices.
