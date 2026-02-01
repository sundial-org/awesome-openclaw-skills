#!/usr/bin/env python3
"""
Campaign Webhook Handler - Processes Dialpad replies → terminates campaigns

Usage:
    python3 webhook_handler.py [--port 8080]
    
This script should be running as a webhook server to receive
SMS replies from Dialpad and terminate corresponding campaigns.
"""

import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
WORKSPACE = os.environ.get("WORKSPACE", "/home/art/niemand")
STATE_FILE = f"{WORKSPACE}/state/campaign-orchestrator/campaigns.json"
PORT = int(os.environ.get("WEBHOOK_PORT", "8081"))


def load_campaigns():
    """Load campaign state from file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"campaigns": {}, "templates": {}}


def save_campaigns(data):
    """Save campaign state to file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def terminate_campaign(lead_phone, lead_name, message):
    """Terminate campaign when lead replies."""
    data = load_campaigns()
    campaigns = data.get("campaigns", {})

    terminated = []

    for name, campaign in campaigns.items():
        if campaign["status"] != "active":
            continue

        # Check if this campaign was for this lead
        # Match by phone number or name
        if name == lead_name or name.lower() in message.lower():
            campaign["status"] = "terminated"
            campaign["terminated_reason"] = "lead_replied"
            campaign["terminated_at"] = datetime.now().isoformat()
            campaign["reply_message"] = message

            # Mark remaining steps as cancelled
            for step in campaign["steps"]:
                if step["status"] == "pending":
                    step["status"] = "cancelled"

            terminated.append(name)
            print(f"Terminated campaign: {name}")

    if terminated:
        save_campaigns(data)
        # TODO: Log reply to Attio
        # attio note companies "uuid" "Lead replied: {message}"
    else:
        print(f"No active campaign found for lead: {lead_name}")

    return terminated


class CampaignWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {"raw": body}

        timestamp = datetime.now().isoformat()

        # Extract lead info from Dialpad webhook
        from_number = data.get("from_number", "")
        to_number = data.get("to_number", [{}])[0] if isinstance(data.get("to_number"), list) else data.get("to_number", {})
        message = data.get("text", data.get("text_content", ""))

        # Try to extract lead name from contacts
        contact = data.get("contact", {})
        lead_name = contact.get("name", from_number)

        print(f"[{timestamp}] Received reply from {lead_name} ({from_number}): {message[:50]}...")

        # Terminate matching campaigns
        terminated = terminate_campaign(from_number, lead_name, message)

        # Send 200 OK
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"status": "ok", "terminated": terminated}
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def main():
    server = HTTPServer(("", PORT), CampaignWebhookHandler)
    print(f"Campaign Webhook Handler running on port {PORT}")
    print(f"Listening for Dialpad SMS replies...")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
