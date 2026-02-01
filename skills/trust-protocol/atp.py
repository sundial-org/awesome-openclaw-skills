#!/usr/bin/env python3
"""
Agent Trust Protocol (ATP) — A trust graph for autonomous agents.

Uses skillsign keys for identity, memory_v2 forgetting curves for trust decay,
and a local graph database for relationship tracking.

Usage:
    python3 atp.py trust add <agent> --fingerprint <fp> [--domain <domain>] [--score <0-1>]
    python3 atp.py trust list
    python3 atp.py trust score <agent>
    python3 atp.py trust remove <agent>
    python3 atp.py trust revoke <agent> [--reason <reason>]
    python3 atp.py trust restore <agent> [--score <0-1>]
    python3 atp.py trust domains <agent>
    python3 atp.py interact <agent> <outcome> [--domain <domain>] [--note <note>]
    python3 atp.py graph show
    python3 atp.py graph path <from_agent> <to_agent>
    python3 atp.py graph export [--format json|dot]
    python3 atp.py challenge create <agent>
    python3 atp.py challenge respond <challenge_file>
    python3 atp.py challenge verify <response_file>
    python3 atp.py status
"""

import json
import os
import sys
import time
import math
import hashlib
import secrets
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────

ATP_DIR = Path.home() / ".atp"
TRUST_DB = ATP_DIR / "trust.json"
INTERACTIONS_DB = ATP_DIR / "interactions.jsonl"
CHALLENGES_DIR = ATP_DIR / "challenges"
SKILLSIGN_DIR = Path.home() / ".skillsign"

# Trust decay: trust_effective = trust_base * e^(-t/S)
# S = stability in hours. Higher = slower decay.
DEFAULT_STABILITY = 168  # 1 week base stability
POSITIVE_STABILITY_BOOST = 1.2  # multiply stability on positive interaction
NEGATIVE_STABILITY_PENALTY = 0.6  # multiply stability on negative interaction
TRUST_FLOOR = 0.1  # minimum trust score (never fully distrust)
TRUST_CEILING = 0.99  # maximum trust score
TRANSITIVE_DECAY = 0.5  # trust propagation factor (A trusts B at 0.8, B trusts C at 0.7 → A trusts C at 0.8*0.7*0.5 = 0.28)

# ── Storage ─────────────────────────────────────────────────────────────────

def ensure_dirs():
    ATP_DIR.mkdir(exist_ok=True)
    CHALLENGES_DIR.mkdir(exist_ok=True)

def load_trust_db():
    if TRUST_DB.exists():
        return json.loads(TRUST_DB.read_text())
    return {"agents": {}, "edges": [], "self": {"agent_id": None, "fingerprint": None}}

def save_trust_db(db):
    ensure_dirs()
    TRUST_DB.write_text(json.dumps(db, indent=2))

def append_interaction(record):
    ensure_dirs()
    with open(INTERACTIONS_DB, "a") as f:
        f.write(json.dumps(record) + "\n")

# ── Trust Math ──────────────────────────────────────────────────────────────

def effective_trust(agent_data, domain=None):
    """Calculate effective trust with forgetting curve decay.
    
    If domain is specified, returns domain-specific trust.
    Falls back to general trust if domain has no data.
    """
    # Check for revocation first
    if agent_data.get("revoked"):
        return TRUST_FLOOR
    
    # Domain-specific trust
    if domain and "domain_scores" in agent_data:
        domain_data = agent_data["domain_scores"].get(domain)
        if domain_data:
            base = domain_data.get("score", 0.5)
            stability = domain_data.get("stability", DEFAULT_STABILITY)
            last_ts = domain_data.get("last_interaction_ts", agent_data.get("last_interaction_ts", time.time()))
            hours_elapsed = (time.time() - last_ts) / 3600
            decay = math.exp(-hours_elapsed / stability)
            return max(TRUST_FLOOR, min(TRUST_CEILING, base * decay))
    
    base = agent_data.get("trust_score", 0.5)
    stability = agent_data.get("stability", DEFAULT_STABILITY)
    last_interaction = agent_data.get("last_interaction_ts", time.time())
    
    hours_elapsed = (time.time() - last_interaction) / 3600
    decay = math.exp(-hours_elapsed / stability)
    
    effective = base * decay
    return max(TRUST_FLOOR, min(TRUST_CEILING, effective))

def update_trust_after_interaction(agent_data, outcome, domain="general"):
    """Update trust score and stability after an interaction.
    
    Updates both global trust and domain-specific trust.
    """
    if agent_data.get("revoked"):
        print(f"  ⚠ Agent is revoked. Interaction recorded but trust stays at floor.")
        agent_data["interaction_count"] = agent_data.get("interaction_count", 0) + 1
        return agent_data
    
    current = agent_data.get("trust_score", 0.5)
    stability = agent_data.get("stability", DEFAULT_STABILITY)
    count = agent_data.get("interaction_count", 0)
    
    if outcome == "positive":
        delta = 0.1 / (1 + count * 0.1)
        agent_data["trust_score"] = min(TRUST_CEILING, current + delta)
        agent_data["stability"] = stability * POSITIVE_STABILITY_BOOST
    elif outcome == "negative":
        delta = 0.15 / (1 + count * 0.05)
        agent_data["trust_score"] = max(TRUST_FLOOR, current - delta)
        agent_data["stability"] = stability * NEGATIVE_STABILITY_PENALTY
    elif outcome == "neutral":
        agent_data["stability"] = stability * 1.05
    
    agent_data["interaction_count"] = count + 1
    agent_data["last_interaction_ts"] = time.time()
    agent_data["last_interaction"] = datetime.now(timezone.utc).isoformat()
    
    # Update domain-specific trust
    if domain != "general":
        if "domain_scores" not in agent_data:
            agent_data["domain_scores"] = {}
        ds = agent_data["domain_scores"].get(domain, {
            "score": 0.5, "stability": DEFAULT_STABILITY, "interactions": 0
        })
        d_count = ds.get("interactions", 0)
        if outcome == "positive":
            d_delta = 0.1 / (1 + d_count * 0.1)
            ds["score"] = min(TRUST_CEILING, ds.get("score", 0.5) + d_delta)
            ds["stability"] = ds.get("stability", DEFAULT_STABILITY) * POSITIVE_STABILITY_BOOST
        elif outcome == "negative":
            d_delta = 0.15 / (1 + d_count * 0.05)
            ds["score"] = max(TRUST_FLOOR, ds.get("score", 0.5) - d_delta)
            ds["stability"] = ds.get("stability", DEFAULT_STABILITY) * NEGATIVE_STABILITY_PENALTY
        elif outcome == "neutral":
            ds["stability"] = ds.get("stability", DEFAULT_STABILITY) * 1.05
        ds["interactions"] = d_count + 1
        ds["last_interaction_ts"] = time.time()
        agent_data["domain_scores"][domain] = ds
    
    return agent_data

def revoke_trust(db, agent_id, reason="manual"):
    """Actively revoke trust for an agent. Unlike decay, this is immediate and permanent until restored."""
    if agent_id not in db["agents"]:
        return False, f"Unknown agent: {agent_id}"
    
    agent_data = db["agents"][agent_id]
    agent_data["revoked"] = True
    agent_data["revoked_at"] = datetime.now(timezone.utc).isoformat()
    agent_data["revoked_reason"] = reason
    agent_data["trust_score_before_revocation"] = agent_data.get("trust_score", 0.5)
    agent_data["trust_score"] = TRUST_FLOOR
    
    # Remove all edges to this agent
    db["edges"] = [e for e in db["edges"] if e["to"] != agent_id]
    
    # Log revocation event
    append_interaction({
        "agent": agent_id,
        "outcome": "revocation",
        "reason": reason,
        "old_score": agent_data["trust_score_before_revocation"],
        "new_score": TRUST_FLOOR,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    save_trust_db(db)
    return True, f"Trust revoked for {agent_id}: {reason}"

def restore_trust(db, agent_id, score=None):
    """Restore a revoked agent's trust. Optionally set a new starting score."""
    if agent_id not in db["agents"]:
        return False, f"Unknown agent: {agent_id}"
    
    agent_data = db["agents"][agent_id]
    if not agent_data.get("revoked"):
        return False, f"{agent_id} is not revoked"
    
    restore_score = score or agent_data.get("trust_score_before_revocation", 0.5) * 0.5  # restore at half
    agent_data["revoked"] = False
    agent_data["trust_score"] = restore_score
    agent_data["stability"] = DEFAULT_STABILITY * 0.5  # reset stability lower
    agent_data["restored_at"] = datetime.now(timezone.utc).isoformat()
    
    # Re-add edge
    self_id = db["self"].get("agent_id", "self")
    db["edges"].append({
        "from": self_id,
        "to": agent_id,
        "weight": restore_score,
        "domain": "general",
        "created": datetime.now(timezone.utc).isoformat()
    })
    
    save_trust_db(db)
    
    append_interaction({
        "agent": agent_id,
        "outcome": "restoration",
        "new_score": restore_score,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return True, f"Trust restored for {agent_id} at {restore_score:.2f}"

# ── Graph Operations ────────────────────────────────────────────────────────

def find_trust_path(db, from_agent, to_agent, max_depth=4):
    """BFS to find trust path between agents."""
    if from_agent == to_agent:
        return [from_agent], 1.0
    
    edges = db.get("edges", [])
    adj = {}
    for e in edges:
        adj.setdefault(e["from"], []).append((e["to"], e["weight"]))
    
    queue = [(from_agent, [from_agent], 1.0)]
    visited = {from_agent}
    
    while queue:
        current, path, cumulative_trust = queue.pop(0)
        if len(path) > max_depth:
            continue
        for neighbor, weight in adj.get(current, []):
            if neighbor in visited:
                continue
            new_trust = cumulative_trust * weight * TRANSITIVE_DECAY
            new_path = path + [neighbor]
            if neighbor == to_agent:
                return new_path, new_trust
            visited.add(neighbor)
            queue.append((neighbor, new_path, new_trust))
    
    return None, 0.0

def export_dot(db):
    """Export trust graph as DOT format."""
    lines = ["digraph trust {", '  rankdir=LR;', '  node [shape=box, style=rounded];']
    for agent_id, data in db["agents"].items():
        eff = effective_trust(data)
        color = "green" if eff > 0.7 else "orange" if eff > 0.4 else "red"
        lines.append(f'  "{agent_id}" [label="{agent_id}\\n{eff:.2f}", color={color}];')
    for edge in db.get("edges", []):
        lines.append(f'  "{edge["from"]}" -> "{edge["to"]}" [label="{edge["weight"]:.2f}", penwidth={edge["weight"]*3:.1f}];')
    lines.append("}")
    return "\n".join(lines)

# ── Challenge-Response ──────────────────────────────────────────────────────

def create_challenge(agent_id):
    """Create a challenge nonce for an agent to sign."""
    nonce = secrets.token_hex(32)
    challenge = {
        "type": "atp_challenge",
        "challenger": load_trust_db()["self"].get("agent_id", "unknown"),
        "target": agent_id,
        "nonce": nonce,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "expires": time.time() + 3600  # 1 hour expiry
    }
    path = CHALLENGES_DIR / f"challenge_{agent_id}_{nonce[:8]}.json"
    path.write_text(json.dumps(challenge, indent=2))
    return path, challenge

def respond_to_challenge(challenge_path):
    """Sign a challenge with our skillsign key."""
    challenge = json.loads(Path(challenge_path).read_text())
    
    if time.time() > challenge.get("expires", 0):
        print("Challenge expired.")
        return None
    
    # Sign the nonce with skillsign
    nonce = challenge["nonce"]
    nonce_file = CHALLENGES_DIR / f"nonce_{nonce[:8]}.txt"
    nonce_file.write_text(nonce)
    
    # Use skillsign to sign
    result = subprocess.run(
        ["python3", str(Path.home() / "clawd/skillsign/skillsign.py"), "sign", str(nonce_file)],
        capture_output=True, text=True
    )
    
    response = {
        "type": "atp_response",
        "challenge_nonce": nonce,
        "responder": load_trust_db()["self"].get("agent_id", "unknown"),
        "signature_output": result.stdout.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    resp_path = CHALLENGES_DIR / f"response_{nonce[:8]}.json"
    resp_path.write_text(json.dumps(response, indent=2))
    nonce_file.unlink(missing_ok=True)
    return resp_path

# ── CLI Commands ────────────────────────────────────────────────────────────

def cmd_trust_add(args):
    db = load_trust_db()
    agent_id = args[0] if args else None
    if not agent_id:
        print("Usage: atp trust add <agent> --fingerprint <fp>")
        return
    
    fingerprint = None
    domain = "general"
    score = 0.5
    i = 1
    while i < len(args):
        if args[i] == "--fingerprint" and i + 1 < len(args):
            fingerprint = args[i + 1]; i += 2
        elif args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]; i += 2
        elif args[i] == "--score" and i + 1 < len(args):
            score = float(args[i + 1]); i += 2
        else:
            i += 1
    
    db["agents"][agent_id] = {
        "agent_id": agent_id,
        "fingerprint": fingerprint,
        "trust_score": score,
        "trust_domains": [domain],
        "stability": DEFAULT_STABILITY,
        "interaction_count": 0,
        "last_interaction": datetime.now(timezone.utc).isoformat(),
        "last_interaction_ts": time.time(),
        "added": datetime.now(timezone.utc).isoformat()
    }
    
    # Add edge from self
    self_id = db["self"].get("agent_id", "self")
    db["edges"].append({
        "from": self_id,
        "to": agent_id,
        "weight": score,
        "domain": domain,
        "created": datetime.now(timezone.utc).isoformat()
    })
    
    save_trust_db(db)
    print(f"✓ Added {agent_id} (fingerprint: {fingerprint}, domain: {domain}, initial trust: {score})")

def cmd_trust_list(args):
    db = load_trust_db()
    agents = db.get("agents", {})
    if not agents:
        print("No trusted agents.")
        return
    
    print(f"{'Agent':<20} {'Fingerprint':<18} {'Base':>6} {'Effective':>10} {'Stability':>10} {'Interactions':>13}")
    print("─" * 80)
    for aid, data in sorted(agents.items()):
        eff = effective_trust(data)
        fp = (data.get("fingerprint") or "?")[:16]
        print(f"{aid:<20} {fp:<18} {data.get('trust_score', 0):.2f}   {eff:>8.2f}   {data.get('stability', 0):>8.1f}h   {data.get('interaction_count', 0):>11}")

def cmd_trust_score(args):
    if not args:
        print("Usage: atp trust score <agent>")
        return
    db = load_trust_db()
    agent_id = args[0]
    data = db["agents"].get(agent_id)
    if not data:
        print(f"Unknown agent: {agent_id}")
        return
    
    eff = effective_trust(data)
    hours_since = (time.time() - data.get("last_interaction_ts", time.time())) / 3600
    
    print(f"Agent: {agent_id}")
    print(f"Fingerprint: {data.get('fingerprint', '?')}")
    print(f"Base trust: {data.get('trust_score', 0):.3f}")
    print(f"Effective trust: {eff:.3f}")
    print(f"Stability: {data.get('stability', 0):.1f}h")
    print(f"Domains: {', '.join(data.get('trust_domains', []))}")
    print(f"Interactions: {data.get('interaction_count', 0)}")
    print(f"Last interaction: {hours_since:.1f}h ago")
    
    # Trust level
    if eff > 0.8: level = "HIGH ✓"
    elif eff > 0.5: level = "MODERATE ◐"
    elif eff > 0.3: level = "LOW ◑"
    else: level = "MINIMAL ✗"
    print(f"Trust level: {level}")

def cmd_trust_remove(args):
    if not args:
        print("Usage: atp trust remove <agent>")
        return
    db = load_trust_db()
    agent_id = args[0]
    if agent_id in db["agents"]:
        del db["agents"][agent_id]
        db["edges"] = [e for e in db["edges"] if e["from"] != agent_id and e["to"] != agent_id]
        save_trust_db(db)
        print(f"✓ Removed {agent_id}")
    else:
        print(f"Unknown agent: {agent_id}")

def cmd_interact(args):
    if len(args) < 2:
        print("Usage: atp interact <agent> <positive|negative|neutral> [--domain <d>] [--note <n>]")
        return
    
    db = load_trust_db()
    agent_id = args[0]
    outcome = args[1]
    
    if agent_id not in db["agents"]:
        print(f"Unknown agent: {agent_id}. Add them first with 'trust add'.")
        return
    
    if outcome not in ("positive", "negative", "neutral"):
        print("Outcome must be: positive, negative, or neutral")
        return
    
    domain = "general"
    note = ""
    i = 2
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]; i += 2
        elif args[i] == "--note" and i + 1 < len(args):
            note = args[i + 1]; i += 2
        else:
            i += 1
    
    old_score = db["agents"][agent_id]["trust_score"]
    db["agents"][agent_id] = update_trust_after_interaction(db["agents"][agent_id], outcome, domain)
    new_score = db["agents"][agent_id]["trust_score"]
    
    # Update edge weight
    for edge in db["edges"]:
        if edge["to"] == agent_id:
            edge["weight"] = new_score
    
    save_trust_db(db)
    
    # Log interaction
    record = {
        "agent": agent_id,
        "outcome": outcome,
        "domain": domain,
        "note": note,
        "old_score": old_score,
        "new_score": new_score,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    append_interaction(record)
    
    delta = new_score - old_score
    arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
    print(f"✓ Interaction with {agent_id}: {outcome}")
    print(f"  Trust: {old_score:.3f} {arrow} {new_score:.3f} (Δ{delta:+.3f})")

def cmd_graph_show(args):
    db = load_trust_db()
    agents = db.get("agents", {})
    edges = db.get("edges", [])
    
    if not agents:
        print("Empty trust graph.")
        return
    
    self_id = db["self"].get("agent_id", "self")
    print(f"Trust Graph ({self_id})")
    print(f"  Nodes: {len(agents)}")
    print(f"  Edges: {len(edges)}")
    print()
    
    for edge in edges:
        eff = effective_trust(agents.get(edge["to"], {})) if edge["to"] in agents else edge["weight"]
        bar = "█" * int(eff * 20) + "░" * (20 - int(eff * 20))
        print(f"  {edge['from']} → {edge['to']} [{bar}] {eff:.2f} ({edge.get('domain', '?')})")

def cmd_graph_path(args):
    if len(args) < 2:
        print("Usage: atp graph path <from> <to>")
        return
    db = load_trust_db()
    path, trust = find_trust_path(db, args[0], args[1])
    if path:
        print(f"Path: {' → '.join(path)}")
        print(f"Transitive trust: {trust:.3f}")
    else:
        print(f"No trust path from {args[0]} to {args[1]}")

def cmd_graph_export(args):
    db = load_trust_db()
    fmt = "dot"
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            fmt = args[idx + 1]
    
    if fmt == "dot":
        print(export_dot(db))
    else:
        print(json.dumps(db, indent=2))

def cmd_challenge_create(args):
    if not args:
        print("Usage: atp challenge create <agent>")
        return
    path, challenge = create_challenge(args[0])
    print(f"✓ Challenge created: {path}")
    print(f"  Nonce: {challenge['nonce'][:16]}...")
    print(f"  Expires in 1 hour")

def cmd_status(args):
    db = load_trust_db()
    self_id = db["self"].get("agent_id", "not set")
    self_fp = db["self"].get("fingerprint", "not set")
    agents = db.get("agents", {})
    edges = db.get("edges", [])
    
    print(f"═══ Agent Trust Protocol ═══")
    print(f"  Identity: {self_id}")
    print(f"  Fingerprint: {self_fp}")
    print(f"  Trusted agents: {len(agents)}")
    print(f"  Trust edges: {len(edges)}")
    
    if agents:
        avg_trust = sum(effective_trust(a) for a in agents.values()) / len(agents)
        print(f"  Avg effective trust: {avg_trust:.2f}")
        
        # Most/least trusted
        sorted_agents = sorted(agents.items(), key=lambda x: effective_trust(x[1]), reverse=True)
        if sorted_agents:
            top = sorted_agents[0]
            print(f"  Most trusted: {top[0]} ({effective_trust(top[1]):.2f})")
            if len(sorted_agents) > 1:
                bot = sorted_agents[-1]
                print(f"  Least trusted: {bot[0]} ({effective_trust(bot[1]):.2f})")

def cmd_trust_revoke(args):
    if not args:
        print("Usage: atp trust revoke <agent> [--reason <reason>]")
        return
    agent_id = args[0]
    reason = "manual"
    if "--reason" in args:
        idx = args.index("--reason")
        if idx + 1 < len(args):
            reason = args[idx + 1]
    db = load_trust_db()
    ok, msg = revoke_trust(db, agent_id, reason)
    print(f"{'✓' if ok else '✗'} {msg}")

def cmd_trust_restore(args):
    if not args:
        print("Usage: atp trust restore <agent> [--score <0-1>]")
        return
    agent_id = args[0]
    score = None
    if "--score" in args:
        idx = args.index("--score")
        if idx + 1 < len(args):
            score = float(args[idx + 1])
    db = load_trust_db()
    ok, msg = restore_trust(db, agent_id, score)
    print(f"{'✓' if ok else '✗'} {msg}")

def cmd_trust_domains(args):
    """Show domain-specific trust for an agent."""
    if not args:
        print("Usage: atp trust domains <agent>")
        return
    db = load_trust_db()
    agent_id = args[0]
    data = db["agents"].get(agent_id)
    if not data:
        print(f"Unknown agent: {agent_id}")
        return
    
    print(f"Domain trust for {agent_id}:")
    print(f"  General: {effective_trust(data):.3f}")
    domains = data.get("domain_scores", {})
    if not domains:
        print("  (no domain-specific scores)")
    for dom, ds in sorted(domains.items()):
        eff = effective_trust(data, domain=dom)
        print(f"  {dom}: {eff:.3f} ({ds.get('interactions', 0)} interactions, stability: {ds.get('stability', 0):.1f}h)")

def cmd_init(args):
    """Initialize ATP with self identity."""
    db = load_trust_db()
    agent_id = args[0] if args else "parker"
    
    # Try to get fingerprint from skillsign
    fingerprint = None
    pub_key = SKILLSIGN_DIR / "keys" / f"{agent_id}.pub"
    if pub_key.exists():
        # Read first line for fingerprint-like info
        content = pub_key.read_text().strip()
        fingerprint = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    db["self"] = {
        "agent_id": agent_id,
        "fingerprint": fingerprint or "unknown"
    }
    save_trust_db(db)
    print(f"✓ Initialized ATP as {agent_id} (fingerprint: {fingerprint or 'unknown'})")

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ensure_dirs()
    args = sys.argv[1:]
    
    if not args:
        print(__doc__)
        return
    
    cmd = args[0]
    sub = args[1] if len(args) > 1 else None
    rest = args[2:]
    
    commands = {
        ("trust", "add"): cmd_trust_add,
        ("trust", "list"): cmd_trust_list,
        ("trust", "score"): cmd_trust_score,
        ("trust", "remove"): cmd_trust_remove,
        ("trust", "revoke"): cmd_trust_revoke,
        ("trust", "restore"): cmd_trust_restore,
        ("trust", "domains"): cmd_trust_domains,
        ("interact", None): lambda a: cmd_interact(args[1:]),
        ("graph", "show"): cmd_graph_show,
        ("graph", "path"): cmd_graph_path,
        ("graph", "export"): cmd_graph_export,
        ("challenge", "create"): cmd_challenge_create,
        ("status", None): cmd_status,
        ("init", None): lambda a: cmd_init(args[1:]),
    }
    
    handler = commands.get((cmd, sub))
    if not handler:
        # Try without sub
        handler = commands.get((cmd, None))
        if handler:
            handler(args[1:])
            return
        print(f"Unknown command: {cmd} {sub or ''}")
        print("Commands: trust (add|list|score|remove), interact, graph (show|path|export), challenge (create), status, init")
        return
    
    handler(rest)

if __name__ == "__main__":
    main()
