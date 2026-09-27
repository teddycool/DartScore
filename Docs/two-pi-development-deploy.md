# Iterating on two Pis before system services

The development deployer copies the current camera-free components to the correct Pi over SSH/SFTP. Run it on your development computer; the Pis need SSH enabled and Python 3.10 or newer. It does not require `rsync` or a Git checkout on either Pi.

## Setup on the development computer

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-deploy.txt
cp deploy/deploy.example.yaml deploy/deploy.local.yaml
chmod 600 deploy/deploy.local.yaml
```

Edit `deploy/deploy.local.yaml` with the real `ip` or `host`, `user`, and optionally `password` for each Pi. `ip` takes priority when supplied. Passwords are plain text in this local file, which Git ignores; leave `password: null` to be prompted or use `password: ""` for SSH key/agent authentication. Keep the template free of real credentials. The script checks server host keys against the development computer's SSH `known_hosts`; first connect with normal `ssh user@address` and verify/accept its fingerprint. Use the **IP** as `address` when the config selects an IP, since SSH host keys are checked for the address actually used.

If there is **no local config file**, the script uses `dartscore-engine` and `dartscore-presentation` and asks for a username and password for each selected Pi. `--dry-run` shows the default hostnames and file list without prompting or connecting. If the hostnames do not resolve, create the config and set `ip` values.

## Deploy

```sh
.venv/bin/python deploy/deploy_two_pis.py --dry-run
.venv/bin/python deploy/deploy_two_pis.py
.venv/bin/python deploy/deploy_two_pis.py --only presentation
```

Use `--only engine` for engine-only changes. `--config /path/to/config.yaml` selects another config. The script compares SHA-256 hashes and copies only changed files. It sends the GameService, input coordinator, durable session, API, and simulator **only to the Pi 5**; it sends the presentation server and static browser assets **only to the Pi 4B**. A small process manager and `SW/__init__.py` go to both. Vision and Pygame are not in this camera-free deployment.

After copying, the script stops the selected Pi's old `serve_engine.py` or `serve_presentation.py` process (whether started from `~/DartScore` or `~/dartscore-deploy`) and starts the deployed version. It matches only these entry points owned by the SSH user; if an old process will not stop, it does not force-kill it or start a duplicate. The Pi 5 starts first, then the Pi 4B. `--only` restarts just one role. Add `--copy-only` to upload files without touching processes. `--dry-run` neither connects nor restarts. The Pi 5 restart requires its existing database at `engine.database_path` in the local YAML (default `~/DartScore/runtime/game.sqlite3`); a missing database aborts before stopping the old engine. The Pi 4B connects to the engine IP/hostname in that same config. Logs are in `~/dartscore-deploy/run/engine.log` and `presentation.log` respectively.

Each Pi receives code under `~/dartscore-deploy/SW/`. The script never copies local credentials to a Pi, overwrites `~/DartScore`, deletes files, or migrates SQLite data. Remove obsolete files in `~/dartscore-deploy` manually if a later refactor deletes or renames code paths.

## Run the deployed code with the existing game

The deployer normally does this automatically. For manual troubleshooting, on the Pi 5 start the **deployed code** using the current **absolute database path**:

```sh
python3 "$HOME/dartscore-deploy/SW/serve_engine.py" --db "$HOME/DartScore/runtime/game.sqlite3" --host 192.168.1.65
```

On the Pi 4B, run:

```sh
python3 "$HOME/dartscore-deploy/SW/serve_presentation.py" --engine-url http://192.168.1.65:8765
```

Adjust the Pi 5 IP in these commands if needed. Open `http://127.0.0.1:8080` on the connected screen. Refresh the browser after deploying changed HTML/CSS/JavaScript so it loads the new files; subsequent engine restarts should reconnect automatically. The Pi 5 journal remains at the same path. If your current database lives elsewhere, substitute that exact path instead of starting with an empty game.

This workflow starts processes for development but not after a reboot. Once the code and data paths are settled, system services can replace this process manager and start the same deployed commands automatically.
