#!/usr/bin/env python3
"""Collect bounded, shareable Pi service and API diagnostics; no DB or images."""

import argparse
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path

from deploy_two_pis import DEFAULT_CONFIG, TARGETS, connection_info, load_config

ROOT = Path(__file__).resolve().parents[1]
MASK = re.compile(r"(?i)\b(password|token|secret|api[_-]?key)\b\s*[:=]\s*[^\s,;]+")
MAX_BYTES = 65536


def redact(value):
    return MASK.sub(lambda match: match.group(1) + "=<redacted>", value)


def remote(ssh, args):
    _stdin, stdout, stderr = ssh.exec_command(shlex.join(args), timeout=15)
    content = stdout.read(MAX_BYTES + 1).decode("utf-8", errors="replace")
    errors = stderr.read(4096).decode("utf-8", errors="replace")
    status = stdout.channel.recv_exit_status()
    if len(content) > MAX_BYTES:
        content = content[:MAX_BYTES] + "\n[truncated]"
    return {"exit_code": status, "output": redact(content), "error": redact(errors)}


def collect(role, info, engine_address):
    import paramiko
    host, port, user, password = info
    unit = f"dartscore-{role}.service"
    base = "http://" + (engine_address + ":8765" if role == "engine" else "127.0.0.1:8080")
    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.connect(host, port=port, username=user, password=password or None,
                    timeout=10, auth_timeout=10, banner_timeout=10)
        commands = {
            "service": ["systemctl", "--user", "show", unit,
                        "--property=ActiveState,SubState,UnitFileState,ExecMainPID,NRestarts"],
            "journal": ["journalctl", "--user", "-u", unit, "-n", "200", "--no-pager", "-o", "short-iso"],
            "os": ["uname", "-a"],
            "disk": ["df", "-h", "."],
            "deployed": ["cat", "dartscore-deploy/deploy/deployed.json"],
        }
        probe = ("import urllib.request,urllib.error,sys; u=sys.argv[1]"
                 "\ntry:\n r=urllib.request.urlopen(u,timeout=3); print(r.status, r.read(16384).decode())"
                 "\nexcept urllib.error.HTTPError as e: print(e.code, e.read(16384).decode())")
        for endpoint in ("state", "health"):
            commands[endpoint] = ["python3", "-c", probe, base + "/api/v1/" + endpoint]
        return {"host": host, "role": role,
                "checks": {name: remote(ssh, argv) for name, argv in commands.items()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--only", choices=tuple(TARGETS))
    parser.add_argument("--out", type=Path, help="JSON report path (default: reports/timestamp.json)")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    engine_values = config.get("engine", {})
    engine_address = engine_values.get("ip") or engine_values.get("host") or TARGETS["engine"]
    report = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
              "description": "Bounded service, journal, disk and HTTP state/health; no DB or images",
              "targets": []}
    for role in ((args.only,) if args.only else TARGETS):
        info = connection_info(role, config)
        try:
            report["targets"].append(collect(role, info, engine_address))
        except Exception as exc:
            report["targets"].append({"role": role, "host": info[0],
                                      "error": redact(f"{type(exc).__name__}: {exc}")})
    target = args.out or ROOT / "reports" / ("dartscore-" +
              datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Diagnostics saved to {target}")
    if any("error" in entry for entry in report["targets"]):
        raise SystemExit("Some targets could not be inspected; the report includes their errors")


if __name__ == "__main__":
    main()
