#!/usr/bin/env python3
"""
Skill Scanner Integration - Security Scanning for Flow

Integrates with the Skill Scanner tool to provide security
scanning capabilities within the Flow system.
"""

import os
import re
import ast
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ScanResult:
    """Result from a security scan"""
    path: str
    risk_level: str  # MINIMAL, LOW, MEDIUM, HIGH, CRITICAL
    total_issues: int
    critical_issues: List[Dict] = field(default_factory=list)
    high_issues: List[Dict] = field(default_factory=list)
    medium_issues: List[Dict] = field(default_factory=list)
    low_issues: List[Dict] = field(default_factory=list)
    scan_time: str = ""
    file_count: int = 0
    
    def __post_init__(self):
        if not self.scan_time:
            self.scan_time = datetime.now().isoformat()


class SkillScannerIntegration:
    """
    Security scanner for skill files.
    
    Detects malicious patterns including:
    - Data exfiltration attempts
    - System modification
    - Crypto mining indicators
    - Arbitrary code execution
    - Backdoors and obfuscation
    """
    
    # Security patterns to detect
    PATTERNS = {
        'critical': [
            (r'eval\s*\(', 'Arbitrary code execution via eval()'),
            (r'exec\s*\(', 'Arbitrary code execution via exec()'),
            (r'subprocess\.call.*shell\s*=\s*True', 'Shell injection risk'),
            (r'os\.system\s*\(', 'System command execution'),
            (r'__import__\s*\([^)]*\)', 'Dynamic import (potential code injection)'),
            (r'compile\s*\([^)]*exec', 'Dynamic code compilation'),
        ],
        'high': [
            (r'requests\.(get|post|put|delete).*\bpassword\b', 'Password in HTTP request'),
            (r'(api[_-]?key|secret|token)\s*=\s*["\'][^"]+["\']', 'Hardcoded credentials'),
            (r'base64\.b64decode', 'Base64 decoding (potential obfuscation)'),
            (r'socket\.socket', 'Raw socket usage'),
            (r'paramiko|fabric|ssh', 'SSH library usage'),
            (r'cryptography|pycrypto|Crypto\.', 'Cryptographic operations'),
        ],
        'medium': [
            (r'open\s*\([^)]*["\']w["\']', 'File write operation'),
            (r'os\.(remove|unlink|rmdir)', 'File deletion'),
            (r'shutil\.(rmtree|move|copy)', 'File system manipulation'),
            (r'sqlite3|mysql|psycopg|pymongo', 'Database access'),
            (r'requests\.(get|post)', 'External HTTP requests'),
            (r'urllib', 'URL operations'),
        ],
        'low': [
            (r'import\s+os', 'OS module import'),
            (r'import\s+sys', 'Sys module import'),
            (r'getenv|environ', 'Environment variable access'),
            (r'logging', 'Logging operations'),
            (r'tempfile', 'Temporary file operations'),
        ]
    }
    
    # Data exfiltration patterns
    EXFIL_PATTERNS = [
        (r'requests\.post.*json\s*=', 'Data posting via HTTP'),
        (r'smtp|email|sendmail', 'Email sending capability'),
        (r'webhook|slack|discord', 'Webhook communication'),
        (r'ftp|sftp', 'FTP operations'),
        (r'boto3|s3|gcs|azure\.storage', 'Cloud storage access'),
    ]
    
    # Crypto mining indicators
    CRYPTO_PATTERNS = [
        (r'stratum|pool\.', 'Mining pool connection'),
        (r'hashrate|nonce|difficulty', 'Mining terminology'),
        (r'monero|bitcoin|ethereum|xmr|btc|eth', 'Cryptocurrency references'),
        (r'cpuminer|gpuminer', 'Mining software'),
    ]
    
    def __init__(self, cache_results: bool = True):
        self.cache_results = cache_results
        self._cache: Dict[str, ScanResult] = {}
        
    def scan(self, path: str, force_rescan: bool = False) -> ScanResult:
        """
        Scan a skill file or directory for security issues.
        
        Args:
            path: Path to file or directory
            force_rescan: Bypass cache and rescan
            
        Returns:
            ScanResult with findings
        """
        # Check cache
        if self.cache_results and not force_rescan and path in self._cache:
            return self._cache[path]
            
        issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        file_count = 0
        
        # Get files to scan
        files_to_scan = []
        if os.path.isfile(path):
            files_to_scan = [path]
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        files_to_scan.append(os.path.join(root, file))
                        
        # Scan each file
        for filepath in files_to_scan:
            file_count += 1
            file_issues = self._scan_file(filepath)
            
            for level, level_issues in file_issues.items():
                issues[level].extend(level_issues)
                
        # Determine overall risk level
        risk_level = self._calculate_risk_level(issues)
        
        result = ScanResult(
            path=path,
            risk_level=risk_level,
            total_issues=sum(len(i) for i in issues.values()),
            critical_issues=issues['critical'],
            high_issues=issues['high'],
            medium_issues=issues['medium'],
            low_issues=issues['low'],
            file_count=file_count
        )
        
        # Cache result
        if self.cache_results:
            self._cache[path] = result
            
        return result
    
    def _scan_file(self, filepath: str) -> Dict[str, List[Dict]]:
        """Scan a single file for issues"""
        issues = {'critical': [], 'high': [], 'medium': [], 'low': []}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check standard patterns
            for level, patterns in self.PATTERNS.items():
                for pattern, description in patterns:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            issues[level].append({
                                'file': filepath,
                                'line': i,
                                'code': line.strip()[:100],
                                'description': description,
                                'pattern': pattern
                            })
                            
            # Check exfiltration patterns
            for pattern, description in self.EXFIL_PATTERNS:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues['high'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip()[:100],
                            'description': f'Data exfiltration: {description}',
                            'category': 'exfiltration'
                        })
                        
            # Check crypto mining patterns
            for pattern, description in self.CRYPTO_PATTERNS:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues['critical'].append({
                            'file': filepath,
                            'line': i,
                            'code': line.strip()[:100],
                            'description': f'Crypto mining: {description}',
                            'category': 'crypto_mining'
                        })
                        
            # AST analysis for deeper inspection
            try:
                tree = ast.parse(content)
                ast_issues = self._analyze_ast(tree, filepath)
                for level, level_issues in ast_issues.items():
                    issues[level].extend(level_issues)
            except SyntaxError:
                pass  # Skip AST analysis for files with syntax errors
                
        except Exception as e:
            issues['low'].append({
                'file': filepath,
                'line': 0,
                'code': '',
                'description': f'Could not scan file: {str(e)}'
            })
            
        return issues
    
    def _analyze_ast(self, tree: ast.AST, filepath: str) -> Dict[str, List[Dict]]:
        """Perform AST-based analysis"""
        issues = {'critical': [], 'high': [], 'medium': [], 'low': []}
        
        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node)
                
                if func_name in ('eval', 'exec', 'compile'):
                    issues['critical'].append({
                        'file': filepath,
                        'line': node.lineno,
                        'code': func_name,
                        'description': f'Dangerous function: {func_name}()',
                        'category': 'code_execution'
                    })
                    
            # Check for suspicious imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ('ctypes', 'cffi'):
                        issues['high'].append({
                            'file': filepath,
                            'line': node.lineno,
                            'code': f'import {alias.name}',
                            'description': 'Low-level memory access library',
                            'category': 'suspicious_import'
                        })
                        
        return issues
    
    def _get_func_name(self, node: ast.Call) -> str:
        """Extract function name from Call node"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ''
    
    def _calculate_risk_level(self, issues: Dict[str, List]) -> str:
        """Calculate overall risk level based on issues found"""
        if issues['critical']:
            return 'CRITICAL'
        elif len(issues['high']) >= 3:
            return 'CRITICAL'
        elif issues['high']:
            return 'HIGH'
        elif len(issues['medium']) >= 5:
            return 'HIGH'
        elif issues['medium']:
            return 'MEDIUM'
        elif issues['low']:
            return 'LOW'
        return 'MINIMAL'
    
    def get_report(self, result: ScanResult) -> str:
        """Generate a human-readable report from scan results"""
        lines = [
            "="*60,
            "SKILL SCANNER SECURITY REPORT",
            "="*60,
            f"Path: {result.path}",
            f"Files Scanned: {result.file_count}",
            f"Scan Time: {result.scan_time}",
            f"\nRISK LEVEL: {result.risk_level}",
            f"Total Issues: {result.total_issues}",
            "-"*60
        ]
        
        if result.critical_issues:
            lines.append(f"\nCRITICAL ({len(result.critical_issues)}):")
            for issue in result.critical_issues[:5]:
                lines.append(f"  [{issue.get('file', 'unknown')}:{issue.get('line', 0)}]")
                lines.append(f"    {issue.get('description', 'No description')}")
                
        if result.high_issues:
            lines.append(f"\nHIGH ({len(result.high_issues)}):")
            for issue in result.high_issues[:5]:
                lines.append(f"  [{issue.get('file', 'unknown')}:{issue.get('line', 0)}]")
                lines.append(f"    {issue.get('description', 'No description')}")
                
        if result.medium_issues:
            lines.append(f"\nMEDIUM ({len(result.medium_issues)}):")
            for issue in result.medium_issues[:3]:
                lines.append(f"  [{issue.get('file', 'unknown')}:{issue.get('line', 0)}]")
                lines.append(f"    {issue.get('description', 'No description')}")
                
        lines.append("\n" + "="*60)
        
        return "\n".join(lines)
    
    def clear_cache(self):
        """Clear the scan cache"""
        self._cache.clear()
