#!/usr/bin/env python3
"""Send one randomly scored dart to the local engine developer-input API."""

import argparse
import json
import random
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "SW"))
from DartScoreEngine.Game.service import VALID_DART_POINTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-url", default="http://127.0.0.1:8765",
                        help="local engine with --dev-input (default: http://127.0.0.1:8765)")
    parser.add_argument("--uncertain-percent", type=float, default=30,
                        help="chance of an uncertain dart, from 0 to 100 (default: 30)")
    args = parser.parse_args()
    if not 0 <= args.uncertain_percent <= 100:
        parser.error("--uncertain-percent must be between 0 and 100")

    rng = random.SystemRandom()
    throw_id = str(uuid.uuid4())
    action = {
        "request_id": throw_id, "throw_id": throw_id,
        "type": "uncertain" if rng.random() < args.uncertain_percent / 100 else "hit",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual_test", "points": rng.choice(sorted(VALID_DART_POINTS)),
    }
    request = Request(args.engine_url.rstrip("/") + "/api/v1/dev/actions",
                      data=json.dumps(action).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
    except HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise SystemExit(1) from None
    except URLError as exc:
        print(f"Cannot reach engine: {exc.reason}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"Dart: {action['type']}, {action['points']} points, ID {throw_id}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
