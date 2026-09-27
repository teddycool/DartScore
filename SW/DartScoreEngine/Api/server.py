"""Small standard-library HTTP/SSE adapter for a trusted local network."""

import json
import queue
import shutil
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from DartScoreEngine.Input.store import RevisionConflict


def snapshot(store):
    state = store.state()
    game = state["game"]
    pending = next(iter(state["pending"].values()), None)
    cameras = [{"camera_id": key, "state": value, "calibrated": False}
               for key, value in sorted(state["camera_health"].items())]
    return {"schema_version": 1, "game_id": store.game_id,
            "revision": game["revision"], "phase": game["phase"],
            "game_type": game["game_type"], "active_player_id": game["player_id"],
            "players": [{"player_id": game["player_id"], "name": "Player 1",
                         "total": game["total"], "current_turn": game["current_turn"]}],
            "pending_throw": pending,
            "engine": {"state": "attention" if pending else "ready", "reason": "pending_review" if pending else None},
            "cameras": cameras}


def command_action(command):
    if type(command) is not dict or command.get("schema_version") != 1:
        raise ValueError("schema_version 1 is required")
    request_id = command.get("request_id")
    revision = command.get("expected_revision")
    if not isinstance(request_id, str) or not request_id or type(revision) is not int or revision < 0:
        raise ValueError("request_id and nonnegative expected_revision are required")
    payload = command.get("payload", {})
    if type(payload) is not dict:
        raise ValueError("payload must be an object")
    kind = command.get("type")
    no_payload = {"pause_game": "pause", "resume_game": "resume",
                  "next_round": "next_round"}
    resolution = {"confirm_throw": "confirm", "correct_throw": "correct",
                  "reject_throw": "reject"}
    if kind == "start_game":
        if payload not in ({}, {"game_type": "simple_score"}):
            raise ValueError("only the current simple_score game is supported")
        action = {"type": "start"}
    elif kind in no_payload:
        if payload:
            raise ValueError("this command takes no payload")
        action = {"type": no_payload[kind]}
    elif kind in resolution:
        required = {"throw_id", "points"} if kind == "correct_throw" else {"throw_id"}
        if set(payload) != required:
            raise ValueError("invalid resolution payload")
        action = {"type": resolution[kind], **payload}
    else:
        raise ValueError("unknown command type")
    action["expected_revision"] = revision
    return request_id, action


class EngineServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, store, allow_dev_input=False):
        super().__init__(address, Handler)
        self.store = store
        self.allow_dev_input = allow_dev_input
        self._gate = threading.RLock()
        self._listeners = set()
        self._run_id = str(uuid.uuid4())
        self._event_number = 0

    def subscribe(self):
        listener = queue.Queue(maxsize=32)
        with self._gate:
            self._listeners.add(listener)
            current = snapshot(self.store)
            listener.put_nowait(self._make_event("game_changed", current, current["revision"]))
        return listener

    def subscribed(self, listener):
        with self._gate:
            return listener in self._listeners

    def unsubscribe(self, listener):
        with self._gate:
            self._listeners.discard(listener)

    def _make_event(self, kind, data, revision):
        self._event_number += 1
        event_id = f"{self._run_id}:{self._event_number}"
        return {"schema_version": 1, "event_id": event_id, "type": kind,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "game_id": self.store.game_id, "revision": revision, **data}

    def apply(self, request_id, action):
        with self._gate:
            before = snapshot(self.store)
            result = self.store.apply(request_id, action)
            after = snapshot(self.store)
            if after != before:
                kind = "throw_scored" if result.get("outcome") == "scored" else (
                    "throw_pending" if result.get("outcome") == "pending" else "game_changed")
                event_revision = after["revision"] if after["revision"] != before["revision"] else None
                event = self._make_event(kind, {"state": after, "result": result}, event_revision)
                for listener in tuple(self._listeners):
                    try:
                        listener.put_nowait(event)
                    except queue.Full:
                        self._listeners.discard(listener)  # The reader reconnects and reloads state.
            return result, after


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json(self, status, value):
        raw = json.dumps(value, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _error(self, status, code, message):
        self._json(status, {"error": {"code": code, "message": message}})

    def do_GET(self):
        if self.path == "/api/v1/state":
            self._json(200, snapshot(self.server.store))
        elif self.path == "/api/v1/health":
            state = snapshot(self.server.store)
            free = shutil.disk_usage(self.server.store.path.parent).free
            self._json(200, {"schema_version": 1, "service": "ready", "game_id": state["game_id"],
                             "engine": state["engine"], "cameras": state["cameras"],
                             "storage": {"free_bytes": free, "image_write_status": "not_integrated"}})
        elif self.path == "/api/v1/events":
            listener = self.server.subscribe()
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                while True:
                    if not self.server.subscribed(listener):
                        break
                    try:
                        event = listener.get(timeout=15)
                        self.wfile.write((f"id: {event['event_id']}\nevent: {event['type']}\n"
                                          f"data: {json.dumps(event, allow_nan=False)}\n\n").encode())
                    except queue.Empty:
                        self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                self.server.unsubscribe(listener)
                self.close_connection = True
        else:
            self._error(404, "not_found", "unknown endpoint")

    def do_POST(self):
        if self.path not in ("/api/v1/commands", "/api/v1/dev/actions"):
            self._error(404, "not_found", "unknown endpoint")
            return
        if self.path.endswith("/dev/actions") and not self.server.allow_dev_input:
            self._error(404, "not_found", "developer input is disabled")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 65536 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("JSON body required (maximum 64 KiB)")
            body = json.loads(self.rfile.read(length))
            if self.path.endswith("/commands"):
                request_id, action = command_action(body)
            else:
                if type(body) is not dict or type(body.get("request_id")) is not str or not body["request_id"]:
                    raise ValueError("request_id is required")
                request_id = body["request_id"]
                action = {key: value for key, value in body.items() if key != "request_id"}
                if action.get("type") not in ("hit", "uncertain", "camera", "clear_board"):
                    raise ValueError("unsupported developer action")
            result, state = self.server.apply(request_id, action)
            self._json(200, {"schema_version": 1, "request_id": request_id, "accepted": True,
                             "game_id": state["game_id"], "revision": state["revision"], "result": result})
        except RevisionConflict as exc:
            self._error(409, "revision_conflict", str(exc))
        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            self._error(400, "invalid_command", str(exc))
