"""Same-origin browser server and narrow proxy to the Pi 5 engine API."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ASSETS = Path(__file__).parent / "static"
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}
ROUTES = {"/api/v1/state", "/api/v1/health", "/api/v1/events", "/api/v1/commands"}


class PresentationServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, engine_url):
        super().__init__(address, Handler)
        self.engine_url = engine_url.rstrip("/")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _response(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _unavailable(self):
        self._response(503, b'{"error":{"code":"engine_unavailable","message":"Cannot reach the engine"}}')

    def _proxy(self, method, body=None):
        try:
            request = Request(self.server.engine_url + self.path, data=body, method=method,
                              headers={"Content-Type": "application/json"} if body is not None else {})
            try:
                upstream = urlopen(request, timeout=35 if self.path.endswith("/events") else 5)
            except HTTPError as error:
                upstream = error
            with upstream:
                if self.path.endswith("/events") and upstream.status == 200:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    try:
                        while chunk := upstream.readline():
                            self.wfile.write(chunk)
                            self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                    finally:
                        self.close_connection = True
                else:
                    self._response(upstream.status, upstream.read(65537))
        except (URLError, TimeoutError, OSError):
            self._unavailable()

    def do_GET(self):
        if self.path in STATIC:
            filename, mime = STATIC[self.path]
            self._response(200, (ASSETS / filename).read_bytes(), mime)
        elif self.path in ROUTES - {"/api/v1/commands"}:
            self._proxy("GET")
        else:
            self._response(404, b'{"error":{"code":"not_found"}}')

    def do_POST(self):
        if self.path != "/api/v1/commands":
            self._response(404, b'{"error":{"code":"not_found"}}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("JSON body required (maximum 64 KiB)")
            body = self.rfile.read(length)
            json.loads(body)  # Reject malformed input before forwarding it.
        except (ValueError, UnicodeDecodeError):
            self._response(400, b'{"error":{"code":"invalid_command"}}')
            return
        self._proxy("POST", body)
