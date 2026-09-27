#!/usr/bin/env python3
"""Copy the current camera-free components to the matching Raspberry Pis."""

import argparse
import getpass
import hashlib
import json
import shlex
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "deploy" / "deploy.local.yaml"
DEPLOY_DIR = "dartscore-deploy"
TARGETS = {"engine": "dartscore-engine", "presentation": "dartscore-presentation"}
FILES = {
    "engine": ("deploy/manage_process.py", "deploy/install_service.py", "SW/__init__.py", "SW/DartScoreEngine/__init__.py",
               "SW/DartScoreEngine/Api", "SW/DartScoreEngine/Game",
               "SW/DartScoreEngine/Input", "SW/serve_engine.py", "SW/simulate_game.py"),
    "presentation": ("deploy/manage_process.py", "deploy/install_service.py", "SW/__init__.py", "SW/Presentation", "SW/serve_presentation.py"),
}


def manifest(role):
    """Return repository-relative regular files owned by this Pi only."""
    paths = []
    for entry in FILES[role]:
        source = ROOT / entry
        candidates = source.rglob("*") if source.is_dir() else (source,)
        for candidate in candidates:
            if candidate.is_file() and not candidate.is_symlink() and not any(
                    part == "__pycache__" for part in candidate.parts) and candidate.suffix != ".pyc":
                paths.append(candidate.relative_to(ROOT))
    if not paths:
        raise ValueError(f"no files found for {role}")
    return tuple(sorted(set(paths)))


def load_config(path):
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Install deploy dependencies: python3 -m pip install -r requirements-deploy.txt") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("deploy config must be a YAML mapping")
    unknown = set(data) - set(TARGETS)
    if unknown:
        raise ValueError(f"unknown deploy targets: {', '.join(sorted(unknown))}")
    for role, values in data.items():
        allowed = {"host", "ip", "user", "password", "port"}
        if role == "engine":
            allowed.add("database_path")
        if not isinstance(values, dict) or set(values) - allowed:
            raise ValueError(f"invalid {role} configuration")
        if role == "engine" and "database_path" in values and (
                not isinstance(values["database_path"], str) or not values["database_path"]):
            raise ValueError("engine.database_path must be a non-empty path")
    return data


def connection_info(role, config, dry_run=False):
    values = config.get(role, {})
    host = values.get("ip") or values.get("host") or TARGETS[role]
    port = values.get("port", 22)
    if not isinstance(host, str) or not host or type(port) is not int or not 1 <= port <= 65535:
        raise ValueError(f"invalid host or port for {role}")
    user = values.get("user")
    if user is not None and (not isinstance(user, str) or not user):
        raise ValueError(f"invalid user for {role}")
    if not dry_run and not user:
        user = input(f"SSH user for {role} ({host}): ").strip()
        if not user:
            raise ValueError("SSH user is required")
    password = values.get("password")
    if password is not None and not isinstance(password, str):
        raise ValueError(f"invalid password for {role}")
    if not dry_run and password is None:
        password = getpass.getpass(f"SSH password for {user}@{host} (Enter for SSH key): ")
    return host, port, user, password


def digest(stream):
    result = hashlib.sha256()
    while chunk := stream.read(65536):
        result.update(chunk)
    return result.digest()


def mkdirs(sftp, path):
    current = ""
    for component in path.strip("/").split("/"):
        current += "/" + component
        try:
            mode = sftp.stat(current).st_mode
            if not stat.S_ISDIR(mode):
                raise ValueError(f"remote path is not a directory: {current}")
        except FileNotFoundError:
            sftp.mkdir(current)


def deploy(role, info, files, *, restart=True, install_services=False,
           engine_address=None, database_path=None):
    try:
        import paramiko
    except ImportError as exc:
        raise RuntimeError("Install deploy dependencies: python3 -m pip install -r requirements-deploy.txt") from exc
    host, port, user, password = info
    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        ssh.connect(host, port=port, username=user, password=password or None,
                    timeout=10, auth_timeout=10, banner_timeout=10)
        with ssh.open_sftp() as sftp:
            home = sftp.normalize(".").rstrip("/")
            destination = home + "/" + DEPLOY_DIR
            mkdirs(sftp, destination)
            changed = 0
            for relative in files:
                local = ROOT / relative
                remote = destination + "/" + relative.as_posix()
                mkdirs(sftp, remote.rsplit("/", 1)[0])
                try:
                    with sftp.open(remote, "rb") as incoming, local.open("rb") as outgoing:
                        if digest(incoming) == digest(outgoing):
                            continue
                except FileNotFoundError:
                    pass
                sftp.put(str(local), remote, confirm=True)
                print(f"  copied {relative}")
                changed += 1
            revision = subprocess.run(("git", "rev-parse", "HEAD"), cwd=ROOT,
                                      capture_output=True, text=True, check=False).stdout.strip()
            dirty = bool(subprocess.run(("git", "status", "--porcelain"), cwd=ROOT,
                                        capture_output=True, text=True, check=False).stdout.strip())
            marker = {"role": role, "source_commit": revision or "unknown", "dirty": dirty,
                      "deployed_at": datetime.now(timezone.utc).isoformat()}
            with sftp.open(destination + "/deploy/deployed.json", "w") as target:
                target.write(json.dumps(marker) + "\n")
        if restart or install_services:
            helper = "install_service.py" if install_services else "manage_process.py"
            command = ["python3", destination + "/deploy/" + helper, role]
            if role == "engine":
                command += ["--bind", host, "--database", database_path or
                            "~/DartScore/runtime/game.sqlite3"]
            else:
                command += ["--engine-url", f"http://{engine_address}:8765"]
            _stdin, stdout, stderr = ssh.exec_command(shlex.join(command), timeout=25)
            output = stdout.read().decode("utf-8", errors="replace")
            error = stderr.read().decode("utf-8", errors="replace")
            code = stdout.channel.recv_exit_status()
            if output.strip():
                print(output.rstrip())
            if code:
                raise RuntimeError(f"{role} restart failed: {error.strip() or output.strip()}")
    print(f"[{role}] {changed} updated, {len(files) - changed} unchanged")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help="local YAML configuration (default: deploy/deploy.local.yaml)")
    parser.add_argument("--only", choices=tuple(TARGETS), help="deploy one Pi only")
    parser.add_argument("--dry-run", action="store_true", help="print plan without connecting or prompting")
    parser.add_argument("--copy-only", action="store_true", help="copy code without restarting processes")
    parser.add_argument("--install-services", action="store_true", help="one-time boot service installation")
    args = parser.parse_args(argv)
    if args.copy_only and args.install_services:
        parser.error("--copy-only and --install-services cannot be combined")
    config = load_config(args.config)
    engine_values = config.get("engine", {})
    engine_address = engine_values.get("ip") or engine_values.get("host") or TARGETS["engine"]
    database_path = engine_values.get("database_path")
    for role in ((args.only,) if args.only else TARGETS):
        files = manifest(role)
        info = connection_info(role, config, args.dry_run)
        host, port, user, _password = info
        print(f"[{role}] {user + '@' if user else ''}{host}:{port} -> ~/{DEPLOY_DIR}/")
        if args.dry_run:
            for path in files:
                print(f"  {path}")
        else:
            deploy(role, info, files, restart=not args.copy_only,
                   install_services=args.install_services,
                   engine_address=engine_address, database_path=database_path)
    if not args.dry_run:
        print("Copy complete." + (" Processes left running as-is." if args.copy_only else
                                  " Selected services installed and started." if args.install_services else
                                  " Selected processes restarted from deployed code."))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        raise SystemExit(f"Deploy failed: {exc}") from None
