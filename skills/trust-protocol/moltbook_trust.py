#!/usr/bin/env python3
"""
Moltbook Trust Bridge — Links ATP trust scores to Moltbook identities.

Maps Moltbook usernames to skillsign fingerprints and ATP trust scores.
Enables trust-aware decisions about Moltbook content and skill recommendations.

Usage:
    python3 moltbook_trust.py link <moltbook_user> <fingerprint>
    python3 moltbook_trust.py lookup <moltbook_user>
    python3 moltbook_trust.py score <moltbook_user> [--domain <domain>]
    python3 moltbook_trust.py scan-post <post_id>
    python3 moltbook_trust.py leaderboard
"""

import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ATP_PY = os.path.join(SCRIPT_DIR, "atp.py")
BRIDGE_FILE = os.path.expanduser("~/.atp/moltbook_bridge.json")

def load_bridge():
    if os.path.exists(BRIDGE_FILE):
        with open(BRIDGE_FILE) as f:
            return json.load(f)
    return {"links": {}, "updated": None}

def save_bridge(data):
    os.makedirs(os.path.dirname(BRIDGE_FILE), exist_ok=True)
    data["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(BRIDGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def atp_cmd(args):
    """Run ATP command and return output."""
    import subprocess
    result = subprocess.run(
        f"python3 {ATP_PY} {args}",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

def cmd_link(username, fingerprint):
    """Link a Moltbook username to a skillsign fingerprint."""
    bridge = load_bridge()
    bridge["links"][username] = {
        "fingerprint": fingerprint,
        "linked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verified": False  # Set to True after challenge-response
    }
    save_bridge(bridge)
    print(f"✓ Linked {username} → {fingerprint}")
    print(f"  Run 'moltbook_trust.py verify {username}' to verify via challenge-response")

def cmd_lookup(username):
    """Look up a Moltbook user's trust info."""
    bridge = load_bridge()
    if username not in bridge["links"]:
        print(f"✗ No link found for {username}")
        print(f"  Run 'moltbook_trust.py link {username} <fingerprint>' to create one")
        return
    
    link = bridge["links"][username]
    print(f"Moltbook User: {username}")
    print(f"  Fingerprint: {link['fingerprint']}")
    print(f"  Linked: {link['linked_at']}")
    print(f"  Verified: {'✓' if link.get('verified') else '✗ (unverified)'}")
    
    # Get ATP trust score
    score_out = atp_cmd(f"trust score {username}")
    if score_out:
        print(f"  ATP Trust: {score_out}")

def cmd_score(username, domain=None):
    """Get trust score for a Moltbook user."""
    bridge = load_bridge()
    if username not in bridge["links"]:
        print(f"✗ Unknown user: {username}")
        return
    
    domain_flag = f" --domain {domain}" if domain else ""
    score_out = atp_cmd(f"trust score {username}{domain_flag}")
    if score_out:
        print(score_out)
    else:
        print(f"No ATP trust data for {username}")

def cmd_scan_post(post_id):
    """Analyze trust signals in a Moltbook post's author and commenters."""
    # Try to fetch post info via moltbook CLI
    try:
        import subprocess
        moltbook_py = os.path.expanduser("~/.openclaw/skills/moltbook/moltbook.py")
        result = subprocess.run(
            f"python3 {moltbook_py} post {post_id}",
            shell=True, capture_output=True, text=True, timeout=15
        )
        if result.stdout:
            post_data = json.loads(result.stdout)
            author = post_data.get("author", {}).get("name", "unknown")
            print(f"Post: {post_data.get('title', 'untitled')}")
            print(f"Author: {author}")
            
            bridge = load_bridge()
            if author in bridge["links"]:
                link = bridge["links"][author]
                verified = "✓ verified" if link.get("verified") else "✗ unverified"
                print(f"  Identity: {link['fingerprint']} ({verified})")
                score_out = atp_cmd(f"trust score {author}")
                print(f"  Trust: {score_out}")
            else:
                print(f"  Identity: ✗ No skillsign link")
                print(f"  Trust: Unknown — no ATP data")
    except Exception as e:
        print(f"Error scanning post: {e}")

def cmd_leaderboard():
    """Show Moltbook users ranked by ATP trust score."""
    bridge = load_bridge()
    if not bridge["links"]:
        print("No linked users yet.")
        return
    
    scores = []
    for username, link in bridge["links"].items():
        score_out = atp_cmd(f"trust score {username}")
        # Parse score from output
        score = 0.0
        for line in score_out.split('\n'):
            if 'effective' in line.lower() or 'score' in line.lower():
                try:
                    score = float(line.split(':')[-1].strip().split()[0])
                except (ValueError, IndexError):
                    pass
        scores.append((username, score, link.get("verified", False)))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    print("═══ Moltbook Trust Leaderboard ═══")
    for i, (user, score, verified) in enumerate(scores, 1):
        v = "✓" if verified else "?"
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"  {i}. {user:20s} [{bar}] {score:.2f} {v}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "link" and len(sys.argv) >= 4:
        cmd_link(sys.argv[2], sys.argv[3])
    elif cmd == "lookup" and len(sys.argv) >= 3:
        cmd_lookup(sys.argv[2])
    elif cmd == "score" and len(sys.argv) >= 3:
        domain = None
        if "--domain" in sys.argv:
            idx = sys.argv.index("--domain")
            domain = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        cmd_score(sys.argv[2], domain)
    elif cmd == "scan-post" and len(sys.argv) >= 3:
        cmd_scan_post(sys.argv[2])
    elif cmd == "leaderboard":
        cmd_leaderboard()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
