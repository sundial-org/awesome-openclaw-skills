---
name: xcodebuildmcp
description: Use when the user needs Xcode build/test/run workflows, simulator or device control, UI automation, screenshots/video, logs, or LLDB debugging through XcodeBuildMCP tools. Includes discovery of projects/schemes, session defaults, and common simulator/device workflows.
---

# Xcodebuildmcp

## Overview

Use the xcodebuildmcp toolset to build/run/test apps, manage simulators/devices, automate UI, and capture logs/screen media. Default to a safe, repeatable flow: discover → set defaults → execute → verify.

## Prereqs & MCP Setup

This skill assumes the XcodeBuildMCP server is installed and exposed to your MCP client so the tools appear (e.g., `mcp__xcodebuildmcp__build_run_sim`). If the tools are missing, follow the setup steps in:

- `references/mcp-setup.md` (requirements + MCP client config examples)

## Example Requests

- "Build and run the iOS app on the latest simulator and take a screenshot."
- "Run unit tests on the simulator and share the failing test logs."
- "Open the simulator, navigate to Settings, and toggle Dark Mode."
- "Install and launch the app on my connected iPhone."

## Quick Start (common flow)

1) Discover the project/workspace and schemes:
   - `mcp__xcodebuildmcp__discover_projs`
   - `mcp__xcodebuildmcp__list_schemes`

2) Set session defaults (so subsequent tools don’t need repeated params):
   - `mcp__xcodebuildmcp__session-set-defaults` (workspacePath/projectPath, scheme, simulatorId/deviceId)

3) Run the task:
   - Build/run: `mcp__xcodebuildmcp__build_run_sim` or `mcp__xcodebuildmcp__build_run_macos`
   - Tests: `mcp__xcodebuildmcp__test_sim` / `mcp__xcodebuildmcp__test_macos` / `mcp__xcodebuildmcp__test_device`

4) Verify and gather evidence:
   - `mcp__xcodebuildmcp__screenshot` (sim)
   - `mcp__xcodebuildmcp__start_sim_log_cap` → `mcp__xcodebuildmcp__stop_sim_log_cap`

## Task Index

- **Build/Run**: iOS simulator, macOS, device installs
- **Testing**: simulator/macOS/device
- **Simulator management**: list/boot/erase/appearance/location/gestures
- **UI automation**: describe UI → tap/type/swipe/gesture
- **Logs & debugging**: sim logs, device logs, LLDB attach/breakpoints
- **Media**: screenshots, screen recording

Load `references/workflows.md` for detailed step-by-step sequences and command patterns.

## Operating Rules

- Always call `mcp__xcodebuildmcp__describe_ui` before coordinate-based taps/swipes/long-press.
- Prefer `mcp__xcodebuildmcp__session-set-defaults` early to reduce parameter noise.
- If user didn’t specify target device/simulator, list options and ask (or pick a sensible default with `useLatestOS`).
- Avoid destructive actions (erase sims, clean) unless the user asked for them.
