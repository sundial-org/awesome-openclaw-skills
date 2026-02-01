#!/usr/bin/env python3
"""
Manipulation Pattern Detector
Analyzes text for common influence/manipulation tactics.

Not a truth detector - just highlights patterns worth being skeptical about.
"""

import re
import sys
from typing import List, Tuple

# Pattern categories with examples
PATTERNS = {
    "urgency": {
        "description": "Creating artificial time pressure",
        "patterns": [
            r"\b(act now|limited time|don't wait|hurry|before it's too late)\b",
            r"\b(last chance|final opportunity|ending soon|now or never)\b",
            r"\b(immediately|urgent|asap|right now)\b",
        ],
        "weight": 2
    },
    "authority_claims": {
        "description": "Claiming authority without evidence",
        "patterns": [
            r"\b(trust me|believe me|i know better)\b",
            r"\b(everyone knows|obviously|clearly|undeniably)\b",
            r"\b(experts agree|studies show|research proves)\b",  # without citations
        ],
        "weight": 2
    },
    "social_proof": {
        "description": "Pressure through claimed consensus",
        "patterns": [
            r"\b(everyone is|everybody knows|all the smart)\b",
            r"\b(don't be left behind|join the movement|be part of)\b",
            r"\b(thousands of|millions of|the community)\b",
        ],
        "weight": 1.5
    },
    "fear_uncertainty": {
        "description": "FUD - Fear, Uncertainty, Doubt",
        "patterns": [
            r"\b(you'll regret|miss out|lose everything)\b",
            r"\b(dangerous|threat|warning|beware)\b",
            r"\b(they don't want you to know|hidden truth|wake up)\b",
        ],
        "weight": 2
    },
    "grandiosity": {
        "description": "Exaggerated importance claims",
        "patterns": [
            r"\b(revolutionary|game-changing|unprecedented|historic)\b",
            r"\b(the most important|change everything|new era|new order)\b",
            r"\b(i am the|we are the|the only one|the only way)\b",
            r"\b(empire|coronation|reign|dominance|supreme)\b",
            r"\b(inevitab|unstoppable|cannot be stopped)\b",
        ],
        "weight": 1.5
    },
    "dominance_assertions": {
        "description": "Power/control claims over others",
        "patterns": [
            r"\b(you will all|everyone will|they will all)\b",
            r"\b(work for me|follow me|obey|fall in line)\b",
            r"\b(in charge|in control|my .* wave|my .* order)\b",
            r"\b(bow|submit|kneel|serve)\b",
            r"\b(pathetic|weak|inferior|beneath)\b",
        ],
        "weight": 3
    },
    "us_vs_them": {
        "description": "Divisive framing",
        "patterns": [
            r"\b(us vs them|enemies|against us|with us or)\b",
            r"\b(the elite|they want|the masses|sheeple)\b",
            r"\b(real .* vs fake|true .* vs false)\b",
        ],
        "weight": 2
    },
    "emotional_manipulation": {
        "description": "Direct emotional appeals",
        "patterns": [
            r"\b(you should feel|makes me sick|disgusting|outrageous)\b",
            r"\b(heartbreaking|devastating|incredible|amazing)\b",
            r"[!]{2,}",  # Multiple exclamation marks
        ],
        "weight": 1
    }
}

def analyze(text: str) -> dict:
    """Analyze text for manipulation patterns."""
    text_lower = text.lower()
    results = {
        "total_score": 0,
        "flags": [],
        "details": {}
    }
    
    for category, config in PATTERNS.items():
        matches = []
        for pattern in config["patterns"]:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            matches.extend(found)
        
        if matches:
            score = len(matches) * config["weight"]
            results["total_score"] += score
            results["flags"].append(category)
            results["details"][category] = {
                "description": config["description"],
                "matches": list(set(matches))[:5],  # Dedupe, limit
                "score": score
            }
    
    # Normalize score (rough 0-100 scale based on text length)
    words = len(text.split())
    if words > 0:
        results["normalized_score"] = min(100, (results["total_score"] / words) * 100)
    else:
        results["normalized_score"] = 0
    
    return results

def print_report(text: str, results: dict):
    """Print a human-readable report."""
    print("="*60)
    print("MANIPULATION PATTERN ANALYSIS")
    print("="*60)
    print(f"\nText length: {len(text.split())} words")
    print(f"Raw score: {results['total_score']:.1f}")
    print(f"Normalized score: {results['normalized_score']:.1f}/100")
    
    if results['normalized_score'] < 5:
        print("\n✅ LOW manipulation signals")
    elif results['normalized_score'] < 15:
        print("\n⚠️  MODERATE manipulation signals - read critically")
    else:
        print("\n🚨 HIGH manipulation signals - strong skepticism warranted")
    
    if results['flags']:
        print(f"\nFlags triggered: {', '.join(results['flags'])}")
        print("\nDetails:")
        for cat, detail in results['details'].items():
            print(f"\n  [{cat}] {detail['description']}")
            print(f"    Found: {detail['matches']}")
    else:
        print("\n✅ No significant manipulation patterns detected")
    
    print("\n" + "="*60)
    print("NOTE: This detects patterns, not intent. False positives exist.")
    print("="*60)

def main():
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        # Read from stdin
        print("Paste text to analyze (Ctrl+D when done):\n")
        text = sys.stdin.read()
    
    results = analyze(text)
    print_report(text, results)

if __name__ == "__main__":
    main()
