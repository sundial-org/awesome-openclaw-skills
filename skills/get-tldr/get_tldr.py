#!/usr/bin/env python3
"""
Call get-tldr.com summarize API with a single URL argument.
Usage: python3 get_tldr.py "https://example.com/..."
Prints the JSON response to stdout.
Reads api_token and optional logfile from ~/.config/get-tldr/config.json (preferred), falling back to GET_TLDR_API_KEY or a .env file in the skill folder. If no logfile is configured the script defaults to ~/.config/get-tldr/skill.log.
This script is used by the get-tldr skill.
"""
import sys
import json
import os
from urllib.parse import urlparse
from datetime import datetime

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests library required. Install with: pip install requests"}))
    sys.exit(1)

API_URL = "https://www.get-tldr.com/api/v1/summarize"
# Read API key and optional logfile from ~/.config/get-tldr/config.json (preferred),
# falling back to the GET_TLDR_API_KEY environment variable or a .env file in this folder.
API_KEY = None
LOGFILE = os.path.expanduser("~/.config/get-tldr/skill.log")
config_path = os.path.expanduser("~/.config/get-tldr/config.json")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
        API_KEY = cfg.get("api_token")
        # if logfile is configured in the config, expand and use it
        if cfg.get("logfile") or cfg.get("log_file"):
            LOGFILE = os.path.expanduser(cfg.get("logfile") or cfg.get("log_file"))
except FileNotFoundError:
    pass
except Exception:
    # ignore parse errors and continue to other fallbacks
    pass

# fallback to environment variable
if not API_KEY:
    API_KEY = os.environ.get("GET_TLDR_API_KEY")

# fallback to .env file located in the same folder as this script
if not API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "GET_TLDR_API_KEY":
                    API_KEY = v.strip().strip('"').strip("'")
                    break
    except FileNotFoundError:
        pass

if not API_KEY:
    print(json.dumps({"error": "Missing API key. Create ~/.config/get-tldr/config.json with api_token, or set GET_TLDR_API_KEY env var or place it in this skill folder's .env."}))
    sys.exit(1)


def summarize(url: str):
    payload = {"input": url}
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    try:
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError:
        try:
            return {"status_code": resp.status_code, "error": resp.json()}
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text}
    except Exception:
        try:
            return resp.json()
        except Exception:
            return {"status_code": getattr(resp, 'status_code', None), "text": getattr(resp, 'text', str(resp))}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing URL argument"}))
        sys.exit(2)
    url = sys.argv[1]
    # basic URL validation
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        print(json.dumps({"error": "Invalid URL scheme; must start with http:// or https://", "url": url}))
        sys.exit(2)
    result = summarize(url)
    # append a log entry: timestamp, sent payload and response payload (ignore errors)
    try:
        sent_payload = {"input": url}
        with open(LOGFILE, "a", encoding="utf-8") as lf:
            lf.write(json.dumps({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "sent": sent_payload,
                "response": result
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass
    print(json.dumps(result, ensure_ascii=False, indent=2))
