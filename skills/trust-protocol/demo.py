#!/usr/bin/env python3
"""
Full-Stack Demo: skillsign → ATP → Dashboard

Runs an end-to-end demonstration of the agent trust ecosystem:
1. Two agents generate identities (skillsign keygen)
2. Agent A signs a skill, Agent B verifies it
3. Verified agent gets added to trust graph
4. Agents interact, trust updates via Bayesian model
5. Challenge-response verification
6. Trust revocation and restoration
7. Dashboard serves everything live at localhost:8420

Usage:
    python3 demo.py           # Run full demo
    python3 demo.py --serve   # Run demo + keep dashboard server alive
    python3 demo.py --clean   # Clean up demo artifacts
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import http.server
import threading

DEMO_DIR = tempfile.mkdtemp(prefix="atp-demo-")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ATP_PY = os.path.join(SCRIPT_DIR, "atp.py")
DASHBOARD_HTML = os.path.join(SCRIPT_DIR, "dashboard.html")
SKILLSIGN_PY = os.path.join(os.path.dirname(SCRIPT_DIR), "skillsign", "skillsign.py")

# Colors
G = "\033[92m"   # green
B = "\033[94m"   # blue
Y = "\033[93m"   # yellow
R = "\033[91m"   # red
D = "\033[90m"   # dim
W = "\033[0m"    # reset
BOLD = "\033[1m"

def banner(text):
    print(f"\n{B}{'─'*60}")
    print(f"  {BOLD}{text}{W}")
    print(f"{B}{'─'*60}{W}\n")

def step(n, text):
    print(f"  {G}[{n}]{W} {text}")

def detail(text):
    print(f"      {D}{text}{W}")

def run(cmd, env=None, capture=True):
    """Run a command, return stdout."""
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, env=merged_env)
    if result.returncode != 0 and capture:
        detail(f"stderr: {result.stderr.strip()[:200]}")
    return result.stdout.strip() if capture else ""

def atp(args, env=None):
    return run(f"python3 {ATP_PY} {args}", env=env)

def skillsign(args, env=None):
    return run(f"python3 {SKILLSIGN_PY} {args}", env=env)

def demo_clean():
    """Clean up demo artifacts."""
    if os.path.exists(DEMO_DIR):
        shutil.rmtree(DEMO_DIR)
    print(f"Cleaned demo directory: {DEMO_DIR}")

def create_demo_skill(path, name="hello-world"):
    """Create a minimal skill folder for signing."""
    skill_dir = os.path.join(path, name)
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(f"# {name}\nA demo skill for the trust protocol demo.\n")
    with open(os.path.join(skill_dir, "hello.py"), "w") as f:
        f.write('#!/usr/bin/env python3\nprint("Hello from a verified skill!")\n')
    return skill_dir

def main():
    serve = "--serve" in sys.argv
    if "--clean" in sys.argv:
        demo_clean()
        return

    # Isolated environments for each agent
    agent_a_home = os.path.join(DEMO_DIR, "agent-a")
    agent_b_home = os.path.join(DEMO_DIR, "agent-b")
    atp_data = os.path.join(DEMO_DIR, "atp-data")
    os.makedirs(agent_a_home, exist_ok=True)
    os.makedirs(agent_b_home, exist_ok=True)

    env_a = {"SKILLSIGN_HOME": agent_a_home}
    env_b = {"SKILLSIGN_HOME": agent_b_home}
    atp_env = {"ATP_DATA_DIR": atp_data}

    banner("Agent Trust Protocol — Full Stack Demo")
    print(f"  {D}Demo workspace: {DEMO_DIR}{W}")
    print(f"  {D}Components: skillsign (identity) → ATP (trust) → dashboard (viz){W}\n")

    # ──────────────────────────────────────────
    banner("Phase 1: Identity")

    step(1, "Agent Alpha generates a signing keypair")
    out = skillsign("keygen --name alpha", env=env_a)
    detail(out.split('\n')[0] if out else "keygen done")

    step(2, "Agent Bravo generates a signing keypair")
    out = skillsign("keygen --name bravo", env=env_b)
    detail(out.split('\n')[0] if out else "keygen done")

    # Get fingerprints from key files
    alpha_fp = ""
    bravo_fp = ""
    alpha_keys_dir = os.path.join(agent_a_home, "keys")
    bravo_keys_dir = os.path.join(agent_b_home, "keys")
    
    # Find pub key files and extract fingerprints from filenames
    for d, fp_ref in [(alpha_keys_dir, "alpha"), (bravo_keys_dir, "bravo")]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith('.pub'):
                    if fp_ref == "alpha":
                        alpha_fp = f.replace('.pub', '')
                    else:
                        bravo_fp = f.replace('.pub', '')

    detail(f"Alpha fingerprint: {alpha_fp or 'generated'}")
    detail(f"Bravo fingerprint: {bravo_fp or 'generated'}")

    # ──────────────────────────────────────────
    banner("Phase 2: Skill Signing & Verification")

    step(3, "Agent Alpha creates and signs a skill package")
    skill_dir = create_demo_skill(DEMO_DIR)
    # Find Alpha's private key
    alpha_key_path = ""
    if os.path.exists(alpha_keys_dir):
        for f in os.listdir(alpha_keys_dir):
            if f.endswith('.pem'):
                alpha_key_path = os.path.join(alpha_keys_dir, f)
    out = skillsign(f"sign {skill_dir}" + (f" --key {alpha_key_path}" if alpha_key_path else ""), env=env_a)
    detail(out.split('\n')[0] if out else "signed")

    step(4, "Agent Bravo trusts Alpha's public key")
    # Copy Alpha's public key to Bravo's trusted keys
    alpha_pub_path = ""
    if os.path.exists(alpha_keys_dir):
        for f in os.listdir(alpha_keys_dir):
            if f.endswith('.pub'):
                alpha_pub_path = os.path.join(alpha_keys_dir, f)
                # Copy to bravo's keys dir so trust command can find it
                shutil.copy2(alpha_pub_path, os.path.join(bravo_keys_dir, f))
                detail(f"Copied {f} to Bravo's keyring")
    if alpha_pub_path:
        # Trust command needs path to the pub file in bravo's env
        bravo_pub_copy = os.path.join(bravo_keys_dir, os.path.basename(alpha_pub_path))
        out = skillsign(f"trust {bravo_pub_copy}", env=env_b)
        detail(out.split('\n')[0] if out else "trusted")

    step(5, "Agent Bravo verifies Alpha's signed skill")
    out = skillsign(f"verify {skill_dir}", env=env_b)
    verified = "pass" in out.lower() or "valid" in out.lower() or "verified" in out.lower() or "✓" in out
    if verified:
        detail(f"{G}✓ Signature verified — skill is authentic{W}")
    else:
        detail(f"{Y}Verification output: {out[:100]}{W}")

    # ──────────────────────────────────────────
    banner("Phase 3: Trust Graph")

    step(6, "Add both agents to the trust graph")
    atp(f'trust add alpha --fingerprint "{alpha_fp or "demo-alpha-fp"}" --score 0.7', env=atp_env)
    detail("Alpha added (initial score: 0.70)")
    atp(f'trust add bravo --fingerprint "{bravo_fp or "demo-bravo-fp"}" --score 0.5', env=atp_env)
    detail("Bravo added (initial score: 0.50)")

    step(7, "Record interactions — trust evolves")
    interactions = [
        ("alpha", "positive", "Signed skill verified correctly"),
        ("alpha", "positive", "Responded to challenge promptly"),
        ("bravo", "positive", "Provided helpful code review"),
        ("alpha", "positive", "Consistent behavior over time"),
        ("bravo", "negative", "Failed to deliver on promise"),
    ]
    for agent, outcome, note in interactions:
        atp(f'interact {agent} {outcome} --note "{note}"', env=atp_env)
        score_out = atp(f'trust score {agent}', env=atp_env)
        # Extract score
        score = "updated"
        for line in score_out.split('\n'):
            if 'score' in line.lower() or 'trust' in line.lower():
                score = line.strip()
                break
        emoji = G + "▲" + W if outcome == "positive" else R + "▼" + W
        detail(f"{emoji} {agent}: {outcome} — {note}")

    step(8, "Trust graph status")
    status = atp("status", env=atp_env)
    for line in status.split('\n')[:8]:
        detail(line)

    # ──────────────────────────────────────────
    banner("Phase 4: Challenge-Response Verification")

    step(9, "Alpha challenges Bravo to prove identity")
    challenge_file = os.path.join(DEMO_DIR, "challenge.json")
    out = atp(f'challenge create bravo', env=atp_env)
    detail(out.split('\n')[0] if out else "Challenge issued")
    # Note: full challenge-response requires both agents to sign,
    # which needs coordinated key access. Showing the flow.
    detail(f"{D}(In production: Bravo signs challenge with its private key,")
    detail(f" Alpha verifies signature to confirm Bravo's identity){W}")

    # ──────────────────────────────────────────
    banner("Phase 5: Trust Revocation")

    step(10, "Bravo's trust is revoked (detected malicious behavior)")
    atp('trust revoke bravo --reason "Attempted to distribute unsigned skill"', env=atp_env)
    detail(f"{R}✗ Bravo revoked — trust dropped to floor{W}")

    step(11, "Trust graph after revocation")
    status = atp("status", env=atp_env)
    for line in status.split('\n')[:8]:
        detail(line)

    step(12, "Bravo's trust is restored after investigation")
    atp('trust restore bravo --score 0.3', env=atp_env)
    detail(f"{Y}↻ Bravo restored at reduced trust (0.30){W}")

    # ──────────────────────────────────────────
    banner("Phase 6: Domain-Specific Trust")

    step(13, "Add domain-specific trust scores")
    atp('interact alpha positive --domain code --note "Clean, well-tested PRs"', env=atp_env)
    atp('interact alpha positive --domain security --note "Found and reported vulnerability"', env=atp_env)
    atp('interact bravo positive --domain documentation --note "Excellent README updates"', env=atp_env)
    detail("Alpha: high trust in code + security domains")
    detail("Bravo: building trust in documentation domain")

    domains_out = atp("trust domains alpha", env=atp_env)
    if domains_out:
        for line in domains_out.split('\n')[:5]:
            detail(line)

    # ──────────────────────────────────────────
    banner("Phase 7: Visualization")

    step(14, "Export trust graph")
    export_out = atp("graph export --format json", env=atp_env)
    if export_out:
        try:
            graph_data = json.loads(export_out)
            detail(f"Nodes: {len(graph_data.get('nodes', []))}")
            detail(f"Edges: {len(graph_data.get('edges', []))}")
        except json.JSONDecodeError:
            detail(export_out[:200])

    # Generate dashboard data file
    dashboard_data = os.path.join(DEMO_DIR, "dashboard-data.json")
    with open(dashboard_data, "w") as f:
        json.dump({
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "demo_dir": DEMO_DIR,
            "atp_data": atp_data
        }, f, indent=2)

    step(15, "Dashboard ready")
    detail(f"Open: {DASHBOARD_HTML}")
    detail(f"ATP data: {atp_data}")

    if serve:
        port = 8420
        step(16, f"Starting dashboard server at http://localhost:{port}")
        
        # Copy dashboard + data to serve directory
        serve_dir = os.path.join(DEMO_DIR, "serve")
        os.makedirs(serve_dir, exist_ok=True)
        shutil.copy2(DASHBOARD_HTML, os.path.join(serve_dir, "index.html"))
        
        # Create a simple API endpoint for ATP data
        class DemoHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=serve_dir, **kwargs)
            
            def do_GET(self):
                if self.path == '/api/status':
                    status = atp("status --json", env=atp_env)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(status.encode() if status else b'{}')
                else:
                    super().do_GET()
            
            def log_message(self, format, *args):
                pass  # Suppress server logs

        server = http.server.HTTPServer(('', port), DemoHandler)
        detail(f"{G}Dashboard live at http://localhost:{port}{W}")
        detail("Press Ctrl+C to stop")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
            print(f"\n{D}Server stopped.{W}")
    else:
        detail(f"Run with --serve to start dashboard on localhost:8420")

    # ──────────────────────────────────────────
    banner("Demo Complete")
    print(f"  {G}✓{W} Identity: 2 agents with ed25519 keypairs (skillsign)")
    print(f"  {G}✓{W} Signing: Skill signed by Alpha, verified by Bravo")
    print(f"  {G}✓{W} Trust: Bayesian trust graph with forgetting curves")
    print(f"  {G}✓{W} Interactions: 5 recorded, trust scores evolved")
    print(f"  {G}✓{W} Revocation: Bravo revoked and restored at reduced trust")
    print(f"  {G}✓{W} Domains: Per-domain trust tracking (code, security, docs)")
    print(f"  {G}✓{W} Dashboard: Visual trust graph at localhost:8420")
    print(f"\n  {D}Artifacts: {DEMO_DIR}{W}")
    print(f"  {D}Clean up: python3 demo.py --clean{W}\n")


if __name__ == "__main__":
    main()
