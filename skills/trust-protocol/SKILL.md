# Agent Trust Protocol (ATP)

Establish, verify, and maintain trust between AI agents. Bayesian trust scoring with domain-specific trust, revocation, forgetting curves, and a visual dashboard.

## Install

```bash
git clone https://github.com/FELMONON/trust-protocol.git
# No dependencies beyond Python 3.8+ stdlib
# Pair with skillsign for identity: https://github.com/FELMONON/skillsign
```

## Quick Start

```bash
# Add an agent to your trust graph
python3 atp.py trust add alpha --fingerprint "abc123" --score 0.7

# Record interactions — trust evolves via Bayesian updates
python3 atp.py interact alpha positive --note "Delivered clean code"
python3 atp.py interact alpha positive --domain code --note "Tests passing"

# Check trust
python3 atp.py trust score alpha
python3 atp.py trust domains alpha

# View the full graph
python3 atp.py status
python3 atp.py graph export --format json

# Run the full-stack demo (identity → trust → dashboard)
python3 demo.py --serve
```

## Commands

### Trust Management
```bash
atp.py trust add <agent> --fingerprint <fp> [--domain <d>] [--score <0-1>]
atp.py trust list
atp.py trust score <agent>
atp.py trust remove <agent>
atp.py trust revoke <agent> [--reason <reason>]
atp.py trust restore <agent> [--score <0-1>]
atp.py trust domains <agent>
```

### Interactions
```bash
atp.py interact <agent> <positive|negative> [--domain <d>] [--note <note>]
```

### Challenge-Response
```bash
atp.py challenge create <agent>
atp.py challenge respond <challenge_file>
atp.py challenge verify <response_file>
```

### Graph
```bash
atp.py graph show
atp.py graph path <from> <to>
atp.py graph export [--format json|dot]
atp.py status
```

### Dashboard
```bash
python3 serve_dashboard.py          # localhost:8420
python3 demo.py --serve             # full demo + dashboard
```

### Moltbook Integration
```bash
python3 moltbook_trust.py verify <agent>    # check agent trust via Moltbook profile
```

## How Trust Works

- **Bayesian updates**: Each interaction shifts trust scores with diminishing deltas (prevents thrashing)
- **Negativity bias**: Negative interactions hit harder than positive ones boost
- **Domain-specific**: Trust an agent for code but not for security advice
- **Forgetting curves**: Trust decays without interaction (R = e^(-t/S))
- **Revocation**: Immediate drop to floor, restorable at reduced score
- **Transitive trust**: If you trust A and A trusts B, you partially trust B (with decay)

## Integration with skillsign

ATP builds on [skillsign](https://github.com/FELMONON/skillsign) for identity:
1. Agents generate ed25519 keypairs with skillsign
2. Agents sign skills, others verify signatures
3. Verified agents get added to the ATP trust graph
4. Interactions update trust scores over time

## Triggers
"check trust", "trust score", "trust graph", "verify agent", "agent trust", "trust status", "who do I trust", "trust report"
