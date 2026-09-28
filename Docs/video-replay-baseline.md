# Recorded-video baseline

This is a diagnostic entry point for the old single-camera detector. It runs on a
development computer without GPIO, Pygame, a network camera, or the fixed
`/home/pi/DartScore` installation path.

From the repository root, using Python 3.10 or later:

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-replay.txt
.venv/bin/python SW/replay_video.py Testdata/Videos/dartscore_20191107_152701.avi --output replay-report.json
```

The JSON report lists frame numbers, video timestamps, candidate points and
legacy scores, plus detector errors. `--max-frames N` limits a diagnostic run;
`--debug-dir DIR` writes threshold images on detection attempts. Debug images
are disabled by default. The old detector and board scorer still print verbose
diagnostics to stdout.

Observed with Python 3.12, OpenCV 5.0.0 and NumPy 2.5.3:

| Video | Frames | Candidates | Detector errors |
| --- | ---: | ---: | ---: |
| `dartscore_20191107_152701.avi` | 238 | 9 | 0 |
| `dartscore_20191205_185227.avi` | 318 | 8 | 0 |

These candidate counts are **not accuracy measurements**. Replay assumes that
the first frame shows an empty board and does not automatically load or create
a camera calibration transform. Scores may therefore be wrong. No labelled
ground truth exists in the repository for these recordings. The next step is
to label throws and compare them with calibrated candidate locations before
changing detection or adding another camera.

This command does not run the legacy Pygame application. Its full Pi 5 and
current OS compatibility remains to be addressed separately.
