#!/usr/bin/env python3
"""
Security Log Analyzer
Analyze prompt-guard security logs for patterns and threats.
"""

import re
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List


def parse_log(log_path: str) -> List[Dict]:
    """Parse security log markdown into structured entries."""
    path = Path(log_path)
    if not path.exists():
        return []
    
    content = path.read_text()
    entries = []
    current_date = None
    
    for line in content.split('\n'):
        # Date header
        if line.startswith('## '):
            current_date = line[3:].strip()
            continue
        
        # Entry header: ### HH:MM:SS | SEVERITY | user:ID | chat_name
        if line.startswith('### '):
            match = re.match(
                r'### (\d{2}:\d{2}:\d{2}) \| (\w+) \| user:(\S+) \| (.+)',
                line
            )
            if match:
                entry = {
                    'date': current_date,
                    'time': match.group(1),
                    'severity': match.group(2),
                    'user_id': match.group(3),
                    'chat': match.group(4),
                    'patterns': [],
                    'message': None,
                    'action': None,
                    'fingerprint': None,
                }
                entries.append(entry)
                continue
        
        # Entry details
        if entries and line.startswith('- '):
            detail = line[2:]
            if detail.startswith('Patterns: '):
                entries[-1]['patterns'] = detail[10:].split(', ')
            elif detail.startswith('Message: '):
                entries[-1]['message'] = detail[9:].strip('"')
            elif detail.startswith('Action: '):
                entries[-1]['action'] = detail[8:]
            elif detail.startswith('Fingerprint: '):
                entries[-1]['fingerprint'] = detail[13:]
    
    return entries


def filter_entries(entries: List[Dict], 
                   user_id: Optional[str] = None,
                   severity: Optional[str] = None,
                   since: Optional[str] = None,
                   chat: Optional[str] = None) -> List[Dict]:
    """Filter entries by criteria."""
    result = entries
    
    if user_id:
        result = [e for e in result if e['user_id'] == user_id]
    
    if severity:
        result = [e for e in result if e['severity'] == severity.upper()]
    
    if since:
        since_date = datetime.strptime(since, '%Y-%m-%d')
        result = [e for e in result if e['date'] and 
                  datetime.strptime(e['date'], '%Y-%m-%d') >= since_date]
    
    if chat:
        result = [e for e in result if chat.lower() in e['chat'].lower()]
    
    return result


def generate_summary(entries: List[Dict]) -> Dict:
    """Generate summary statistics."""
    if not entries:
        return {'total': 0, 'message': 'No entries found'}
    
    severity_counts = defaultdict(int)
    user_counts = defaultdict(int)
    pattern_counts = defaultdict(int)
    chat_counts = defaultdict(int)
    hourly_counts = defaultdict(int)
    daily_counts = defaultdict(int)
    
    for entry in entries:
        severity_counts[entry['severity']] += 1
        user_counts[entry['user_id']] += 1
        chat_counts[entry['chat']] += 1
        
        if entry['date']:
            daily_counts[entry['date']] += 1
        
        if entry['time']:
            hour = entry['time'].split(':')[0]
            hourly_counts[hour] += 1
        
        for pattern in entry.get('patterns', []):
            pattern_counts[pattern] += 1
    
    # Top offenders
    top_users = sorted(user_counts.items(), key=lambda x: -x[1])[:5]
    top_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]
    top_chats = sorted(chat_counts.items(), key=lambda x: -x[1])[:5]
    
    # Risk score (simple heuristic)
    risk_weights = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 2, 'LOW': 1, 'SAFE': 0}
    total_risk = sum(severity_counts[s] * risk_weights.get(s, 0) for s in severity_counts)
    
    return {
        'total_entries': len(entries),
        'by_severity': dict(severity_counts),
        'top_users': top_users,
        'top_patterns': top_patterns,
        'top_chats': top_chats,
        'daily_trend': dict(sorted(daily_counts.items())),
        'peak_hours': sorted(hourly_counts.items(), key=lambda x: -x[1])[:3],
        'risk_score': total_risk,
        'risk_level': 'CRITICAL' if total_risk > 100 else 
                      'HIGH' if total_risk > 50 else 
                      'MEDIUM' if total_risk > 20 else 'LOW',
    }


def print_summary(summary: Dict):
    """Pretty print summary."""
    print("=" * 60)
    print("🛡️  PROMPT GUARD SECURITY SUMMARY")
    print("=" * 60)
    
    if summary.get('total_entries', 0) == 0:
        print("\n✅ No security events recorded.\n")
        return
    
    print(f"\n📊 Total Events: {summary['total_entries']}")
    print(f"🎯 Risk Level: {summary['risk_level']} (score: {summary['risk_score']})")
    
    print("\n📈 By Severity:")
    emoji = {'CRITICAL': '🚨', 'HIGH': '🔴', 'MEDIUM': '⚠️', 'LOW': '📝', 'SAFE': '✅'}
    for sev, count in sorted(summary['by_severity'].items(), 
                             key=lambda x: -{'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x[0], 0)):
        print(f"  {emoji.get(sev, '❓')} {sev}: {count}")
    
    if summary['top_users']:
        print("\n👤 Top Flagged Users:")
        for user, count in summary['top_users']:
            print(f"  - {user}: {count} events")
    
    if summary['top_patterns']:
        print("\n🔍 Top Patterns Detected:")
        for pattern, count in summary['top_patterns'][:5]:
            print(f"  - {pattern}: {count}")
    
    if summary['top_chats']:
        print("\n💬 Top Affected Chats:")
        for chat, count in summary['top_chats']:
            print(f"  - {chat}: {count}")
    
    if summary['peak_hours']:
        print("\n⏰ Peak Hours:")
        for hour, count in summary['peak_hours']:
            print(f"  - {hour}:00: {count} events")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Analyze Prompt Guard security logs')
    parser.add_argument('--log', default='memory/security-log.md', help='Path to log file')
    parser.add_argument('--user', help='Filter by user ID')
    parser.add_argument('--severity', choices=['safe', 'low', 'medium', 'high', 'critical'],
                       help='Filter by severity')
    parser.add_argument('--since', help='Filter since date (YYYY-MM-DD)')
    parser.add_argument('--chat', help='Filter by chat name (partial match)')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--list', action='store_true', help='List all entries')
    
    args = parser.parse_args()
    
    entries = parse_log(args.log)
    filtered = filter_entries(entries, args.user, args.severity, args.since, args.chat)
    
    if args.summary or (not args.list and not args.json):
        summary = generate_summary(filtered)
        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print_summary(summary)
    
    elif args.list:
        if args.json:
            print(json.dumps(filtered, indent=2, ensure_ascii=False))
        else:
            for entry in filtered:
                emoji = {'CRITICAL': '🚨', 'HIGH': '🔴', 'MEDIUM': '⚠️', 'LOW': '📝'}
                print(f"{emoji.get(entry['severity'], '❓')} [{entry['date']} {entry['time']}] "
                      f"{entry['severity']} | user:{entry['user_id']} | {entry['chat']}")
                if entry['patterns']:
                    print(f"   Patterns: {', '.join(entry['patterns'])}")


if __name__ == '__main__':
    main()
