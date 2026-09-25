"""Replay the legacy single-camera detector against a local video.

This diagnostic assumes the first frame shows an empty board. It records
candidate events, not validated dart scores.
"""

import argparse
import json
from pathlib import Path

import cv2

from DartScoreEngine.Vision.DartDetector import DartDetector


def replay(video: Path, output: Path, max_frames: int | None = None, debug_dir: Path | None = None):
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video}")
    if debug_dir is not None:
        debug_dir.mkdir(parents=True, exist_ok=True)

    events = []
    frames = 0
    errors = []
    detector = None
    previous = None
    board_state = None
    stable_frames = 0
    locked = False
    fps = capture.get(cv2.CAP_PROP_FPS)
    try:
        while max_frames is None or frames < max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            frames += 1
            if detector is None:
                detector = DartDetector(frame, debug_dir=debug_dir)
                previous = board_state = frame.copy()
                continue

            if detector.boardEmpty(frame):
                board_state = frame.copy()
                stable_frames = 0
                locked = False
            elif detector.boardChanged(frame, previous):
                stable_frames = 0
                locked = False
            else:
                stable_frames += 1
                if not locked:
                    try:
                        detected = detector.detectDart(frame, board_state)
                        if detected:
                            score = detector._lastscore
                            events.append({"frame": frames, "time_seconds": round((frames - 1) / fps, 3) if fps > 0 else None,
                                           "point": list(map(int, detector._lasthitcoords)) if detector._lasthitcoords is not None else None,
                                           "score": int(score) if score is not None else None})
                            board_state = frame.copy()
                            locked = True
                    except (TypeError, ValueError, IndexError) as exc:
                        errors.append({"frame": frames, "error": f"{type(exc).__name__}: {exc}"})
                        locked = True
            previous = frame.copy()
    finally:
        capture.release()
    if frames == 0:
        raise ValueError(f"Video contains no readable frames: {video}")

    result = {"video": str(video), "frames": frames, "fps": fps, "candidate_events": events,
              "detection_errors": errors,
              "limitations": "First frame assumed empty; video is not automatically calibrated; scores are unverified."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--output", type=Path, default=Path("replay-report.json"))
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--debug-dir", type=Path)
    args = parser.parse_args()
    result = replay(args.video, args.output, args.max_frames, args.debug_dir)
    print(f"{result['frames']} frames, {len(result['candidate_events'])} candidates, "
          f"{len(result['detection_errors'])} errors -> {args.output}")


if __name__ == "__main__":
    main()
