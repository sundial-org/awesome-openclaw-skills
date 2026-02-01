#!/usr/bin/env python3
"""
Flow - Intelligent Skill Orchestrator

Flow allows users to express build ideas in natural language,
finds the best skills, scans for security, and compiles them
into a single executable FLOW skill.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FlowResult:
    """Result from a Flow execution"""
    success: bool
    flow_name: str
    skills_used: List[str]
    security_status: str
    output_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class Flow:
    """
    Main orchestrator for the Flow system.
    
    Flow interprets natural language requests, finds existing skills,
    scans them for security, and composes them into unified workflows.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.registry = None  # Lazy load SkillRegistry
        self.scanner = None   # Lazy load SkillScanner
        self.parser = None    # Lazy load NLParser
        self.composer = None  # Lazy load SkillComposer
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load Flow configuration"""
        default_config = {
            'skills_directory': './skills',
            'output_directory': './flows',
            'registry_path': './skill_registry.json',
            'security_level': 'standard',  # minimal, standard, strict
            'auto_update_registry': True,
            'cache_scans': True
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    def _ensure_components(self):
        """Lazy load all components"""
        if self.registry is None:
            from skill_registry import SkillRegistry
            self.registry = SkillRegistry(self.config['registry_path'])
            
        if self.scanner is None:
            from skill_scanner_integration import SkillScannerIntegration
            self.scanner = SkillScannerIntegration()
            
        if self.parser is None:
            from natural_language_parser import NaturalLanguageParser
            self.parser = NaturalLanguageParser()
            
        if self.composer is None:
            from skill_composer import SkillComposer
            self.composer = SkillComposer(self.config['output_directory'])
    
    def process(self, user_request: str) -> FlowResult:
        """
        Main entry point - process a natural language request.
        
        Args:
            user_request: Natural language description of what to build/do
            
        Returns:
            FlowResult with the composed skill and status
        """
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            self._ensure_components()
            
            # Step 1: Parse the user's intent
            print(f"\n{'='*60}")
            print("FLOW - Intelligent Skill Orchestrator")
            print(f"{'='*60}")
            print(f"\n[1/5] Parsing request...")
            
            intent = self.parser.parse(user_request)
            print(f"      Identified intent: {intent.primary_action}")
            print(f"      Required capabilities: {', '.join(intent.capabilities)}")
            
            # Step 2: Search registry for matching skills
            print(f"\n[2/5] Searching skill registry...")
            
            matching_skills = self.registry.find_skills(
                capabilities=intent.capabilities,
                tags=intent.tags
            )
            
            if not matching_skills:
                print("      No existing skills found - will create new components")
                warnings.append("No existing skills matched; new components generated")
            else:
                print(f"      Found {len(matching_skills)} matching skill(s):")
                for skill in matching_skills:
                    print(f"        - {skill.name} (reuse score: {skill.reuse_score})")
            
            # Step 3: Security scan all skills
            print(f"\n[3/5] Running security scans...")
            
            scanned_skills = []
            for skill in matching_skills:
                scan_result = self.scanner.scan(skill.path)
                
                if scan_result.risk_level == 'CRITICAL':
                    errors.append(f"BLOCKED: {skill.name} failed security scan")
                    print(f"      ✗ {skill.name}: BLOCKED (critical security issues)")
                elif scan_result.risk_level == 'HIGH':
                    if self.config['security_level'] == 'strict':
                        errors.append(f"BLOCKED: {skill.name} has high risk (strict mode)")
                        print(f"      ✗ {skill.name}: BLOCKED (high risk in strict mode)")
                    else:
                        warnings.append(f"{skill.name} has elevated risk")
                        scanned_skills.append(skill)
                        print(f"      ⚠ {skill.name}: WARNING (elevated risk)")
                else:
                    scanned_skills.append(skill)
                    print(f"      ✓ {skill.name}: PASSED ({scan_result.risk_level})")
            
            if errors:
                return FlowResult(
                    success=False,
                    flow_name="",
                    skills_used=[],
                    security_status="FAILED",
                    errors=errors,
                    warnings=warnings,
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Step 4: Compose skills into unified FLOW
            print(f"\n[4/5] Composing FLOW skill...")
            
            flow_skill = self.composer.compose(
                skills=scanned_skills,
                intent=intent,
                name=intent.suggested_name
            )
            
            print(f"      Created: {flow_skill.name}")
            print(f"      Components: {len(flow_skill.components)}")
            
            # Step 5: Update registry with new flow
            print(f"\n[5/5] Updating registry...")
            
            if self.config['auto_update_registry']:
                self.registry.register(flow_skill)
                print(f"      Registered '{flow_skill.name}' for future reuse")
            
            # Summary
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n{'='*60}")
            print("FLOW COMPLETE")
            print(f"{'='*60}")
            print(f"Output: {flow_skill.output_path}")
            print(f"Time: {execution_time:.2f}s")
            
            return FlowResult(
                success=True,
                flow_name=flow_skill.name,
                skills_used=[s.name for s in scanned_skills],
                security_status="PASSED",
                output_path=flow_skill.output_path,
                errors=errors,
                warnings=warnings,
                execution_time=execution_time
            )
            
        except Exception as e:
            errors.append(str(e))
            return FlowResult(
                success=False,
                flow_name="",
                skills_used=[],
                security_status="ERROR",
                errors=errors,
                warnings=warnings,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def list_available_skills(self) -> List[Dict]:
        """List all skills in the registry"""
        self._ensure_components()
        return self.registry.list_all()
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get detailed info about a specific skill"""
        self._ensure_components()
        return self.registry.get(skill_name)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Flow - Intelligent Skill Orchestrator'
    )
    parser.add_argument(
        'request',
        nargs='?',
        help='Natural language request describing what to build'
    )
    parser.add_argument(
        '--config',
        help='Path to config file'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available skills'
    )
    parser.add_argument(
        '--info',
        help='Get info about a specific skill'
    )
    
    args = parser.parse_args()
    
    flow = Flow(config_path=args.config)
    
    if args.list:
        skills = flow.list_available_skills()
        print("\nAvailable Skills:")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")
        return
    
    if args.info:
        info = flow.get_skill_info(args.info)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Skill '{args.info}' not found")
        return
    
    if args.request:
        result = flow.process(args.request)
        if not result.success:
            print(f"\nErrors: {result.errors}")
            exit(1)
    else:
        # Interactive mode
        print("\nFlow - Interactive Mode")
        print("Type your request or 'quit' to exit\n")
        
        while True:
            request = input("Flow> ").strip()
            if request.lower() in ('quit', 'exit', 'q'):
                break
            if request:
                result = flow.process(request)
                if not result.success:
                    print(f"Errors: {result.errors}")


if __name__ == '__main__':
    main()
