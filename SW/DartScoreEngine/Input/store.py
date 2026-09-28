"""Single-writer SQLite action journal for the camera-free game runtime."""

import fcntl
import json
import sqlite3
import threading
import uuid
from dataclasses import asdict
from pathlib import Path

from DartScoreEngine.Game import GameService
from .actions import apply_action
from .contract import InputCoordinator


class StorageCorruptionError(RuntimeError):
    """Committed actions cannot be replayed into the same game state."""


class RevisionConflict(ValueError):
    """A command was based on an older game snapshot."""


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class DurableSession:
    """Persist each accepted action and replay it after process restart.

    A process-wide file lock prevents two writer processes from diverging.
    Request IDs are unique and idempotent within this session database.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mutex = threading.RLock()
        self._lock_file = (self.path.parent / (self.path.name + ".lock")).open("a+b")
        self._conn = None
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=FULL")
            version = self._conn.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise RuntimeError(f"unsupported session schema version: {version}")
            self._conn.execute("""CREATE TABLE IF NOT EXISTS actions (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL UNIQUE,
                payload TEXT NOT NULL,
                result TEXT NOT NULL
            )""")
            self._conn.execute("""CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
            self._conn.execute("INSERT OR IGNORE INTO metadata(key,value) VALUES('game_id',?)",
                               (str(uuid.uuid4()),))
            self.game_id = self._conn.execute(
                "SELECT value FROM metadata WHERE key='game_id'").fetchone()[0]
            self._conn.execute("PRAGMA user_version=1")
            self._conn.commit()
            self._reload()
        except Exception:
            self.close()
            raise

    def _reload(self):
        game = GameService()
        inputs = InputCoordinator(game)
        for sequence, payload, stored_result in self._conn.execute(
                "SELECT sequence, payload, result FROM actions ORDER BY sequence"):
            try:
                action = json.loads(payload)
                if type(action) is not dict:
                    raise ValueError("committed action must be an object")
                expected = action.get("expected_revision")
                if expected is not None and expected != game.snapshot().revision:
                    raise ValueError("committed revision precondition differs")
                old_result = json.loads(stored_result)
                if type(old_result) is not dict:
                    raise ValueError("committed result must be an object")
                result = apply_action(game, inputs, action)
                if _json(result) != stored_result:
                    raise ValueError("replayed result differs from committed result")
            except (ValueError, TypeError, RuntimeError, AttributeError) as exc:
                raise StorageCorruptionError(f"cannot replay action {sequence}: {exc}") from exc
        self.game, self.inputs = game, inputs

    def apply(self, request_id: str, action: dict) -> dict:
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("request_id must be a non-empty string")
        payload = _json(action)
        with self._mutex:
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                old = self._conn.execute(
                    "SELECT payload, result FROM actions WHERE request_id=?", (request_id,)).fetchone()
                if old is not None:
                    if old[0] != payload:
                        raise ValueError("request_id reused with a different action")
                    self._conn.commit()
                    return json.loads(old[1])
                expected = action.get("expected_revision")
                if expected is not None and (type(expected) is not int or
                                             expected != self.game.snapshot().revision):
                    raise RevisionConflict("expected_revision does not match current revision")
                result = apply_action(self.game, self.inputs, action)
                encoded = _json(result)
                self._conn.execute("INSERT INTO actions(request_id,payload,result) VALUES(?,?,?)",
                                   (request_id, payload, encoded))
                self._conn.commit()
                return json.loads(encoded)
            except Exception:
                self._conn.rollback()
                self._reload()  # Revert any in-memory mutation after a failed write.
                raise

    def state(self) -> dict:
        with self._mutex:
            pending = {}
            for throw_id, candidate in self.inputs.ordered_pending():
                record = asdict(candidate)
                record["captured_at"] = candidate.captured_at.isoformat()
                pending[throw_id] = record
            return {"game": asdict(self.game.snapshot()), "pending": pending,
                    "camera_health": dict(self.inputs.camera_health)}

    def accepted_score_events(self) -> list[dict]:
        """Read committed scoring results in order, for a future API adapter."""
        with self._mutex:
            results = self._conn.execute("SELECT result FROM actions ORDER BY sequence")
            accepted = []
            seen = set()
            for (record,) in results:
                result = json.loads(record)
                events = ([result["score_event"]] if result.get("score_event") is not None else [])
                events.extend(result.get("following_scores", ()))
                for event in events:
                    key = (event["throw_id"], event["revision"])
                    if key not in seen:
                        accepted.append(event)
                        seen.add(key)
            return accepted

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        if self._lock_file is not None:
            fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
