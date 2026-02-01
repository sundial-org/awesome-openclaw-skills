#!/usr/bin/env python3
"""Serve the ATP dashboard with live data from trust.json and interactions.jsonl."""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ATP_DIR = Path.home() / ".atp"
TRUST_DB = ATP_DIR / "trust.json"
INTERACTIONS_DB = ATP_DIR / "interactions.jsonl"
DASHBOARD = Path(__file__).parent / "dashboard.html"
PORT = 8420


class ATPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/trust":
            self._json_response(self._load_trust())
        elif self.path == "/api/interactions":
            self._json_response(self._load_interactions())
        elif self.path == "/" or self.path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD.read_bytes())
        else:
            self.send_error(404)

    def _json_response(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _load_trust(self):
        if TRUST_DB.exists():
            return json.loads(TRUST_DB.read_text())
        return {"agents": {}, "edges": [], "self": {}}

    def _load_interactions(self):
        if not INTERACTIONS_DB.exists():
            return []
        records = []
        for line in INTERACTIONS_DB.read_text().strip().split("\n"):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return records

    def log_message(self, format, *args):
        pass  # silence request logs


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), ATPHandler)
    print(f"ATP Dashboard: http://localhost:{PORT}")
    server.serve_forever()
