---
name: swiftui-empty-app-init
description: Initialize a minimal SwiftUI iOS app in the current directory by generating a single `.xcodeproj` with XcodeGen (no workspaces, packages, or tests unless explicitly requested).
---

# SwiftUI Empty App Init

## Overview
Initialize a clean, single-target SwiftUI iOS app in the current directory.
The project is generated using **XcodeGen** to produce a single `.xcodeproj`, leaving developers ready to start adding features immediately.

## Prerequisites
- Xcode installed and selected via `xcode-select`
- **XcodeGen** available on `PATH`

If any prerequisite is missing:
- Stop execution
- Tell the user exactly what is missing
- Do **not** attempt alternative scaffolding or auto-installation

## Inputs
- **Project name** (required)
- **Minimum iOS deployment target**
- **Optional bundle identifier** (or use default)

## Defaults (use without extra confirmation)
- Bundle identifier default: `com.example.<ProjectName>`
- Proceed immediately once required inputs are provided (do not ask extra confirmations)

## Core Requirements
The resulting project must:
- Be generated via **XcodeGen** (do not hand-author `project.pbxproj`)
- Use a single `.xcodeproj` (no `.xcworkspace`)
- Contain exactly one **app target**
- Use the SwiftUI `@main App` lifecycle
- Contain a minimal `ContentView` placeholder
- Contain a minimal `Info.plist` (avoid unnecessary scene or delegate keys)
- Contain **no Swift packages**
- Contain **no test targets** unless explicitly requested

## Generation
- Create a minimal `project.yml` using the provided inputs
- Generate `YourApp.xcodeproj` using XcodeGen
- Ensure the output matches all Core Requirements

## Expected Structure
- `project.yml`
- `YourApp.xcodeproj`
- `YourApp/` (app target source files)
- Optional config files only

No additional folders, packages, workspaces, scripts, or assets should be present.

## Minimal Verification (fast)
- Confirm `YourApp.xcodeproj` is generated successfully by XcodeGen.
- Confirm the default scheme exists (e.g., via a lightweight scheme listing).
- Do **not** boot simulators, build, install, or launch unless explicitly requested.

## Notes
- Keep the project minimal and unopinionated
- Do not add icons/scripts, packages, workspaces, or architecture scaffolding
- This skill is for **app initialization only**, not feature scaffolding
