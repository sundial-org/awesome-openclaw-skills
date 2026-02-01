#!/usr/bin/env python3
"""Translate portfolio headlines in briefing JSON using openclaw.

Usage: python3 translate_portfolio.py /path/to/briefing.json [--lang de]

Reads briefing JSON, translates portfolio article headlines via openclaw,
writes back the modified JSON.
"""

import argparse
import json
import re
import subprocess
import sys


def extract_headlines(portfolio_message: str) -> list[str]:
    """Extract article headlines (lines starting with •) from portfolio message."""
    headlines = []
    for line in portfolio_message.split('\n'):
        line = line.strip()
        if line.startswith('•'):
            # Remove bullet, reference number, and clean up
            # Format: "• Headline text [1]"
            match = re.match(r'•\s*(.+?)\s*\[\d+\]$', line)
            if match:
                headlines.append(match.group(1))
            else:
                # No reference number
                headlines.append(line[1:].strip())
    return headlines


def translate_headlines(headlines: list[str], lang: str = "de") -> list[str]:
    """Translate headlines using openclaw agent."""
    if not headlines:
        return []

    prompt = f"""Translate these English headlines to German.
Return ONLY a JSON array of strings in the same order.
Example: ["Übersetzung 1", "Übersetzung 2"]
Do not add commentary.

Headlines:
"""
    for idx, title in enumerate(headlines, start=1):
        prompt += f"{idx}. {title}\n"

    try:
        result = subprocess.run(
            [
                'openclaw', 'agent',
                '--session-id', 'finance-news-translate-portfolio',
                '--message', prompt,
                '--json',
                '--timeout', '60'
            ],
            capture_output=True,
            text=True,
            timeout=90
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        print(f"⚠️ Translation failed: {e}", file=sys.stderr)
        return headlines

    if result.returncode != 0:
        print(f"⚠️ openclaw error: {result.stderr}", file=sys.stderr)
        return headlines

    # Extract reply from openclaw JSON output
    # Format: {"result": {"payloads": [{"text": "..."}]}}
    # Note: openclaw may print plugin loading messages before JSON, so find the JSON start
    stdout = result.stdout
    json_start = stdout.find('{')
    if json_start > 0:
        stdout = stdout[json_start:]

    try:
        output = json.loads(stdout)
        payloads = output.get('result', {}).get('payloads', [])
        if payloads and payloads[0].get('text'):
            reply = payloads[0]['text']
        else:
            reply = output.get('reply', '') or output.get('message', '') or stdout
    except json.JSONDecodeError:
        reply = stdout

    # Parse JSON array from reply
    json_text = reply.strip()
    if "```" in json_text:
        match = re.search(r'```(?:json)?\s*(.*?)```', json_text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()

    try:
        translated = json.loads(json_text)
        if isinstance(translated, list) and len(translated) == len(headlines):
            print(f"✅ Translated {len(headlines)} portfolio headlines", file=sys.stderr)
            return translated
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error: {e}", file=sys.stderr)

    print(f"⚠️ Translation failed, using original headlines", file=sys.stderr)
    return headlines


def replace_headlines(portfolio_message: str, original: list[str], translated: list[str]) -> str:
    """Replace original headlines with translated ones in portfolio message."""
    result = portfolio_message
    for orig, trans in zip(original, translated):
        if orig != trans:
            # Replace the headline text, preserving bullet and reference
            result = result.replace(f"• {orig}", f"• {trans}")
    return result


def main():
    parser = argparse.ArgumentParser(description='Translate portfolio headlines')
    parser.add_argument('json_file', help='Path to briefing JSON file')
    parser.add_argument('--lang', default='de', help='Target language (default: de)')
    args = parser.parse_args()

    # Read JSON
    try:
        with open(args.json_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading {args.json_file}: {e}", file=sys.stderr)
        sys.exit(1)

    portfolio_message = data.get('portfolio_message', '')
    if not portfolio_message:
        print("No portfolio_message to translate", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # Extract, translate, replace
    headlines = extract_headlines(portfolio_message)
    if not headlines:
        print("No headlines found in portfolio_message", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(f"📝 Found {len(headlines)} headlines to translate", file=sys.stderr)
    translated = translate_headlines(headlines, args.lang)

    # Update portfolio message
    data['portfolio_message'] = replace_headlines(portfolio_message, headlines, translated)

    # Write back
    with open(args.json_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated {args.json_file}", file=sys.stderr)


if __name__ == '__main__':
    main()
