#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

CONFIG_PATH = os.path.expanduser("~/.lightrag_config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"servers": {}, "default_server": None}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Query LightRAG API")
    subparsers = parser.add_subparsers(dest="command")

    # Config command
    config_parser = subparsers.add_parser("config", help="Configure servers")
    config_parser.add_argument("--alias", required=True)
    config_parser.add_argument("--url", required=True)
    config_parser.add_argument("--key")
    config_parser.add_argument("--mode", default="local", choices=["local", "global", "hybrid", "naive", "mix"])

    # Query command
    query_parser = subparsers.add_parser("query", help="Query a server")
    query_parser.add_argument("query_text")
    query_parser.add_argument("--alias")
    query_parser.add_argument("--mode", choices=["local", "global", "hybrid", "naive", "mix"])
    query_parser.add_argument("--only-context", action="store_true")

    args = parser.parse_args()

    config = load_config()

    if args.command == "config":
        config["servers"][args.alias] = {
            "url": args.url, 
            "api_key": args.key,
            "mode": args.mode
        }
        if not config.get("default_server"):
            config["default_server"] = args.alias
        save_config(config)
        print(f"Server '{args.alias}' configured (default mode: {args.mode}).")
        return

    if args.command == "query":
        alias = args.alias or config.get("default_server")
        if not alias or alias not in config["servers"]:
            print("Error: Server alias not found or not specified.")
            sys.exit(1)
        
        server = config["servers"][alias]
        url = f"{server['url'].rstrip('/')}/query"
        headers = {"Content-Type": "application/json"}
        if server.get("api_key"):
            headers["X-API-Key"] = server["api_key"]
        
        # Priority: args.mode -> server['mode'] -> 'local'
        mode = args.mode or server.get("mode", "local")
        
        payload = {
            "query": args.query_text,
            "mode": mode,
            "only_need_context": args.only_context
        }

        try:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"), 
                headers=headers, 
                method="POST"
            )
            with urllib.request.urlopen(req, context=ctx) as f:
                data = json.loads(f.read().decode("utf-8"))
            
            if args.only_context:
                print(data.get("context", "No context found."))
            else:
                print(data.get("response", "No response found."))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
