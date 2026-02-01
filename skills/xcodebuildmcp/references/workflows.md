# Xcodebuildmcp Workflows

Use these patterns when running Xcode builds/tests, simulator control, or UI automation.

## Discovery & Defaults

1) Find project/workspace:
   - `mcp__xcodebuildmcp__discover_projs` (scanPath + workspaceRoot)
2) List schemes:
   - `mcp__xcodebuildmcp__list_schemes`
3) Pick target sim/device:
   - `mcp__xcodebuildmcp__list_sims`
   - `mcp__xcodebuildmcp__list_devices`
4) Set defaults (do once per session):
   - `mcp__xcodebuildmcp__session-set-defaults`

## Build/Run (iOS Simulator)

1) Boot/open sim:
   - `mcp__xcodebuildmcp__open_sim`
   - `mcp__xcodebuildmcp__boot_sim`
2) Build + run:
   - `mcp__xcodebuildmcp__build_run_sim`
3) Screenshot for verification:
   - `mcp__xcodebuildmcp__screenshot`

## Build/Run (macOS)

1) Build:
   - `mcp__xcodebuildmcp__build_macos`
2) Run:
   - `mcp__xcodebuildmcp__build_run_macos`

## Build/Run (Device)

1) Build:
   - `mcp__xcodebuildmcp__build_device`
2) Install:
   - `mcp__xcodebuildmcp__install_app_device`
3) Launch:
   - `mcp__xcodebuildmcp__launch_app_device`

## Tests

- Simulator: `mcp__xcodebuildmcp__test_sim`
- macOS: `mcp__xcodebuildmcp__test_macos`
- Device: `mcp__xcodebuildmcp__test_device`

## UI Automation (Simulator)

1) Get coordinates:
   - `mcp__xcodebuildmcp__describe_ui`
2) Interact:
   - `mcp__xcodebuildmcp__tap`
   - `mcp__xcodebuildmcp__type_text`
   - `mcp__xcodebuildmcp__swipe`
   - `mcp__xcodebuildmcp__gesture`
   - `mcp__xcodebuildmcp__long_press`
3) Validate:
   - `mcp__xcodebuildmcp__screenshot`

## Logs & Debugging

- Start logs (sim): `mcp__xcodebuildmcp__start_sim_log_cap`
- Stop logs (sim): `mcp__xcodebuildmcp__stop_sim_log_cap`
- Attach LLDB (sim): `mcp__xcodebuildmcp__debug_attach_sim`
- Breakpoints: `mcp__xcodebuildmcp__debug_breakpoint_add` / `mcp__xcodebuildmcp__debug_breakpoint_remove`
- Continue/detach: `mcp__xcodebuildmcp__debug_continue` / `mcp__xcodebuildmcp__debug_detach`
- Run LLDB command: `mcp__xcodebuildmcp__debug_lldb_command`
- Stack/vars: `mcp__xcodebuildmcp__debug_stack` / `mcp__xcodebuildmcp__debug_variables`

## Simulator Controls

- Appearance: `mcp__xcodebuildmcp__set_sim_appearance`
- Location: `mcp__xcodebuildmcp__set_sim_location`
- Reset location: `mcp__xcodebuildmcp__reset_sim_location`
- Status bar: `mcp__xcodebuildmcp__sim_statusbar`
- Record video: `mcp__xcodebuildmcp__record_sim_video` (start/stop)

## Cleanup

- Stop sim app: `mcp__xcodebuildmcp__stop_app_sim`
- Stop device app: `mcp__xcodebuildmcp__stop_app_device`
- Stop macOS app: `mcp__xcodebuildmcp__stop_mac_app`
