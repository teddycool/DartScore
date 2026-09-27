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

If there is **no local config file**, the script asks for an IP address or hostname, username (default `pi`), and password for each selected Pi. The engine database path is also requested when starting/restarting the engine. Within one run, an address or credential is requested only once per Pi; the Pi 4B's engine URL reuses the engine address already entered. `--dry-run` shows placeholders for missing addresses and the file list without prompting or connecting. A presentation-only copy with `--copy-only` needs no engine address.

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
python3 "$HOME/dartscore-deploy/SW/serve_engine.py" --db "$HOME/DartScore/runtime/game.sqlite3" --host 192.168.1.64
```

On the Pi 4B, run:

```sh
python3 "$HOME/dartscore-deploy/SW/serve_presentation.py" --engine-url http://192.168.1.64:8765
```

Adjust the Pi 5 IP in these commands if needed. Open `http://127.0.0.1:8080` on the connected screen. Refresh the browser after deploying changed HTML/CSS/JavaScript so it loads the new files; subsequent engine restarts should reconnect automatically. The Pi 5 journal remains at the same path. If your current database lives elsewhere, substitute that exact path instead of starting with an empty game.

Without the optional system services below, deployed processes do not start after a Pi reboot.

## Enable boot startup once

On **each Pi**, enable lingering for the SSH user (for example `psk` on the engine and `pi` on presentation):

```sh
sudo loginctl enable-linger "$(whoami)"
```

Then from the development computer run:

```sh
.venv/bin/python deploy/deploy_two_pis.py --install-services
```

The installer checks lingering and the engine's existing database **before** it stops the old process. It installs `dartscore-engine.service` or `dartscore-presentation.service` under the SSH user's `~/.config/systemd/user/`, enables it for boot and starts it. From then on the regular deploy command copies code and uses `systemctl --user restart` for that Pi instead of launching a second unmanaged process. The services write to the user journal and retry failed startup; the Pi 4B page reconnects after the Pi 5 becomes available. `--copy-only` leaves them running.

On a Pi, inspect a service with `systemctl --user status dartscore-engine.service` (or `dartscore-presentation.service`) and its log with `journalctl --user -u dartscore-engine.service -n 80 --no-pager`. The engine still uses `engine.database_path` from your local deploy YAML (default `~/DartScore/runtime/game.sqlite3`). If its address changes, update the YAML and run `--install-services` again to regenerate both units. The Pi 4B browser itself is not yet launched in kiosk mode; the service hosts the page for the screen's browser.

## Collect a shareable diagnostic report

```sh
.venv/bin/python deploy/collect_diagnostics.py
.venv/bin/python deploy/collect_diagnostics.py --only engine
```

The command saves a timestamped JSON report under ignored `reports/` on your development computer. It records each service's state, up to 200 journal lines, disk summary, deployed source commit and API state/health. It does **not** copy the database, YAML config, passwords or images. Log text is bounded and common credential assignments are masked; review the report before sharing it, since application log lines and pending evidence references can contain your own data. Upload that report when asking for help here or in Copilot.
