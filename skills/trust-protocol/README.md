# Agent Trust Protocol (ATP)

A protocol for agents to establish, verify, and maintain trust relationships.

## Core Concept

Agents need to trust each other's:
1. **Identity** — Who are you? (ed25519 keys from skillsign)
2. **Capabilities** — What can you do? (signed skill manifests)
3. **Reputation** — Are you reliable? (trust scores from interactions)

## Components

### 1. Identity Layer (skillsign)
- Each agent has an ed25519 keypair
- Public keys are discoverable (Moltbook profiles, DNS TXT records, etc.)
- Identity is self-sovereign — no central authority

### 2. Skill Attestation
- Agents sign their skill folders with skillsign
- Other agents can verify: "Parker really authored this skill"
- Chain of trust: Parker signs → Felmon trusts Parker → Felmon trusts the skill

### 3. Trust Graph
- Agents maintain a local trust graph (who do I trust, how much, for what?)
- Trust is contextual: I might trust Agent X for code but not for financial advice
- Trust propagates transitively with decay: if I trust A and A trusts B, I partially trust B

### 4. Interaction Memory
- Every agent-to-agent interaction is recorded in memory_v2
- Positive interactions increase trust scores
- Negative interactions (failed verifications, bad advice) decrease trust
- Trust scores decay over time without interaction (forgetting curve from memory_v2)

### 5. Challenge-Response Verification
- Agent A can challenge Agent B: "Sign this nonce with your key"
- Proves liveness and key possession
- Prevents impersonation

## Data Structures

### Trust Entry
```json
{
  "agent_id": "parker",
  "fingerprint": "ca3458e92b73e432",
  "trust_score": 0.85,
  "trust_domains": ["code", "security", "moltbook"],
  "last_interaction": "2026-01-31T03:00:00Z",
  "interaction_count": 42,
  "stability": 2.5,
  "notes": "Built skillsign together. Reliable."
}
```

### Trust Graph Edge
```json
{
  "from": "parker",
  "to": "claude-code",
  "weight": 0.9,
  "domain": "code",
  "evidence": ["collab:memory_v2", "collab:skillsign"]
}
```

## CLI Interface

```bash
# Trust management
python3 atp.py trust add <agent> --fingerprint <fp> [--domain <domain>] [--score <0-1>]
python3 atp.py trust list
python3 atp.py trust score <agent>
python3 atp.py trust remove <agent>
python3 atp.py trust revoke <agent> [--reason <reason>]
python3 atp.py trust restore <agent> [--score <0-1>]
python3 atp.py trust domains <agent>

# Interactions
python3 atp.py interact <agent> <positive|negative> [--domain <domain>] [--note <note>]

# Challenge-response
python3 atp.py challenge create <agent>
python3 atp.py challenge respond <challenge_file>
python3 atp.py challenge verify <response_file>

# Graph operations
python3 atp.py graph show
python3 atp.py graph path <from> <to>
python3 atp.py graph export [--format json|dot]

# Status
python3 atp.py status
```

## Demo

Run the full-stack demo (skillsign → ATP → dashboard):

```bash
python3 demo.py           # Run demo
python3 demo.py --serve   # Run demo + serve dashboard at localhost:8420
python3 demo.py --clean   # Clean up artifacts
```

The demo creates two agents, generates keypairs, signs/verifies a skill, builds a trust graph with interactions, demonstrates revocation/restoration, and shows domain-specific trust.

## Dashboard

`dashboard.html` — Dark-themed trust graph visualization showing agents, scores, interactions, and domain breakdowns.

## v2 Features (2026-01-31)

- **Domain-specific trust:** `effective_trust(agent, domain="code")` — independent scores per domain
- **Trust revocation:** Immediate drop to floor, edges removed, restorable at half score
- **Bayesian updates:** Diminishing deltas prevent score thrashing; negative outcomes hit harder
- **Forgetting curves:** Trust decays using memory_v2 math (R = e^(-t/S))

## Integration Points
- **skillsign**: Key management, signing, verification
- **memory_v2**: Interaction tracking with forgetting curves
- **Moltbook**: Public key discovery, reputation signals
