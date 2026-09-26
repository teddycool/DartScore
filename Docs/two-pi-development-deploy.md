# Iterating on two Pis before system services

The camera-free engine and presentation can be deployed directly from a developer checkout over SSH. Install `rsync` and `openssh-client` on the development computer and `rsync`, `openssh-server` and `python3` on each Pi. Configure SSH access to both Pis first. This workflow does not require a Git checkout on the Pis.

From the developer checkout:

```sh
./deploy/deploy_two_pis.sh --engine pi@192.168.1.65 --presentation pi@dartscore-p4 --dry-run
./deploy/deploy_two_pis.sh --engine pi@192.168.1.65 --presentation pi@dartscore-p4
```

Adjust the SSH usernames/hosts to the actual values. Use `--only engine` or `--only presentation` with the corresponding destination when iterating on one process. The dry run prints the exact component manifest and destinations without connecting to the Pis. A real deploy uses `rsync` and prints changed files.

Each Pi receives its own code under `~/dartscore-deploy/SW/`. The script does not overwrite `~/DartScore`, delete files, migrate SQLite data, or stop/restart processes. The Pi 4B receives only the presentation server and static browser files; the Pi 5 receives the GameService, input coordinator, durable session, API and simulator. Vision and Pygame are not part of this camera-free deployment. Remove obsolete files in `~/dartscore-deploy` manually if a later refactor deletes or renames code paths.

For the current test database already stored in the Pi 5's Git checkout, stop its old engine process and start the **deployed code** using the existing **absolute database path**:

```sh
python3 "$HOME/dartscore-deploy/SW/serve_engine.py" --db "$HOME/DartScore/runtime/game.sqlite3" --host 192.168.1.65
```

On the Pi 4B, stop its old presentation process and run:

```sh
python3 "$HOME/dartscore-deploy/SW/serve_presentation.py" --engine-url http://192.168.1.65:8765
```

Open `http://127.0.0.1:8080` on its connected screen. Refresh the browser after deploying a changed HTML/CSS/JavaScript file so it loads the new code. Subsequent engine restarts should reconnect automatically. The Pi 5 journal remains in `~/DartScore/runtime/game.sqlite3`; a Pi 4B deploy has no score storage to migrate. If your current database lives somewhere else, substitute its exact path rather than starting with a new empty one.

This workflow copies code but intentionally leaves process startup manual. After the code locations and data path are settled, system services can start the deployed commands automatically and log to the journal.
