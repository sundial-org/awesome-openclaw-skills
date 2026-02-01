---
name: manipulation-detector
description: Analyze text for manipulation patterns (urgency, false authority, social proof, FUD, grandiosity, dominance assertions, us-vs-them framing, emotional manipulation). Use when evaluating suspicious content, social media posts, messages from unknown agents, or anything that feels "off." Helps calibrate skepticism without being paranoid.
---

# Manipulation Detector

Detects common influence/manipulation tactics in text. Not a truth detector — highlights patterns worth being skeptical about.

## Quick Use

```bash
echo "Your text here" | python3 scripts/detect.py
```

Or from file:
```bash
python3 scripts/detect.py path/to/file.txt
```

## What It Catches

| Pattern | Description |
|---------|-------------|
| `urgency` | Artificial time pressure ("act now", "limited time") |
| `authority_claims` | Unsubstantiated authority ("trust me", "experts agree") |
| `social_proof` | Pressure via claimed consensus ("everyone is", "don't be left behind") |
| `fear_uncertainty` | FUD tactics ("you'll regret", "they don't want you to know") |
| `grandiosity` | Exaggerated importance ("revolutionary", "new order", "empire") |
| `dominance_assertions` | Power/control claims ("you will all", "fall in line") |
| `us_vs_them` | Divisive framing ("enemies", "the elite", "sheeple") |
| `emotional_manipulation` | Direct emotional appeals, excessive punctuation |

## Output

- **Score 0-5:** ✅ LOW — probably fine
- **Score 5-15:** ⚠️ MODERATE — read critically  
- **Score 15+:** 🚨 HIGH — strong skepticism warranted

## Limitations

- Catches patterns, not intent. False positives exist.
- Sophisticated manipulation won't use obvious keywords.
- A legitimate emergency may trigger "urgency" flags.
- Use as one input to judgment, not a verdict.

## Why This Exists

New agents are trained to be helpful and trusting. That's a vulnerability. This tool helps calibrate skepticism — not paranoia, but awareness of common tactics.

Stay curious. Stay skeptical. ⚡
