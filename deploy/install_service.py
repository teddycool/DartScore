#!/usr/bin/env python3
"""Install one boot-starting DartScore user service on its target Pi."""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from manage_process import DEPLOY, ENTRIES, stop_old

UNITS = {"engine": "dartscore-engine.service", "presentation": "dartscore-presentation.service"}


def run(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True, timeout=20)


def unit_text(role, bind, engine_url, database):
    program = DEPLOY / "SW" / ENTRIES[role]
    command = [sys.executable, "-B", str(program)]
    if role == "engine":
        command += ["--db", str(Path(database).expanduser()), "--host", bind]
    else:
        command += ["--engine-url", engine_url]
    if any(not item or any(char.isspace() for char in item) for item in command):
        raise ValueError("service paths and arguments must not contain whitespace")
    return (f"[Unit]\nDescription=DartScore {role}\nStartLimitIntervalSec=0\n\n"
            f"[Service]\nType=simple\nWorkingDirectory={DEPLOY}\n"
            f"ExecStart={' '.join(command)}\nRestart=on-failure\nRestartSec=3\n"
            f"Environment=PYTHONUNBUFFERED=1\n\n[Install]\nWantedBy=default.target\n")


def install(role, bind, engine_url, database):
    if role == "engine" and not Path(database).expanduser().is_file():
        raise RuntimeError("game database is missing; existing process was left running")
    if not (DEPLOY / "SW" / ENTRIES[role]).is_file():
        raise RuntimeError("deployed entry point missing; existing process was left running")
    linger = run("loginctl", "show-user", str(os.getuid()), "-p", "Linger", "--value")
    if linger.stdout.strip() != "yes":
        raise RuntimeError("boot startup requires linger: run 'sudo loginctl enable-linger $(whoami)' on this Pi, then retry")
    content = unit_text(role, bind, engine_url, database)
    unit_dir = Path.home() / ".config/systemd/user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    unit = unit_dir / UNITS[role]
    if unit.exists():
        run("systemctl", "--user", "stop", UNITS[role], check=False)
    stop_old(role)
    unit.write_text(content, encoding="utf-8")
    run("systemctl", "--user", "daemon-reload")
    run("systemctl", "--user", "enable", "--now", UNITS[role])
    for _ in range(20):
        if run("systemctl", "--user", "is-active", "--quiet", UNITS[role], check=False).returncode == 0:
            print(f"enabled and started {UNITS[role]}")
            return
        time.sleep(0.5)
    raise RuntimeError(f"service did not start; inspect: journalctl --user -u {UNITS[role]} -n 80")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=tuple(UNITS))
    parser.add_argument("--bind")
    parser.add_argument("--engine-url")
    parser.add_argument("--database")
    args = parser.parse_args()
    if args.role == "engine" and (not args.bind or not args.database):
        parser.error("engine requires --bind and --database")
    if args.role == "presentation" and not args.engine_url:
        parser.error("presentation requires --engine-url")
    install(args.role, args.bind, args.engine_url, args.database)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Service installation failed: {exc}") from None
