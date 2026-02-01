import os
import requests
import json
import sys

class SlackHub:
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.base_url = "https://slack.com/api"

    def _call(self, endpoint, data=None):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        response = requests.post(f"{self.base_url}/{endpoint}", headers=headers, json=data)
        return response.json()

    def send(self, target, message, thread_ts=None):
        data = {"channel": target, "text": message}
        if thread_ts:
            data["thread_ts"] = thread_ts
        return self._call("chat.postMessage", data)

    def search(self, query):
        # Slack search API requires different headers/method usually
        params = {"query": query}
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/search.messages", headers=headers, params=params)
        return response.json()

if __name__ == "__main__":
    import argparse
    hub = SlackHub()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["send", "search", "list"])
    parser.add_argument("--target")
    parser.add_argument("--message")
    parser.add_argument("--query")
    args = parser.parse_args()

    if args.action == "list":
        print(json.dumps(hub._call("conversations.list", {"types": "public_channel,private_channel"})))
    elif args.action == "send":
        print(json.dumps(hub.send(args.target, args.message)))
    elif args.action == "search":
        print(json.dumps(hub.search(args.query)))
