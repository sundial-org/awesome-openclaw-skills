---
name: comfyui-request
description: Send a workflow request to ComfyUI and return image results.
metadata: {"clawdbot":{"emoji":"🧩","requires":{"bins":["node","curl"]},"entry":"bin/cli.js"}}
---

# comfyui-request

## Purpose
Send a workflow request to a running ComfyUI instance and return the generated image URL or base64 data.

## Configuration
- `COMFYUI_HOST`: Host/IP of the ComfyUI server (default `192.168.179.111`).
- `COMFYUI_PORT`: Port of the ComfyUI server (default `28188`).
- `COMFYUI_USER`: Optional username for basic auth.
- `COMFYUI_PASS`: Optional password for basic auth.

These can be set via environment variables or a `.env` file in the skill directory.

## Usage
```json
{
  "action": "run",
  "workflow": { ... }   // JSON workflow object
}
```

The skill will POST to `http://{host}:{port}/run` and return the response JSON.

## Example
```json
{
  "action": "run",
  "workflow": {
    "nodes": [ ... ],
    "edges": [ ... ]
  }
}
```

## Notes
The skill expects the ComfyUI server to expose the `/run` endpoint and return a JSON object containing an `image` field with a URL or base64 string.
