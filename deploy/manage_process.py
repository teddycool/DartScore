#!/usr/bin/env python3
"""Stop a user's old DartScore entry point and start deployed code on one Pi."""

import argparse
import fcntl
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
DEPLOY = HOME / "dartscore-deploy"
ENTRIES = {"engine": "serve_engine.py", "presentation": "serve_presentation.py"}
UNITS = {"engine": "dartscore-engine.service", "presentation": "dartscore-presentation.service"}


def owned_processes(role):
    """Find only this user's exact old-checkout or deployed entry point."""
    name = ENTRIES[role]
    allowed = {(HOME / "DartScore/SW" / name).resolve(),
               (DEPLOY / "SW" / name).resolve()}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) == os.getpid():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            args = (proc / "cmdline").read_bytes().split(b"\0")
            cwd = (proc / "cwd").resolve()
            # Only a Python script argument, never matching arbitrary command text.
            for arg in args[1:]:
                path = os.fsdecode(arg)
                if Path(path).name == name and (cwd / path).resolve() in allowed:
                    yield int(proc.name)
                    break
        except (FileNotFoundError, PermissionError, ProcessLookupError, OSError):
            continue


def stop_old(role):
    pids = list(owned_processes(role))
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"stopping old {role} process {pid}", flush=True)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 8
    while any(pid in set(owned_processes(role)) for pid in pids):
        if time.monotonic() >= deadline:
            raise RuntimeError(f"old {role} process did not exit; new process was not started")
        time.sleep(0.2)


def start(role, bind, engine_url, database):
    program = DEPLOY / "SW" / ENTRIES[role]
    if not program.is_file():
        raise RuntimeError(f"deployed entry point missing: {program}")
    command = [sys.executable, "-B", str(program)]
    if role == "engine":
        db = Path(database).expanduser()
        if not db.is_file():
            raise RuntimeError(f"game database missing: {db}; set engine.database_path in local YAML")
        command += ["--db", str(db), "--host", bind]
        probe_host, probe_port = bind, 8765
    else:
        command += ["--engine-url", engine_url]
        probe_host, probe_port = "127.0.0.1", 8080
    run = DEPLOY / "run"
    run.mkdir(mode=0o700, exist_ok=True)
    log_path = run / f"{role}.log"
    with log_path.open("ab") as log:
        process = subprocess.Popen(command, cwd=DEPLOY, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True, close_fds=True)
    deadline = time.monotonic() + 7
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"new {role} exited; check {log_path}")
        try:
            with socket.create_connection((probe_host, probe_port), timeout=0.5):
                time.sleep(0.2)
                if process.poll() is not None:
                    raise RuntimeError(f"new {role} exited; check {log_path}")
                (run / f"{role}.pid").write_text(f"{process.pid}\n")
                print(f"started {role} process {process.pid}; log: {log_path}", flush=True)
                return
        except OSError:
            time.sleep(0.2)
    process.terminate()
    raise RuntimeError(f"new {role} did not open port {probe_port}; check {log_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=tuple(ENTRIES))
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--engine-url", default="http://dartscore-engine:8765")
    parser.add_argument("--database", default="~/DartScore/runtime/game.sqlite3")
    args = parser.parse_args()
    unit = HOME / ".config/systemd/user" / UNITS[args.role]
    if unit.is_file():
        # The service manager owns the process once installed. Never launch a
        # second unmanaged copy beside it.
        result = subprocess.run(("systemctl", "--user", "restart", UNITS[args.role]),
                                capture_output=True, text=True, timeout=20)
        if result.returncode:
            raise RuntimeError(f"service restart failed: {result.stderr.strip()}")
        print(f"restarted {UNITS[args.role]}")
        return
    run = DEPLOY / "run"
    run.mkdir(mode=0o700, exist_ok=True)
    with (run / f"{args.role}.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        # Validate the target and persistent data before stopping a running game.
        if args.role == "engine" and not Path(args.database).expanduser().is_file():
            raise RuntimeError(f"game database missing: {args.database}; old engine left running")
        if not (DEPLOY / "SW" / ENTRIES[args.role]).is_file():
            raise RuntimeError("deployed entry point missing; old process left running")
        stop_old(args.role)
        start(args.role, args.bind, args.engine_url, args.database)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as exc:
        raise SystemExit(f"Process restart failed: {exc}") from None
