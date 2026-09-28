# DartScore

![DartScore: a player, dartboard, two cameras and a web scoreboard](Docs/images/dartscore-readme-hero.jpg)

DartScore is an open-source experiment in detecting darts with cameras and turning board hits into game scores. The repository contains a historical Python 3 single-camera MVP and a new, documented direction for a two-Pi system.

## Project status

- **Available now:** the original one-camera Pygame prototype, recorded test videos, a simple-score GameService, a durable camera-free simulator, an HTTP/SSE engine API, a web scoreboard/proxy, and optional boot-starting user services for the two Pis.
- **In design:** two-camera capture on a Raspberry Pi 5, 301/501 rules, browser kiosk startup, and status LEDs.
- **Accuracy:** the legacy detector is experimental. Replay candidate counts are a reproducible software baseline, not verified scoring accuracy.

The original MVP supports mounting and calibration states, one player, and a simple accumulating score. Its fixed 1680 × 1050 Pygame interface, hardcoded configuration and older camera dependencies have not been migrated to the new hardware. Do not treat the historical instructions as a current Pi 5 installation guide.

## Target architecture

The engine is deployed on a **Raspberry Pi 5 with 8 GB RAM** and a 512 GB M.2 SSD; two-camera capture is planned. A separate `GameService` applies game rules, owns game state, and persists accepted events. The engine exposes state, commands and events through a versioned HTTP/JSON API and server-sent events.

A **Raspberry Pi 4B with 2 GB RAM** serves the web UI and drives the screen. All player interaction happens in that browser; game rules and authoritative scores stay with the Pi 5. Both Pis use PoE and wired Ethernet. A display Pi restart does not reset a game.

For the initial web UI, the agreed controls are Start Game, Pause/Resume, and review of uncertain hits: confirm the proposed score, enter a correct single-dart score as points, or reject a false detection. Throws during Pause do not change game state and are not queued for Resume. Evidence images remain on the Pi 5 until manually deleted in the first version. Sector selection, 301/501 rules and automatic image cleanup are later implementation steps.

Read the design documents:

* [Two-Pi architecture and component migration](Docs/two-pi-architecture.md)
* [Engine/presentation API contract](Docs/engine-presentation-api-v1.md)
* [First web UI and uncertain-hit review](Docs/web-ui-first-release.md)

The architecture documents distinguish running components from planned camera and LED work.

## Simulate game input without cameras

The board-hit simulator exercises the extracted one-player game, uncertain-hit
review, Pause/Resume, and camera-health states without GPIO, Pygame, or video:

```sh
python3 SW/simulate_game.py Testdata/Simulations/basic_game.jsonl
python3 SW/simulate_game.py Testdata/Simulations/basic_game.jsonl --db runtime/game.sqlite3
python3 -m unittest discover -s tests -v
```

Each JSON Lines action produces a game snapshot and result. The example ends
with 80 points after a corrected hit; a throw during Pause is ignored. The
simulator is a developer tool. With `--db`, accepted actions, pending hits and
camera health recover after a process restart. Use a fresh database for a new
simulation scenario. See [the input contract](Docs/board-hit-input-and-simulator.md)
and [the persistence notes](Docs/durable-game-session.md).

## Deploy to two Pis for development

For iterative testing across two Pis, use
[the Python SSH/SFTP development deploy guide](Docs/two-pi-development-deploy.md).
It copies only the current engine code to the Pi 5 and presentation code to the
Pi 4B, keeping game data at its existing path, then restarts those processes.
Boot startup is available through optional per-user system services.
Use `--install-services` once after enabling user lingering on both Pis for
boot startup. For a shareable status/log report, run
`python3 deploy/collect_diagnostics.py`. See the deploy guide for details.

## Run the camera-free engine API

From the repository root, run `python3 SW/serve_engine.py --db runtime/game.sqlite3`.
It listens on loopback port 8765. State, health, commands and an SSE stream
are available for the existing `simple_score` game. Add `--dev-input` to
simulate board hits through a loopback-only development route. See
[the API contract and current scope](Docs/engine-presentation-api-v1.md).
Run `python3 SW/serve_presentation.py` in another terminal and open
`http://127.0.0.1:8080`. On the Pi 4B, set `--engine-url` to the Pi 5's
trusted-LAN address and use `--host 0.0.0.0` to serve its screen/browser.
See [web UI scope and setup](Docs/web-ui-first-release.md). The page
supports one-player simple score, Start, Pause/Resume, and pending-hit review;
it does not yet display stored evidence images.
For hands-on testing without cameras, use `python3 scripts/send_test_throw.py`
to submit one random dart (30% uncertain) and see
[the manual API command guide](Docs/manual-api-testing.md).

## Replay the legacy detector

The headless replay runs on a development computer without a camera, GPIO or Pygame. From the repository root, using Python 3.10 or later:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-replay.txt
.venv/bin/python SW/replay_video.py Testdata/Videos/dartscore_20191107_152701.avi --output replay-report.json
```

The JSON report contains frame numbers, timestamps, candidate points and legacy scores. The first bundled video produced 238 frames and 9 candidates in the documented baseline run. Those scores are not ground truth: replay assumes the first frame is an empty board and does not automatically calibrate the video. See [the replay notes](Docs/video-replay-baseline.md) for the second video, options and limitations.

## Development path

1. Label recorded throws and verify board-hit/scoring behavior.
2. Integrate Pi 5 hardware status, two-camera capture and independent calibration.
3. Validate 301/501 rules and detection accuracy before treating scores as reliable.

Historical prototype setup instructions are retained in [Legacy single-camera setup (2020)](Docs/legacy-single-camera-setup.md). The original code layout is described in [the software notes](SW/README.md).
The [legacy asset inventory](Docs/asset-inventory.md) lists unreferenced images
and other historical files for a later archive/removal decision.

Licensed under [GNU GPLv3](LICENSE).
