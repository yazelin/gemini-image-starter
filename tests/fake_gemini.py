"""A tiny local stand-in for the Gemini image API, for API-key-free tests.

It answers any POST with a Gemini-shaped response whose inlineData is a fixed
1x1 PNG, so the real client code path (build body -> POST -> parse inlineData
-> decode) runs end to end without a key or network.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# a valid 1x1 transparent PNG, base64
PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
    "2mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        body = json.dumps(
            {
                "candidates": [
                    {"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": PNG_B64}}]}}
                ]
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence
        pass


def start():
    """Start the fake server on a random port. Returns (server, base_url)."""
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/v1beta/models"
