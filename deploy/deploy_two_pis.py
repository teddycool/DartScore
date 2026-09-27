#!/usr/bin/env python3
"""Copy the current camera-free components to the matching Raspberry Pis."""

import argparse
import getpass
import hashlib
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "deploy" / "deploy.local.yaml"
DEPLOY_DIR = "dartscore-deploy"
TARGETS = {"engine": "dartscore-engine", "presentation": "dartscore-presentation"}
FILES = {
    "engine": ("SW/__init__.py", "SW/DartScoreEngine/__init__.py",
               "SW/DartScoreEngine/Api", "SW/DartScoreEngine/Game",
               "SW/DartScoreEngine/Input", "SW/serve_engine.py", "SW/simulate_game.py"),
    "presentation": ("SW/__init__.py", "SW/Presentation", "SW/serve_presentation.py"),
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
        if not isinstance(values, dict) or set(values) - {"host", "ip", "user", "password", "port"}:
            raise ValueError(f"invalid {role} configuration")
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


def deploy(role, info, files):
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
    print(f"[{role}] {changed} updated, {len(files) - changed} unchanged")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help="local YAML configuration (default: deploy/deploy.local.yaml)")
    parser.add_argument("--only", choices=tuple(TARGETS), help="deploy one Pi only")
    parser.add_argument("--dry-run", action="store_true", help="print plan without connecting or prompting")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    for role in ((args.only,) if args.only else TARGETS):
        files = manifest(role)
        info = connection_info(role, config, args.dry_run)
        host, port, user, _password = info
        print(f"[{role}] {user + '@' if user else ''}{host}:{port} -> ~/{DEPLOY_DIR}/")
        if args.dry_run:
            for path in files:
                print(f"  {path}")
        else:
            deploy(role, info, files)
    if not args.dry_run:
        print("Copy complete. Restart the selected process to use the new code.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        raise SystemExit(f"Deploy failed: {exc}") from None
