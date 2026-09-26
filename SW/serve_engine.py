"""Serve the camera-free durable engine API on a trusted interface."""

import argparse
from pathlib import Path

from DartScoreEngine.Api.server import EngineServer
from DartScoreEngine.Input.store import DurableSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("runtime/game.sqlite3"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--dev-input", action="store_true", help="enable simulated hits (loopback only)")
    args = parser.parse_args()
    if args.dev_input and args.host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("--dev-input requires a loopback host")
    with DurableSession(args.db) as store:
        with EngineServer((args.host, args.port), store, args.dev_input) as server:
            print(f"Engine API listening on http://{args.host}:{server.server_port}", flush=True)
            server.serve_forever()


if __name__ == "__main__":
    main()
