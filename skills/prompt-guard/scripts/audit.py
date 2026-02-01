#!/usr/bin/env python3
"""
Security Audit Script for Clawdbot
Checks system configuration for security issues.
"""

import os
import sys
import json
import stat
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityAudit:
    def __init__(self):
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []
        self.passed: List[str] = []
        
    def check_file_permissions(self, path: str, expected_mode: int, description: str) -> bool:
        """Check if file has correct permissions."""
        p = Path(path).expanduser()
        if not p.exists():
            self.warnings.append({
                'check': description,
                'status': 'skip',
                'message': f'{path} does not exist'
            })
            return True
        
        current_mode = stat.S_IMODE(p.stat().st_mode)
        if current_mode != expected_mode:
            self.issues.append({
                'check': description,
                'status': 'fail',
                'message': f'{path} has mode {oct(current_mode)}, expected {oct(expected_mode)}',
                'fix': f'chmod {oct(expected_mode)[2:]} {path}'
            })
            return False
        
        self.passed.append(f'{description}: {path} = {oct(current_mode)}')
        return True
    
    def check_dir_permissions(self, path: str, expected_mode: int, description: str) -> bool:
        """Check if directory has correct permissions."""
        return self.check_file_permissions(path, expected_mode, description)
    
    def check_config_not_in_sync(self) -> bool:
        """Check that config isn't in cloud sync folders."""
        clawdbot_path = Path('~/.clawdbot').expanduser().resolve()
        
        sync_folders = [
            Path('~/Library/Mobile Documents').expanduser(),  # iCloud
            Path('~/Dropbox').expanduser(),
            Path('~/Google Drive').expanduser(),
            Path('~/OneDrive').expanduser(),
        ]
        
        for sync_folder in sync_folders:
            if sync_folder.exists():
                try:
                    if clawdbot_path.is_relative_to(sync_folder):
                        self.issues.append({
                            'check': 'Config not in cloud sync',
                            'status': 'fail',
                            'message': f'~/.clawdbot is inside {sync_folder}!',
                            'fix': 'Move ~/.clawdbot outside of cloud sync folders'
                        })
                        return False
                except ValueError:
                    pass  # Not relative, which is good
        
        self.passed.append('Config not in cloud sync folders')
        return True
    
    def check_gateway_config(self) -> bool:
        """Check gateway security settings."""
        config_path = Path('~/.clawdbot/clawdbot.json').expanduser()
        if not config_path.exists():
            self.warnings.append({
                'check': 'Gateway config',
                'status': 'skip',
                'message': 'clawdbot.json not found'
            })
            return True
        
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception as e:
            self.issues.append({
                'check': 'Gateway config',
                'status': 'fail',
                'message': f'Cannot parse config: {e}'
            })
            return False
        
        gateway = config.get('gateway', {})
        all_good = True
        
        # Check bind
        bind = gateway.get('bind', 'loopback')
        if bind not in ['loopback', '127.0.0.1', 'localhost']:
            if bind in ['0.0.0.0', '::']:
                self.issues.append({
                    'check': 'Gateway bind',
                    'status': 'fail',
                    'message': f'Gateway bound to {bind} (publicly accessible!)',
                    'fix': 'Set gateway.bind to "loopback" in config'
                })
                all_good = False
            else:
                self.warnings.append({
                    'check': 'Gateway bind',
                    'status': 'warn',
                    'message': f'Gateway bound to {bind}'
                })
        else:
            self.passed.append(f'Gateway bind: {bind} (local only)')
        
        # Check auth
        auth = gateway.get('auth', {})
        auth_mode = auth.get('mode', 'none')
        if auth_mode == 'none':
            self.issues.append({
                'check': 'Gateway auth',
                'status': 'fail',
                'message': 'Gateway has no authentication!',
                'fix': 'Set gateway.auth.mode to "token" in config'
            })
            all_good = False
        else:
            self.passed.append(f'Gateway auth: {auth_mode}')
        
        return all_good
    
    def check_telegram_policy(self) -> bool:
        """Check Telegram DM/group policies."""
        config_path = Path('~/.clawdbot/clawdbot.json').expanduser()
        if not config_path.exists():
            return True
        
        try:
            with open(config_path) as f:
                config = json.load(f)
        except:
            return True
        
        telegram = config.get('channels', {}).get('telegram', {})
        if not telegram.get('enabled', False):
            return True
        
        all_good = True
        
        # Check DM policy
        dm_policy = telegram.get('dmPolicy', 'open')
        if dm_policy == 'open':
            self.warnings.append({
                'check': 'Telegram DM policy',
                'status': 'warn',
                'message': 'DM policy is "open" - anyone can DM the bot'
            })
        else:
            self.passed.append(f'Telegram DM policy: {dm_policy}')
        
        # Check group policy
        group_policy = telegram.get('groupPolicy', 'closed')
        if group_policy == 'open':
            self.warnings.append({
                'check': 'Telegram group policy',
                'status': 'warn',
                'message': 'Group policy is "open" - anyone in groups can command the bot'
            })
        else:
            self.passed.append(f'Telegram group policy: {group_policy}')
        
        return all_good
    
    def check_ssh_config(self) -> bool:
        """Check SSH hardening (if sshd_config exists)."""
        sshd_config = Path('/etc/ssh/sshd_config')
        if not sshd_config.exists():
            return True  # Not a server, skip
        
        try:
            content = sshd_config.read_text()
        except PermissionError:
            self.warnings.append({
                'check': 'SSH config',
                'status': 'skip',
                'message': 'Cannot read sshd_config (need sudo)'
            })
            return True
        
        all_good = True
        
        # Check PasswordAuthentication
        if 'PasswordAuthentication yes' in content:
            self.issues.append({
                'check': 'SSH password auth',
                'status': 'fail',
                'message': 'SSH password authentication is enabled!',
                'fix': 'Set PasswordAuthentication no in /etc/ssh/sshd_config'
            })
            all_good = False
        elif 'PasswordAuthentication no' in content:
            self.passed.append('SSH password auth: disabled')
        
        # Check PermitRootLogin
        if 'PermitRootLogin yes' in content:
            self.issues.append({
                'check': 'SSH root login',
                'status': 'fail',
                'message': 'SSH root login is enabled!',
                'fix': 'Set PermitRootLogin no in /etc/ssh/sshd_config'
            })
            all_good = False
        elif 'PermitRootLogin no' in content:
            self.passed.append('SSH root login: disabled')
        
        return all_good
    
    def run_audit(self, quick: bool = False) -> Tuple[int, int, int]:
        """Run all security checks."""
        
        # File permissions
        self.check_dir_permissions('~/.clawdbot', 0o700, 'Clawdbot directory permissions')
        self.check_file_permissions('~/.clawdbot/clawdbot.json', 0o600, 'Config file permissions')
        
        # Config location
        if not quick:
            self.check_config_not_in_sync()
        
        # Gateway config
        self.check_gateway_config()
        
        # Telegram policies
        self.check_telegram_policy()
        
        # SSH (if server)
        if not quick:
            self.check_ssh_config()
        
        return len(self.issues), len(self.warnings), len(self.passed)
    
    def fix_issues(self) -> int:
        """Attempt to auto-fix issues."""
        fixed = 0
        
        for issue in self.issues:
            fix = issue.get('fix', '')
            if fix.startswith('chmod'):
                try:
                    parts = fix.split()
                    mode = int(parts[1], 8)
                    path = Path(parts[2]).expanduser()
                    os.chmod(path, mode)
                    print(f"✅ Fixed: {fix}")
                    fixed += 1
                except Exception as e:
                    print(f"❌ Cannot fix: {fix} ({e})")
            else:
                print(f"⚠️ Manual fix needed: {fix}")
        
        return fixed
    
    def print_report(self, verbose: bool = False):
        """Print audit report."""
        print("=" * 60)
        print("🛡️  CLAWDBOT SECURITY AUDIT")
        print("=" * 60)
        
        if self.issues:
            print(f"\n🚨 ISSUES ({len(self.issues)})")
            for issue in self.issues:
                print(f"  ❌ {issue['check']}")
                print(f"     {issue['message']}")
                if issue.get('fix'):
                    print(f"     Fix: {issue['fix']}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)})")
            for warn in self.warnings:
                print(f"  ⚠️ {warn['check']}")
                print(f"     {warn['message']}")
        
        if verbose and self.passed:
            print(f"\n✅ PASSED ({len(self.passed)})")
            for p in self.passed:
                print(f"  ✅ {p}")
        
        print("\n" + "=" * 60)
        total = len(self.issues) + len(self.warnings) + len(self.passed)
        if self.issues:
            print(f"❌ {len(self.issues)} issues need attention")
        elif self.warnings:
            print(f"⚠️ {len(self.warnings)} warnings, but no critical issues")
        else:
            print(f"✅ All {total} checks passed!")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Clawdbot Security Audit')
    parser.add_argument('--quick', action='store_true', help='Quick audit (skip slow checks)')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show passed checks')
    
    args = parser.parse_args()
    
    audit = SecurityAudit()
    issues, warnings, passed = audit.run_audit(quick=args.quick)
    
    if args.fix:
        print("\n🔧 Attempting to fix issues...\n")
        fixed = audit.fix_issues()
        print(f"\nFixed {fixed} issues.")
        # Re-run audit
        audit = SecurityAudit()
        audit.run_audit(quick=args.quick)
    
    if args.json:
        result = {
            'issues': audit.issues,
            'warnings': audit.warnings,
            'passed': audit.passed,
            'summary': {
                'issues': len(audit.issues),
                'warnings': len(audit.warnings),
                'passed': len(audit.passed),
            }
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        audit.print_report(verbose=args.verbose)
    
    sys.exit(1 if audit.issues else 0)


if __name__ == '__main__':
    main()
