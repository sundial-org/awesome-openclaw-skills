---
name: comfyui-runner
description: Start/stop/status for a ComfyUI instance.
metadata: {"clawdbot":{"emoji":"🧩","requires":{"bins":["node","curl"]},"entry":"bin/cli.js"}}
---

# comfyui-runner

## Purpose
Start, stop, and check the status of a local ComfyUI instance.

## Configuration
- `COMFYUI_HOST`: Host/IP of the ComfyUI server (default `192.168.179.111`).
- `COMFYUI_PORT`: Port of the ComfyUI server (default `28188`).
- `COMFYUI_USER`: Optional username for basic auth.
- `COMFYUI_PASS`: Optional password for basic auth.

These can be set via environment variables or a `.env` file in the skill directory.

## Usage
```json
{
  "action": "run" | "stop" | "status"
}
```

- `run`: Starts the ComfyUI server if not already running.
- `stop`: Stops the ComfyUI server.
- `status`: Returns whether the server is reachable.

## Example
```json
{"action": "status"}
```

## Notes
This skill assumes the ComfyUI binary is available in the system PATH or in the same directory as the skill. It uses `curl` to ping the `/health` endpoint.
