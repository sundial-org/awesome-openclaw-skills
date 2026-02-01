#!/usr/bin/env python3
"""
Komodo CLI - interact with Komodo Core API.

Environment variables:
  KOMODO_ADDRESS    - Komodo Core URL (e.g., https://komodo.example.com)
  KOMODO_API_KEY    - API key (starts with K-)
  KOMODO_API_SECRET - API secret (starts with S-)

Usage:
  python komodo.py <command> [args...]

Commands:
  # Read operations
  servers              - List all servers with status
  deployments          - List all deployments
  stacks               - List all stacks
  builds               - List all builds
  procedures           - List all procedures
  repos                - List all repos
  
  # Server details
  server <name>        - Get server details and stats
  server-stats <name>  - Get server CPU/memory/disk stats
  
  # Deployment operations
  deployment <name>    - Get deployment details
  deploy <name>        - Deploy/redeploy a deployment
  start <name>         - Start a deployment
  stop <name>          - Stop a deployment
  restart <name>       - Restart a deployment
  logs <name> [lines]  - Get container logs (default 100 lines)
  
  # Stack operations
  stack <name>         - Get stack details
  deploy-stack <name>  - Deploy a stack
  start-stack <name>   - Start a stack
  stop-stack <name>    - Stop a stack
  restart-stack <name> - Restart a stack
  
  # Build operations
  build <name>         - Get build details
  run-build <name>     - Run a build
  
  # Procedure operations
  procedure <name>     - Get procedure details
  run-procedure <name> - Run a procedure
  
  # Create operations
  create-stack <name> <server> <compose_file> [env_file]
                       - Create a new stack from compose file
"""

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

KOMODO_ADDRESS = os.environ.get("KOMODO_ADDRESS", "").rstrip("/")
KOMODO_API_KEY = os.environ.get("KOMODO_API_KEY", "")
KOMODO_API_SECRET = os.environ.get("KOMODO_API_SECRET", "")


def api_call(endpoint: str, payload: dict | None = None, method: str = "POST") -> Any:
    """Make an API call to Komodo Core."""
    if not KOMODO_ADDRESS:
        print("Error: KOMODO_ADDRESS not set", file=sys.stderr)
        sys.exit(1)
    if not KOMODO_API_KEY or not KOMODO_API_SECRET:
        print("Error: KOMODO_API_KEY or KOMODO_API_SECRET not set", file=sys.stderr)
        sys.exit(1)

    url = f"{KOMODO_ADDRESS}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": KOMODO_API_KEY,
        "X-Api-Secret": KOMODO_API_SECRET,
    }
    
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def read(request_type: str, payload: dict | None = None) -> Any:
    """Read operation."""
    return api_call(f"read/{request_type}", payload)


def execute(request_type: str, payload: dict | None = None) -> Any:
    """Execute operation."""
    return api_call(f"execute/{request_type}", payload)


def format_state(state: str) -> str:
    """Format state with emoji."""
    states = {
        "Ok": "🟢",
        "Running": "🟢",
        "Stopped": "🔴",
        "NotDeployed": "⚪",
        "Unknown": "❓",
        "Unhealthy": "🟡",
        "Restarting": "🔄",
        "Building": "🔨",
        "Pending": "⏳",
    }
    emoji = states.get(state, "❓")
    return f"{emoji} {state}"


def cmd_servers():
    """List all servers."""
    servers = read("ListServers")
    if not servers:
        print("No servers found.")
        return
    
    print("=== Servers ===\n")
    for s in servers:
        info = s.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        version = info.get("version", "?")
        print(f"{state} {s['name']}")
        print(f"   Version: {version}")
        print(f"   Address: {info.get('address', 'N/A')}")
        print()


def cmd_server(name: str):
    """Get server details."""
    servers = read("ListServers")
    server = next((s for s in servers if s["name"].lower() == name.lower()), None)
    if not server:
        print(f"Server '{name}' not found.")
        return
    
    info = server.get("info", {})
    print(f"=== Server: {server['name']} ===\n")
    print(f"ID: {server['id']}")
    print(f"State: {format_state(info.get('state', 'Unknown'))}")
    print(f"Version: {info.get('version', 'N/A')}")
    print(f"Address: {info.get('address', 'N/A')}")
    print(f"External: {info.get('external_address', 'N/A')}")
    print(f"Region: {info.get('region', 'N/A')}")


def cmd_server_stats(name: str):
    """Get server stats."""
    stats = read("GetSystemStats", {"server": name})
    if not stats:
        print(f"No stats for server '{name}'.")
        return
    
    print(f"=== Server Stats: {name} ===\n")
    
    # CPU
    cpu = stats.get("cpu", {})
    cpu_usage = cpu.get("usage", 0)
    print(f"CPU: {cpu_usage:.1f}%")
    
    # Memory
    mem = stats.get("memory", {})
    mem_used = mem.get("used_gb", 0)
    mem_total = mem.get("total_gb", 0)
    mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
    print(f"Memory: {mem_used:.1f} / {mem_total:.1f} GB ({mem_pct:.1f}%)")
    
    # Disks
    disks = stats.get("disks", [])
    for disk in disks:
        mount = disk.get("mount", "?")
        used = disk.get("used_gb", 0)
        total = disk.get("total_gb", 0)
        pct = (used / total * 100) if total > 0 else 0
        print(f"Disk {mount}: {used:.1f} / {total:.1f} GB ({pct:.1f}%)")


def cmd_deployments():
    """List all deployments."""
    deployments = read("ListDeployments")
    if not deployments:
        print("No deployments found.")
        return
    
    print("=== Deployments ===\n")
    for d in deployments:
        info = d.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        image = info.get("image", "N/A")
        server = info.get("server_name", "N/A")
        print(f"{state} {d['name']}")
        print(f"   Image: {image}")
        print(f"   Server: {server}")
        print()


def cmd_deployment(name: str):
    """Get deployment details."""
    deployments = read("ListDeployments")
    dep = next((d for d in deployments if d["name"].lower() == name.lower()), None)
    if not dep:
        print(f"Deployment '{name}' not found.")
        return
    
    info = dep.get("info", {})
    print(f"=== Deployment: {dep['name']} ===\n")
    print(f"ID: {dep['id']}")
    print(f"State: {format_state(info.get('state', 'Unknown'))}")
    print(f"Image: {info.get('image', 'N/A')}")
    print(f"Server: {info.get('server_name', 'N/A')}")


def cmd_deploy(name: str):
    """Deploy a deployment."""
    result = execute("Deploy", {"deployment": name})
    print(f"Deploy '{name}': {result}")


def cmd_start(name: str):
    """Start a deployment."""
    result = execute("StartDeployment", {"deployment": name})
    print(f"Start '{name}': {result}")


def cmd_stop(name: str):
    """Stop a deployment."""
    result = execute("StopDeployment", {"deployment": name})
    print(f"Stop '{name}': {result}")


def cmd_restart(name: str):
    """Restart a deployment."""
    result = execute("RestartDeployment", {"deployment": name})
    print(f"Restart '{name}': {result}")


def cmd_logs(name: str, lines: int = 100):
    """Get container logs."""
    result = read("GetLog", {"deployment": name, "tail": lines})
    if isinstance(result, dict) and "log" in result:
        print(result["log"])
    else:
        print(result)


def cmd_stacks():
    """List all stacks."""
    stacks = read("ListStacks")
    if not stacks:
        print("No stacks found.")
        return
    
    print("=== Stacks ===\n")
    for s in stacks:
        info = s.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        server = info.get("server_name", "N/A")
        print(f"{state} {s['name']}")
        print(f"   Server: {server}")
        print()


def cmd_stack(name: str):
    """Get stack details."""
    stacks = read("ListStacks")
    stack = next((s for s in stacks if s["name"].lower() == name.lower()), None)
    if not stack:
        print(f"Stack '{name}' not found.")
        return
    
    info = stack.get("info", {})
    print(f"=== Stack: {stack['name']} ===\n")
    print(f"ID: {stack['id']}")
    print(f"State: {format_state(info.get('state', 'Unknown'))}")
    print(f"Server: {info.get('server_name', 'N/A')}")


def cmd_deploy_stack(name: str):
    """Deploy a stack."""
    result = execute("DeployStack", {"stack": name})
    print(f"Deploy stack '{name}': {result}")


def cmd_start_stack(name: str):
    """Start a stack."""
    result = execute("StartStack", {"stack": name})
    print(f"Start stack '{name}': {result}")


def cmd_stop_stack(name: str):
    """Stop a stack."""
    result = execute("StopStack", {"stack": name})
    print(f"Stop stack '{name}': {result}")


def cmd_restart_stack(name: str):
    """Restart a stack."""
    result = execute("RestartStack", {"stack": name})
    print(f"Restart stack '{name}': {result}")


def cmd_builds():
    """List all builds."""
    builds = read("ListBuilds")
    if not builds:
        print("No builds found.")
        return
    
    print("=== Builds ===\n")
    for b in builds:
        info = b.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        version = info.get("version", "N/A")
        print(f"{state} {b['name']}")
        print(f"   Version: {version}")
        print()


def cmd_build(name: str):
    """Get build details."""
    builds = read("ListBuilds")
    build = next((b for b in builds if b["name"].lower() == name.lower()), None)
    if not build:
        print(f"Build '{name}' not found.")
        return
    
    info = build.get("info", {})
    print(f"=== Build: {build['name']} ===\n")
    print(f"ID: {build['id']}")
    print(f"State: {format_state(info.get('state', 'Unknown'))}")
    print(f"Version: {info.get('version', 'N/A')}")


def cmd_run_build(name: str):
    """Run a build."""
    result = execute("RunBuild", {"build": name})
    print(f"Run build '{name}': {result}")


def cmd_procedures():
    """List all procedures."""
    procedures = read("ListProcedures")
    if not procedures:
        print("No procedures found.")
        return
    
    print("=== Procedures ===\n")
    for p in procedures:
        info = p.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        print(f"{state} {p['name']}")
        print()


def cmd_procedure(name: str):
    """Get procedure details."""
    procedures = read("ListProcedures")
    proc = next((p for p in procedures if p["name"].lower() == name.lower()), None)
    if not proc:
        print(f"Procedure '{name}' not found.")
        return
    
    print(f"=== Procedure: {proc['name']} ===\n")
    print(f"ID: {proc['id']}")


def cmd_run_procedure(name: str):
    """Run a procedure."""
    result = execute("RunProcedure", {"procedure": name})
    print(f"Run procedure '{name}': {result}")


def cmd_repos():
    """List all repos."""
    repos = read("ListRepos")
    if not repos:
        print("No repos found.")
        return
    
    print("=== Repos ===\n")
    for r in repos:
        info = r.get("info", {})
        state = format_state(info.get("state", "Unknown"))
        print(f"{state} {r['name']}")
        print()


def cmd_create_stack(name: str, server: str, compose_file: str, env_file: str | None = None):
    """Create a new stack from compose file."""
    # Read compose file
    try:
        with open(compose_file, "r") as f:
            compose_contents = f.read()
    except FileNotFoundError:
        print(f"Error: Compose file '{compose_file}' not found.")
        sys.exit(1)
    
    # Read env file if provided
    env_vars = {}
    if env_file:
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        env_vars[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Error: Env file '{env_file}' not found.")
            sys.exit(1)
    
    # First, create the stack
    create_payload = {
        "name": name,
        "config": {
            "server_id": server,
            "file_contents": compose_contents,
            "environment": "\n".join(f"{k}={v}" for k, v in env_vars.items()) if env_vars else "",
        }
    }
    
    result = api_call("write/CreateStack", create_payload)
    print(f"Created stack '{name}': {result.get('id', result)}")
    print(f"\nTo deploy, run: python komodo.py deploy-stack {name}")


def cmd_delete_stack(name: str):
    """Delete a stack."""
    result = execute("DeleteStack", {"stack": name})
    print(f"Delete stack '{name}': {result}")


def cmd_stack_logs(name: str, service: str | None = None):
    """Get stack service logs."""
    payload = {"stack": name}
    if service:
        payload["service"] = service
    result = read("GetStackServiceLog", payload)
    if isinstance(result, dict) and "log" in result:
        print(result["log"])
    else:
        print(result)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "servers": (cmd_servers, 0),
        "server": (cmd_server, 1),
        "server-stats": (cmd_server_stats, 1),
        "deployments": (cmd_deployments, 0),
        "deployment": (cmd_deployment, 1),
        "deploy": (cmd_deploy, 1),
        "start": (cmd_start, 1),
        "stop": (cmd_stop, 1),
        "restart": (cmd_restart, 1),
        "logs": (cmd_logs, 1),
        "stacks": (cmd_stacks, 0),
        "stack": (cmd_stack, 1),
        "deploy-stack": (cmd_deploy_stack, 1),
        "start-stack": (cmd_start_stack, 1),
        "stop-stack": (cmd_stop_stack, 1),
        "restart-stack": (cmd_restart_stack, 1),
        "create-stack": (cmd_create_stack, 3),
        "delete-stack": (cmd_delete_stack, 1),
        "stack-logs": (cmd_stack_logs, 1),
        "builds": (cmd_builds, 0),
        "build": (cmd_build, 1),
        "run-build": (cmd_run_build, 1),
        "procedures": (cmd_procedures, 0),
        "procedure": (cmd_procedure, 1),
        "run-procedure": (cmd_run_procedure, 1),
        "repos": (cmd_repos, 0),
    }
    
    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print("Run without arguments for help.")
        sys.exit(1)
    
    func, min_args = commands[cmd]
    if len(args) < min_args:
        print(f"Command '{cmd}' requires {min_args} argument(s).")
        sys.exit(1)
    
    if cmd == "logs" and len(args) >= 2:
        func(args[0], int(args[1]))
    elif cmd == "create-stack":
        # create-stack <name> <server> <compose_file> [env_file]
        env_file = args[3] if len(args) >= 4 else None
        func(args[0], args[1], args[2], env_file)
    elif cmd == "stack-logs" and len(args) >= 2:
        func(args[0], args[1])
    elif min_args > 0:
        func(args[0])
    else:
        func()


if __name__ == "__main__":
    main()
