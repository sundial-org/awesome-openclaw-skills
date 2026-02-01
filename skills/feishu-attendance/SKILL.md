---
name: feishu-attendance
description: Monitor Feishu (Lark) attendance records. Check for late, early leave, or absent employees and report to admin.
tags: [feishu, lark, attendance, monitor, report]
---

# Feishu Attendance Skill

Monitor daily attendance, notify employees of abnormalities, and report summary to admin.

## Usage

Check today's attendance:
```bash
node index.js check
```

Check specific date:
```bash
node index.js check --date 2023-10-27
```

## Permissions Required
- `attendance:report:readonly`
- `contact:user.employee:readonly`
- `im:message:send_as_bot`
