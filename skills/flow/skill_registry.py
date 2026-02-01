#!/usr/bin/env python3
"""
Skill Registry - Reusable Skill Database

Manages a registry of skills for reuse, tracking capabilities,
usage statistics, and compatibility information.
"""

import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class SkillMetadata:
    """Metadata for a registered skill"""
    name: str
    description: str
    path: str
    capabilities: List[str]
    tags: List[str]
    version: str = "1.0.0"
    author: str = ""
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    reuse_score: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    security_status: str = "unscanned"
    last_scan_date: str = ""
    hash: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


class SkillRegistry:
    """
    Registry for tracking and managing reusable skills.
    
    Implements a reusable object architecture where skills
    can be discovered, composed, and reused across different flows.
    """
    
    def __init__(self, registry_path: str = "./skill_registry.json"):
        self.registry_path = registry_path
        self.skills: Dict[str, SkillMetadata] = {}
        self._capability_index: Dict[str, Set[str]] = {}  # capability -> skill names
        self._tag_index: Dict[str, Set[str]] = {}  # tag -> skill names
        self._load_registry()
        
    def _load_registry(self):
        """Load registry from disk"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for name, skill_data in data.get('skills', {}).items():
                        self.skills[name] = SkillMetadata(**skill_data)
                    self._rebuild_indices()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load registry: {e}")
                
    def _save_registry(self):
        """Save registry to disk"""
        data = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'skills': {name: asdict(skill) for name, skill in self.skills.items()}
        }
        
        os.makedirs(os.path.dirname(self.registry_path) or '.', exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _rebuild_indices(self):
        """Rebuild capability and tag indices"""
        self._capability_index.clear()
        self._tag_index.clear()
        
        for name, skill in self.skills.items():
            for cap in skill.capabilities:
                if cap not in self._capability_index:
                    self._capability_index[cap] = set()
                self._capability_index[cap].add(name)
                
            for tag in skill.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(name)
                
    def _compute_hash(self, path: str) -> str:
        """Compute hash of skill file(s) for change detection"""
        hasher = hashlib.sha256()
        
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                hasher.update(f.read())
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in sorted(files):
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        with open(filepath, 'rb') as f:
                            hasher.update(f.read())
                            
        return hasher.hexdigest()[:16]
    
    def _calculate_reuse_score(self, skill: SkillMetadata) -> float:
        """
        Calculate reuse score based on:
        - Usage count
        - Number of capabilities
        - Security status
        - Recency of updates
        """
        score = 0.0
        
        # Usage contribution (max 40 points)
        score += min(skill.usage_count * 2, 40)
        
        # Capability coverage (max 30 points)
        score += min(len(skill.capabilities) * 5, 30)
        
        # Security bonus (max 20 points)
        security_scores = {
            'passed': 20,
            'warning': 10,
            'unscanned': 5,
            'failed': 0
        }
        score += security_scores.get(skill.security_status, 0)
        
        # Recency bonus (max 10 points)
        try:
            updated = datetime.fromisoformat(skill.updated_at)
            days_old = (datetime.now() - updated).days
            if days_old < 7:
                score += 10
            elif days_old < 30:
                score += 7
            elif days_old < 90:
                score += 4
        except:
            pass
            
        return round(score, 2)
    
    def register(self, skill: 'ComposedSkill') -> SkillMetadata:
        """
        Register a new skill or update existing one.
        
        Args:
            skill: ComposedSkill object from skill_composer
            
        Returns:
            SkillMetadata for the registered skill
        """
        existing = self.skills.get(skill.name)
        
        metadata = SkillMetadata(
            name=skill.name,
            description=skill.description,
            path=skill.output_path,
            capabilities=skill.capabilities,
            tags=skill.tags,
            version=skill.version if hasattr(skill, 'version') else "1.0.0",
            author=skill.author if hasattr(skill, 'author') else "",
            dependencies=skill.dependencies if hasattr(skill, 'dependencies') else [],
            created_at=existing.created_at if existing else datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            usage_count=existing.usage_count if existing else 0,
            security_status=skill.security_status if hasattr(skill, 'security_status') else "unscanned"
        )
        
        metadata.hash = self._compute_hash(skill.output_path)
        metadata.reuse_score = self._calculate_reuse_score(metadata)
        
        self.skills[skill.name] = metadata
        self._rebuild_indices()
        self._save_registry()
        
        return metadata
    
    def register_from_path(self, path: str, name: str, description: str,
                          capabilities: List[str], tags: List[str]) -> SkillMetadata:
        """
        Register a skill directly from a file path.
        """
        metadata = SkillMetadata(
            name=name,
            description=description,
            path=path,
            capabilities=capabilities,
            tags=tags
        )
        
        metadata.hash = self._compute_hash(path)
        metadata.reuse_score = self._calculate_reuse_score(metadata)
        
        self.skills[name] = metadata
        self._rebuild_indices()
        self._save_registry()
        
        return metadata
    
    def find_skills(self, capabilities: List[str] = None,
                    tags: List[str] = None,
                    min_reuse_score: float = 0) -> List[SkillMetadata]:
        """
        Find skills matching the given criteria.
        
        Args:
            capabilities: Required capabilities
            tags: Desired tags
            min_reuse_score: Minimum reuse score threshold
            
        Returns:
            List of matching skills, sorted by reuse score
        """
        candidates = set(self.skills.keys())
        
        # Filter by capabilities
        if capabilities:
            for cap in capabilities:
                cap_lower = cap.lower()
                matching = set()
                for c, skills in self._capability_index.items():
                    if cap_lower in c.lower():
                        matching.update(skills)
                candidates &= matching
                
        # Filter by tags
        if tags:
            tag_matches = set()
            for tag in tags:
                tag_lower = tag.lower()
                for t, skills in self._tag_index.items():
                    if tag_lower in t.lower():
                        tag_matches.update(skills)
            if tag_matches:
                candidates &= tag_matches
                
        # Filter by reuse score
        results = [
            self.skills[name] for name in candidates
            if self.skills[name].reuse_score >= min_reuse_score
        ]
        
        # Sort by reuse score (highest first)
        results.sort(key=lambda x: x.reuse_score, reverse=True)
        
        return results
    
    def get(self, name: str) -> Optional[Dict]:
        """Get skill details by name"""
        skill = self.skills.get(name)
        return asdict(skill) if skill else None
    
    def list_all(self) -> List[Dict]:
        """List all registered skills"""
        return [
            {'name': s.name, 'description': s.description, 
             'reuse_score': s.reuse_score, 'capabilities': s.capabilities}
            for s in sorted(self.skills.values(), 
                          key=lambda x: x.reuse_score, reverse=True)
        ]
    
    def increment_usage(self, name: str):
        """Increment usage count for a skill"""
        if name in self.skills:
            self.skills[name].usage_count += 1
            self.skills[name].reuse_score = self._calculate_reuse_score(self.skills[name])
            self._save_registry()
            
    def update_security_status(self, name: str, status: str, scan_date: str = None):
        """Update security scan status for a skill"""
        if name in self.skills:
            self.skills[name].security_status = status
            self.skills[name].last_scan_date = scan_date or datetime.now().isoformat()
            self.skills[name].reuse_score = self._calculate_reuse_score(self.skills[name])
            self._save_registry()
            
    def remove(self, name: str) -> bool:
        """Remove a skill from the registry"""
        if name in self.skills:
            del self.skills[name]
            self._rebuild_indices()
            self._save_registry()
            return True
        return False
    
    def get_capabilities(self) -> List[str]:
        """Get all registered capabilities"""
        return sorted(self._capability_index.keys())
    
    def get_tags(self) -> List[str]:
        """Get all registered tags"""
        return sorted(self._tag_index.keys())
