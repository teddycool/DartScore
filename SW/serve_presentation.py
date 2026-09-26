"""Run the Pi 4B scoreboard/proxy against a Pi 5 engine URL."""

import argparse

from Presentation.server import PresentationServer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-url", default="http://127.0.0.1:8765")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    with PresentationServer((args.host, args.port), args.engine_url) as server:
        print(f"Scoreboard at http://{args.host}:{server.server_port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
