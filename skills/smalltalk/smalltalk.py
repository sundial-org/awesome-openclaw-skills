#!/usr/bin/env python3
"""
Smalltalk CLI for Clawdbot

Communicates with a Squeak/Cuis MCP server via stdio JSON-RPC.
Requires xvfb-run for headless operation on Linux servers.

Usage:
    smalltalk.py --check                    # Verify setup
    smalltalk.py evaluate "3 factorial"
    smalltalk.py browse OrderedCollection
    smalltalk.py method-source String asUppercase

Environment Variables:
    SQUEAK_VM_PATH      - Path to Squeak/Cuis VM executable
    SQUEAK_IMAGE_PATH   - Path to Smalltalk image with MCP server

Author: Adapted from ClaudeSmalltalk by John M McIntosh
"""

import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# Search paths for auto-detection
VM_SEARCH_PATTERNS = [
    "~/Squeak*/bin/squeak",
    "~/squeak/bin/squeak",
    "/usr/local/bin/squeak",
    "/usr/bin/squeak",
    "/opt/squeak/bin/squeak",
    "~/Cuis*/bin/squeak",
]

IMAGE_SEARCH_PATTERNS = [
    "~/ClaudeSqueak*.image",
    "~/squeak/ClaudeSqueak*.image",
    "~/ClaudeCuis*.image",
    "~/*Squeak*/*Claude*.image",
]


def find_file(patterns: list[str]) -> Optional[str]:
    """Find first matching file from glob patterns."""
    for pattern in patterns:
        expanded = os.path.expanduser(pattern)
        matches = glob.glob(expanded)
        if matches:
            return sorted(matches)[-1]  # Return newest/latest
    return None


def get_paths() -> Tuple[str, str]:
    """Get VM and image paths from env vars or auto-detect."""
    vm_path = os.environ.get("SQUEAK_VM_PATH")
    image_path = os.environ.get("SQUEAK_IMAGE_PATH")

    if not vm_path:
        vm_path = find_file(VM_SEARCH_PATTERNS)
    if not image_path:
        image_path = find_file(IMAGE_SEARCH_PATTERNS)

    return vm_path or "", image_path or ""


def check_setup() -> bool:
    """Verify all dependencies and paths are correct."""
    print("🔍 Checking Clawdbot Smalltalk setup...\n")
    all_ok = True

    # Check xvfb-run
    if shutil.which("xvfb-run"):
        print("✅ xvfb-run found")
    else:
        print("❌ xvfb-run not found - install with: sudo apt install xvfb")
        all_ok = False

    # Check paths
    vm_path, image_path = get_paths()

    if vm_path and os.path.exists(vm_path):
        print(f"✅ VM found: {vm_path}")
    else:
        print(f"❌ VM not found")
        print(f"   Set SQUEAK_VM_PATH or install Squeak 6.0")
        print(f"   Download from: https://squeak.org/downloads/")
        all_ok = False

    if image_path and os.path.exists(image_path):
        print(f"✅ Image found: {image_path}")
    else:
        print(f"❌ Image not found")
        print(f"   Set SQUEAK_IMAGE_PATH or build per SQUEAK-SETUP.md")
        all_ok = False

    # Check sources file
    if image_path and os.path.exists(image_path):
        image_dir = os.path.dirname(image_path) or "."
        sources = glob.glob(os.path.join(image_dir, "*.sources"))
        if sources:
            print(f"✅ Sources file found: {sources[0]}")
        else:
            print(f"⚠️  No .sources file in image directory")
            print(f"   May cause dialog popups - symlink SqueakV60.sources to {image_dir}/")

    print()
    if all_ok:
        print("✅ Setup looks good!")
    else:
        print("❌ Setup incomplete - see errors above")

    return all_ok


class MCPClient:
    """Simple MCP client for Smalltalk interaction."""

    def __init__(self, vm_path: str, image_path: str):
        self.vm_path = vm_path
        self.image_path = image_path
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0

    def start(self) -> None:
        """Start the Smalltalk MCP server subprocess."""
        if self.process is not None:
            return

        # Use xvfb-run for headless operation
        cmd = ["xvfb-run", "-a", self.vm_path, self.image_path, "--mcp"]

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Initialize MCP connection
        self._initialize()

    def stop(self) -> None:
        """Stop the subprocess."""
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _send(self, method: str, params: Optional[dict] = None) -> dict:
        """Send JSON-RPC request and get response."""
        if self.process is None:
            raise RuntimeError("MCP server not started")

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            request["params"] = params

        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        # Read response, skipping non-JSON lines (stderr warnings etc)
        while True:
            response_line = self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from MCP server")
            response_line = response_line.strip()
            if response_line.startswith("{"):
                return json.loads(response_line)

    def _initialize(self) -> None:
        """Initialize the MCP connection."""
        response = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "clawdbot-smalltalk", "version": "1.0.0"}
        })

        if "error" in response:
            raise RuntimeError(f"MCP init failed: {response['error']}")

        # Send initialized notification
        self.process.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }) + "\n")
        self.process.stdin.flush()

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool and return the result."""
        response = self._send("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        if "error" in response:
            return f"Error: {response['error'].get('message', 'Unknown error')}"

        result = response.get("result", {})
        content = result.get("content", [])

        if content and isinstance(content, list):
            return content[0].get("text", str(result))
        return str(result)


def debug_squeak():
    """Start Squeak, send SIGUSR1, capture stack trace, screenshot, and generate HTML report."""
    import signal
    import time
    import platform
    import base64
    from datetime import datetime
    
    vm_path, image_path = get_paths()
    if not vm_path or not image_path:
        print("Error: VM or image not found. Run --check first.")
        return False
    
    print("🔍 Starting Squeak for debugging...")
    
    # Start Xvfb
    xvfb = subprocess.Popen(
        ["Xvfb", ":98", "-screen", "0", "1024x768x24"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    
    # Start Squeak
    env = os.environ.copy()
    env["DISPLAY"] = ":98"
    squeak = subprocess.Popen(
        [vm_path, image_path, "--mcp"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=env, text=True
    )
    
    print(f"⏳ Waiting for Squeak to start (PID {squeak.pid})...")
    time.sleep(5)
    
    # Capture screenshot on Linux
    screenshot_path = None
    screenshot_b64 = None
    if platform.system() == "Linux" and shutil.which("import"):
        screenshot_path = "/tmp/squeak_debug.png"
        subprocess.run(
            ["import", "-window", "root", "-display", ":98", screenshot_path],
            capture_output=True, timeout=10
        )
        if os.path.exists(screenshot_path):
            print(f"📸 Screenshot captured")
            with open(screenshot_path, 'rb') as f:
                screenshot_b64 = base64.b64encode(f.read()).decode()
        else:
            print("⚠️  Screenshot capture failed")
            screenshot_path = None
    
    print(f"📡 Sending SIGUSR1 to get stack trace...")
    squeak.send_signal(signal.SIGUSR1)
    time.sleep(2)
    
    # Kill and collect output
    squeak.terminate()
    try:
        output, _ = squeak.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        squeak.kill()
        output, _ = squeak.communicate()
    
    xvfb.terminate()
    
    # Filter out pthread warning boilerplate
    skip_patterns = [
        'pthread_setschedparam',
        'heartbeat thread',
        'higher priority',
        'security/limits',
        'squeak mailing',
        'log out and log',
        'opensmalltalk-vm',
        'cat <<END',
        'rtprio',
    ]
    
    lines = output.split('\n')
    filtered = []
    for line in lines:
        if not any(p in line for p in skip_patterns):
            filtered.append(line)
    
    trace_text = '\n'.join(filtered)
    
    # Generate timestamp and report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"/tmp/ClaudeSmalltalkDebug_{timestamp}.html"
    
    # Generate HTML report
    img_html = ""
    if screenshot_b64:
        img_html = f'<img src="data:image/png;base64,{screenshot_b64}" style="max-width:100%; border:1px solid #ccc;"/>'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<title>ClaudeSmalltalk Debug Report - {timestamp}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
h2 {{ color: #555; margin-top: 30px; }}
pre {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 11px; line-height: 1.4; }}
.timestamp {{ color: #888; font-size: 12px; }}
img {{ margin: 10px 0; }}
</style>
</head>
<body>
<div class="container">
<h1>🔧 ClaudeSmalltalk Debug Report</h1>
<p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

<h2>📸 Screenshot</h2>
{img_html if img_html else "<p>Screenshot not available</p>"}

<h2>📋 SIGUSR1 Stack Trace</h2>
<pre>{trace_text}</pre>
</div>
</body>
</html>'''
    
    with open(report_path, 'w') as f:
        f.write(html)
    
    print("\n📋 Full stack trace:")
    print(trace_text)
    
    print(f"\n📄 Report saved: {report_path}")
    
    return True


def print_usage():
    print("Usage: smalltalk.py <command> [args...]")
    print("\nCommands:")
    print("  --check                      - Verify setup")
    print("  --debug                      - Debug hung system (SIGUSR1 stack trace)")
    print("  evaluate <code>              - Evaluate Smalltalk code")
    print("  browse <className>           - Browse a class")
    print("  method-source <class> <sel>  - Get method source")
    print("  define-class <definition>    - Define a class")
    print("  define-method <class> <src>  - Define a method")
    print("  delete-method <class> <sel>  - Delete a method")
    print("  delete-class <className>     - Delete a class")
    print("  list-classes [prefix]        - List classes")
    print("  hierarchy <className>        - Get class hierarchy")
    print("  subclasses <className>       - Get subclasses")
    print("  list-categories              - List categories")
    print("  classes-in-category <cat>    - List classes in category")
    print("\nEnvironment:")
    print("  SQUEAK_VM_PATH     - Path to VM (auto-detected if not set)")
    print("  SQUEAK_IMAGE_PATH  - Path to image (auto-detected if not set)")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    # Handle --check separately
    if command in ("--check", "-c", "check"):
        success = check_setup()
        sys.exit(0 if success else 1)

    # Handle --debug
    if command in ("--debug", "-d", "debug"):
        success = debug_squeak()
        sys.exit(0 if success else 1)

    # Get paths
    vm_path, image_path = get_paths()

    if not vm_path or not os.path.exists(vm_path):
        print(f"Error: VM not found")
        print(f"Run 'smalltalk.py --check' for setup help")
        sys.exit(1)

    if not image_path or not os.path.exists(image_path):
        print(f"Error: Image not found")
        print(f"Run 'smalltalk.py --check' for setup help")
        sys.exit(1)

    client = MCPClient(vm_path, image_path)

    try:
        client.start()

        # Map commands to tool calls
        if command == "evaluate":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py evaluate <code>")
                sys.exit(1)
            code = " ".join(sys.argv[2:])
            result = client.call_tool("smalltalk_evaluate", {"code": code})

        elif command == "browse":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py browse <className>")
                sys.exit(1)
            result = client.call_tool("smalltalk_browse", {"className": sys.argv[2]})

        elif command == "method-source":
            if len(sys.argv) < 4:
                print("Usage: smalltalk.py method-source <className> <selector>")
                sys.exit(1)
            result = client.call_tool("smalltalk_method_source", {
                "className": sys.argv[2],
                "selector": sys.argv[3]
            })

        elif command == "define-class":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py define-class <definition>")
                sys.exit(1)
            result = client.call_tool("smalltalk_define_class", {
                "definition": " ".join(sys.argv[2:])
            })

        elif command == "define-method":
            if len(sys.argv) < 4:
                print("Usage: smalltalk.py define-method <className> <source>")
                sys.exit(1)
            result = client.call_tool("smalltalk_define_method", {
                "className": sys.argv[2],
                "source": " ".join(sys.argv[3:])
            })

        elif command == "delete-method":
            if len(sys.argv) < 4:
                print("Usage: smalltalk.py delete-method <className> <selector>")
                sys.exit(1)
            result = client.call_tool("smalltalk_delete_method", {
                "className": sys.argv[2],
                "selector": sys.argv[3]
            })

        elif command == "delete-class":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py delete-class <className>")
                sys.exit(1)
            result = client.call_tool("smalltalk_delete_class", {"className": sys.argv[2]})

        elif command == "list-classes":
            prefix = sys.argv[2] if len(sys.argv) > 2 else ""
            result = client.call_tool("smalltalk_list_classes", {"prefix": prefix})

        elif command == "hierarchy":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py hierarchy <className>")
                sys.exit(1)
            result = client.call_tool("smalltalk_hierarchy", {"className": sys.argv[2]})

        elif command == "subclasses":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py subclasses <className>")
                sys.exit(1)
            result = client.call_tool("smalltalk_subclasses", {"className": sys.argv[2]})

        elif command == "list-categories":
            result = client.call_tool("smalltalk_list_categories", {})

        elif command == "classes-in-category":
            if len(sys.argv) < 3:
                print("Usage: smalltalk.py classes-in-category <category>")
                sys.exit(1)
            result = client.call_tool("smalltalk_classes_in_category", {
                "category": sys.argv[2]
            })

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

        print(result)

    finally:
        client.stop()


if __name__ == "__main__":
    main()
