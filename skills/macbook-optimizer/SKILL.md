---
name: macbook-optimizer
description: Complete MacBook optimization suite: monitoring, troubleshooting, cleanup, and performance tuning. Works on all Macs (Intel & Apple Silicon). No extra tools required.
homepage: https://github.com/T4btc/macbook-optimizer
metadata:
  {
    "openclaw":
      {
        "emoji": "💻",
        "os": ["darwin"],
        "requires": { "bins": ["system_profiler", "top", "ps", "df", "du"] },
      },
  }
---

# 💻 MacBook Optimizer

_Complete MacBook health & performance suite - No installation required_

A comprehensive, user-friendly skill for monitoring, optimizing, and troubleshooting MacBook performance. Works on **all Macs** (Intel & Apple Silicon) using built-in macOS tools. Unlike specialized tools, this provides actionable recommendations and automated fixes.

## Why This Skill is Better

✅ **No installation required** - Uses built-in macOS tools  
✅ **Works on all Macs** - Intel & Apple Silicon  
✅ **Actionable recommendations** - Not just metrics, but solutions  
✅ **Automated fixes** - Can clean up and optimize automatically  
✅ **User-friendly** - Plain language, not technical jargon  
✅ **Complete suite** - Monitoring + troubleshooting + optimization  
✅ **GUI-first** - Opens visual tools automatically for non-technical users  
✅ **Visual reports** - Charts, graphs, and emoji indicators for easy understanding  

## Capabilities

### 🔍 System Monitoring
- **CPU Analysis**: Real-time CPU usage, temperature (via `powermetrics`), load averages, per-process breakdown
- **Memory Health**: RAM usage, memory pressure, swap usage, identify memory leaks
- **Disk Intelligence**: Space analysis, find large files/folders, duplicate detection, cache locations
- **Battery Diagnostics**: Health percentage, cycle count, capacity, charging status, power consumption
- **Thermal Monitoring**: System temperature, thermal state, identify overheating causes
- **Network Activity**: Bandwidth usage, active connections, identify bandwidth hogs

### ⚡ Optimization Tools
- **Smart Cleanup**: Automatically find and remove caches, logs, temp files, downloads, duplicates
- **Process Management**: Identify resource hogs, suggest optimizations, safe process termination
- **Startup Optimization**: Manage login items, background apps, reduce boot time
- **Storage Optimization**: Find large files, suggest deletions, empty trash, clear caches
- **Performance Tuning**: System settings recommendations, disable unnecessary services

### 🛠 Troubleshooting
- **Slowdown Diagnosis**: Identify bottlenecks (CPU/memory/disk/network), root cause analysis
- **Overheating Solutions**: Find hot processes, suggest cooling strategies, thermal management
- **Memory Issues**: Detect leaks, suggest app restarts, memory optimization
- **Disk Problems**: Full disk analysis, permission issues, disk health checks
- **Battery Issues**: Health degradation, charging problems, power management

## Usage Examples

**Complete system check (with GUI):**
```
Run a full system health check, show me the results visually, and fix any issues
```

**Performance optimization (GUI mode):**
```
My MacBook is slow. Open Activity Monitor and show me what's using resources
```

**Overheating issue:**
```
My MacBook is overheating. Show me the hot processes in Activity Monitor
```

**Disk cleanup (visual):**
```
Show me my disk usage visually and clean up automatically
```

**Memory problems (GUI):**
```
My Mac is using too much memory. Open Activity Monitor and highlight the memory hogs
```

**Battery health (visual):**
```
Show me my battery health in System Settings and optimize power settings
```

**Startup optimization:**
```
What's slowing down my Mac startup? Show me login items in System Settings
```

**Find large files (visual):**
```
Find all files larger than 1GB, show them in Finder, and suggest what I can delete
```

**GUI-first requests:**
```
Show me everything in Activity Monitor
Open System Settings to battery settings
Show me disk usage in a visual way
```

## Advanced Commands Available

The agent intelligently uses these macOS tools:

**System Info:**
- `system_profiler` - Complete hardware/software information
- `sysctl` - System parameters and kernel settings
- `sw_vers` - macOS version information

**Process Monitoring:**
- `top` / `htop` - Real-time process monitoring
- `ps` - Process status and details
- `lsof` - List open files and network connections
- `launchctl list` - Background services and daemons

**Resource Monitoring:**
- `vm_stat` - Virtual memory statistics
- `iostat` - Disk I/O statistics
- `netstat` / `lsof -i` - Network connections
- `powermetrics` - CPU/GPU power and temperature (Apple Silicon)
- `pmset -g therm` - Thermal state (Intel Macs)

**Disk Management:**
- `df` - Disk space usage
- `du` - Directory size analysis
- `find` - Locate large files
- `mdutil` - Spotlight index management

**Power & Battery:**
- `pmset` - Power management settings
- `ioreg` - I/O registry (battery info)
- `system_profiler SPPowerDataType` - Battery details

**Cleanup:**
- `rm` - Safe file removal (with confirmation)
- `purge` - Memory purge
- Cache locations: `~/Library/Caches`, `/Library/Caches`, `/var/folders`

**GUI Tools (Visual Interface):**
- `open -a "Activity Monitor"` - Launch Activity Monitor (CPU, Memory, Energy, Disk, Network)
- `open -a "System Settings"` - Open System Settings (all system preferences)
- `open -a "System Settings" && open "x-apple.systempreferences:com.apple.preference.battery"` - Battery settings
- `open -a "System Settings" && open "x-apple.systempreferences:com.apple.preference.storage"` - Storage management
- `open -a "System Settings" && open "x-apple.systempreferences:com.apple.LoginItems-Settings.extension"` - Login items
- `open -a "Finder"` - Open Finder for file browsing
- `open ~/Library/Caches` - Open Caches folder in Finder
- `open ~/Downloads` - Open Downloads folder
- `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"` - Privacy settings
- `open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"` - Accessibility permissions

**Visual Reports:**
- Generate HTML reports with charts (CPU, Memory, Disk usage over time)
- Create visual summaries with emoji indicators (🟢 Good, 🟡 Warning, 🔴 Critical)
- Open relevant System Settings panels automatically based on findings

## 🎨 GUI-First Experience

**For users who prefer visual interfaces**, the agent can:

- 📊 **Open Activity Monitor** automatically when showing system stats
- ⚙️ **Navigate System Settings** to relevant panels (Battery, Storage, Privacy)
- 📁 **Open Finder** to specific folders (Caches, Downloads, Large files)
- 📈 **Generate visual reports** with charts and graphs (HTML format)
- 🎯 **Highlight issues** in GUI apps with clear indicators
- 🔍 **Show step-by-step** with screenshots or GUI navigation

**Example GUI Workflow:**
1. User: "My Mac is slow"
2. Agent opens Activity Monitor → highlights CPU/Memory hogs
3. Agent opens System Settings → shows relevant optimization settings
4. Agent provides visual summary with emoji status indicators

## Intelligent Automation

The agent can:
- ✅ **Automatically clean** safe caches and temp files (with user confirmation)
- ✅ **Suggest optimizations** based on system analysis
- ✅ **Provide step-by-step fixes** for common issues (with GUI navigation)
- ✅ **Monitor continuously** if requested (via cron jobs)
- ✅ **Generate visual reports** with charts, graphs, and actionable recommendations
- ✅ **Open GUI tools** automatically when showing system information

## Safety & Privacy

- 🔒 **Always asks before** deleting files or killing processes
- 🔒 **Protects system files** and critical processes
- 🔒 **Reviews before action** - shows what will be deleted
- 🔒 **No data collection** - everything runs locally
- 🔒 **Respects privacy** - never sends data externally

## Requirements

- ✅ **macOS only** (Intel & Apple Silicon)
- ✅ **No installation needed** - uses built-in tools
- ✅ **Optional**: `htop` for prettier process view (`brew install htop`)
- ✅ **Optional**: `mactop` for Apple Silicon detailed metrics (`brew install mactop`)

## How to Use GUI Tools

When the user asks for visual information or mentions they're not technical:

1. **Always open Activity Monitor** when showing CPU/Memory/Process info
2. **Navigate to relevant System Settings** panels automatically
3. **Open Finder** to specific folders when discussing files
4. **Generate visual summaries** with emoji indicators (🟢🟡🔴)
5. **Provide step-by-step GUI navigation** instructions

**GUI Navigation Commands:**
- CPU issues → Open Activity Monitor, sort by CPU
- Memory issues → Open Activity Monitor, sort by Memory
- Battery → Open System Settings → Battery
- Storage → Open System Settings → General → Storage
- Login items → Open System Settings → General → Login Items
- Large files → Open Finder, navigate to location, sort by size

## Comparison with Other Tools

| Feature | macbook-optimizer | mactop |
|---------|------------------|--------|
| Installation required | ❌ No | ✅ Yes (brew) |
| Works on Intel Macs | ✅ Yes | ❌ No (Apple Silicon only) |
| Actionable recommendations | ✅ Yes | ❌ No (metrics only) |
| Automated cleanup | ✅ Yes | ❌ No |
| Troubleshooting | ✅ Yes | ❌ No |
| User-friendly | ✅ Yes | ⚠️ Technical |
| Complete suite | ✅ Yes | ⚠️ Monitoring only |
| GUI-first experience | ✅ Yes | ❌ CLI only |
| Visual reports | ✅ Yes | ❌ Text only |