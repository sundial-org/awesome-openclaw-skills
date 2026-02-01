#!/usr/bin/env python3
"""
Skill Composer - Compiles Skills into Unified FLOW

Takes multiple skills and composes them into a single,
executable FLOW skill with proper orchestration.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ComposedSkill:
    """A composed skill ready for execution"""
    name: str
    description: str
    output_path: str
    components: List[str]
    capabilities: List[str]
    tags: List[str]
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    security_status: str = "unscanned"
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class SkillComposer:
    """
    Composes multiple skills into a unified FLOW.
    
    The composer handles:
    - Dependency resolution
    - Code merging and organization
    - Interface generation
    - Execution flow orchestration
    """
    
    def __init__(self, output_directory: str = "./flows"):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
        
    def compose(self, skills: List, intent: 'ParsedIntent', 
                name: Optional[str] = None) -> ComposedSkill:
        """
        Compose multiple skills into a single FLOW.
        
        Args:
            skills: List of SkillMetadata objects to compose
            intent: ParsedIntent from the NLP parser
            name: Optional name for the composed skill
            
        Returns:
            ComposedSkill ready for execution
        """
        # Generate name if not provided
        if not name:
            name = self._generate_name(intent)
            
        # Resolve dependencies
        ordered_skills = self._resolve_dependencies(skills)
        
        # Collect all capabilities and tags
        all_capabilities = set()
        all_tags = set()
        all_dependencies = set()
        
        for skill in ordered_skills:
            all_capabilities.update(skill.capabilities)
            all_tags.update(skill.tags)
            all_dependencies.update(skill.dependencies)
            
        # Add capabilities from intent
        all_capabilities.update(intent.capabilities)
        all_tags.update(intent.tags)
        
        # Generate the composed skill code
        output_path = self._generate_skill_code(
            name=name,
            skills=ordered_skills,
            intent=intent
        )
        
        return ComposedSkill(
            name=name,
            description=intent.description or f"Composed flow for: {intent.primary_action}",
            output_path=output_path,
            components=[s.name for s in ordered_skills],
            capabilities=list(all_capabilities),
            tags=list(all_tags),
            dependencies=list(all_dependencies)
        )
    
    def _generate_name(self, intent: 'ParsedIntent') -> str:
        """Generate a name for the composed skill"""
        if intent.suggested_name:
            return intent.suggested_name
            
        # Create name from primary action
        words = intent.primary_action.lower().split()
        name = '_'.join(words[:3])  # Take first 3 words
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"flow_{name}_{timestamp}"
    
    def _resolve_dependencies(self, skills: List) -> List:
        """
        Resolve skill dependencies and return ordered list.
        Uses topological sort for proper ordering.
        """
        if not skills:
            return []
            
        # Build dependency graph
        skill_map = {s.name: s for s in skills}
        in_degree = {s.name: 0 for s in skills}
        
        for skill in skills:
            for dep in skill.dependencies:
                if dep in skill_map:
                    in_degree[skill.name] += 1
                    
        # Topological sort
        ordered = []
        queue = [name for name, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            ordered.append(skill_map[current])
            
            for skill in skills:
                if current in skill.dependencies:
                    in_degree[skill.name] -= 1
                    if in_degree[skill.name] == 0:
                        queue.append(skill.name)
                        
        # If not all skills are ordered, there's a cycle
        # In that case, just return original order
        if len(ordered) != len(skills):
            return skills
            
        return ordered
    
    def _generate_skill_code(self, name: str, skills: List, 
                             intent: 'ParsedIntent') -> str:
        """
        Generate the composed skill Python code.
        """
        output_path = os.path.join(self.output_directory, f"{name}.py")
        
        # Generate the code
        code_lines = [
            '#!/usr/bin/env python3',
            '"""',
            f'{name} - Composed FLOW Skill',
            '',
            f'Description: {intent.description or intent.primary_action}',
            f'Generated: {datetime.now().isoformat()}',
            f'Components: {[s.name for s in skills]}',
            '"""',
            '',
            'import os',
            'import sys',
            'from typing import Dict, Any, Optional',
            '',
            '',
            'class FlowExecutor:',
            '    """Executes the composed flow"""',
            '    ',
            '    def __init__(self):',
            '        self.components = {}',
            '        self.results = {}',
            '        ',
        ]
        
        # Add component loading
        if skills:
            code_lines.extend([
                '    def load_components(self):',
                '        """Load all component skills"""',
            ])
            
            for skill in skills:
                code_lines.append(
                    f'        # Component: {skill.name}'
                )
                code_lines.append(
                    f'        self.components["{skill.name}"] = self._load_skill("{skill.path}")'
                )
                
            code_lines.extend([
                '        ',
                '    def _load_skill(self, path: str):',
                '        """Load a skill module"""',
                '        # Implementation would dynamically load the skill',
                '        return {"path": path, "loaded": True}',
                '        ',
            ])
        
        # Add execution method
        code_lines.extend([
            '    def execute(self, **kwargs) -> Dict[str, Any]:',
            '        """',
            f'        Execute the flow: {intent.primary_action}',
            '        """',
            '        results = {}',
            '        ',
        ])
        
        # Add steps based on intent
        for i, step in enumerate(intent.steps, 1):
            code_lines.extend([
                f'        # Step {i}: {step}',
                f'        results["step_{i}"] = self._execute_step("{step}", kwargs)',
                '        ',
            ])
            
        code_lines.extend([
            '        return {',
            '            "success": True,',
            '            "results": results,',
            f'            "flow_name": "{name}"',
            '        }',
            '        ',
            '    def _execute_step(self, step: str, context: Dict) -> Dict:',
            '        """Execute a single step"""',
            '        return {"step": step, "status": "completed"}',
            '',
            '',
            'def main():',
            '    """Main entry point"""',
            '    executor = FlowExecutor()',
            '    ',
        ])
        
        if skills:
            code_lines.append('    executor.load_components()'))
            
        code_lines.extend([
            '    ',
            '    result = executor.execute()',
            '    print(f"Flow completed: {result}")',
            '    return result',
            '',
            '',
            'if __name__ == "__main__":',
            '    main()',
        ])
        
        # Write the file
        with open(output_path, 'w') as f:
            f.write('\n'.join(code_lines))
            
        return output_path
    
    def compose_from_templates(self, intent: 'ParsedIntent', 
                               templates: List[Dict]) -> ComposedSkill:
        """
        Compose a skill from code templates when no existing skills match.
        """
        name = self._generate_name(intent)
        
        # Generate code from templates
        output_path = self._generate_from_templates(name, intent, templates)
        
        return ComposedSkill(
            name=name,
            description=intent.description or intent.primary_action,
            output_path=output_path,
            components=[],
            capabilities=intent.capabilities,
            tags=intent.tags
        )
    
    def _generate_from_templates(self, name: str, intent: 'ParsedIntent',
                                  templates: List[Dict]) -> str:
        """
        Generate skill code from templates.
        """
        output_path = os.path.join(self.output_directory, f"{name}.py")
        
        code_lines = [
            '#!/usr/bin/env python3',
            f'"""Generated FLOW: {name}"""',
            '',
        ]
        
        for template in templates:
            code_lines.append(f'# Template: {template.get("name", "unknown")}')
            code_lines.append(template.get('code', '# No code provided'))
            code_lines.append('')
            
        with open(output_path, 'w') as f:
            f.write('\n'.join(code_lines))
            
        return output_path
