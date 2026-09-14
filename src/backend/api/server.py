"""Standalone HTTP server implementation for Chain Guard AI REST API.

Built on Python's standard library ThreadingHTTPServer, providing zero-dependency,
thread-safe, CORS-enabled HTTP endpoints out of the box.
"""

import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional

from .router import route_request
from ..config import SERVER_HOST, SERVER_PORT


class ChainGuardRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler dispatching to the Chain Guard API router."""

    def _set_cors_headers(self, status_code: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("X-Powered-By", "ChainGuard-AI-Core")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight inquiries."""
        self._set_cors_headers(200)
        self.wfile.write(b'{"status":"cors_ready"}')

    def do_GET(self) -> None:
        """Handle GET requests."""
        status_code, response_data = route_request("GET", self.path)
        self._set_cors_headers(status_code)
        self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))

    def do_POST(self) -> None:
        """Handle POST requests with JSON payload."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = None
        if content_length > 0:
            try:
                raw_body = self.rfile.read(content_length).decode("utf-8")
                body = json.loads(raw_body)
            except Exception as e:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}).encode("utf-8"))
                return

        status_code, response_data = route_request("POST", self.path, body=body)
        self._set_cors_headers(status_code)
        self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        """Custom concise logging format."""
        # Clean terminal output for hackathon demonstrations
        pass


def run_server(host: str = SERVER_HOST, port: int = SERVER_PORT) -> None:
    """Launch the Chain Guard API server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, ChainGuardRequestHandler)
    print(f"🛡️  Chain Guard AI API Server active at http://{host}:{port}")
    print(f"📡 Ready to receive frontend requests and AI optimization hooks.")
    print(f"📌 Health Check: http://{host}:{port}/api/health")
    print(f"📌 Disruptions: http://{host}:{port}/api/disruptions/affected-shipments")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Chain Guard AI server...")
        httpd.server_close()
