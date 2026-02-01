---
name: desktop-mouse
description: Local mouse control via ydotool wrapper
metadata: {"moltbot":{"emoji":"","os":["linux"],"requires":{"bins":["molt-mouse"]}}}
user-invocable: false
---
When the user asks to move/click the mouse:
- Use the exec tool with host=gateway.
- ONLY run commands that start with: `molt-mouse ...`
- Supported:
  - `molt-mouse move <dx> <dy>`
  - `molt-mouse abs <x> <y>`
  - `molt-mouse click left|right|middle`
  - `molt-mouse click 0x40` # left button down (hold)
  - `molt-mouse click 0x80` # left button up (release)
- If numbers are missing/ambiguous, ask the user.

