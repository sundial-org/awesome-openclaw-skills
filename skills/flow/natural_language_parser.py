#!/usr/bin/env python3
"""
Natural Language Parser - Interprets User Intent

Parses natural language requests to extract intent,
required capabilities, and execution steps.
"""

import re
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class ParsedIntent:
    """Parsed intent from natural language request"""
    primary_action: str
    description: str
    capabilities: List[str]
    tags: List[str]
    steps: List[str]
    suggested_name: str = ""
    confidence: float = 0.0
    raw_request: str = ""
    

class NaturalLanguageParser:
    """
    Parses natural language requests into structured intents.
    
    Uses pattern matching and keyword extraction to understand
    what the user wants to build or accomplish.
    """
    
    # Action keywords that indicate what the user wants to do
    ACTION_PATTERNS = {
        'build': ['build', 'create', 'make', 'develop', 'construct'],
        'automate': ['automate', 'schedule', 'trigger', 'run automatically'],
        'analyze': ['analyze', 'examine', 'inspect', 'review', 'scan'],
        'transform': ['convert', 'transform', 'change', 'modify'],
        'integrate': ['integrate', 'connect', 'link', 'combine'],
        'monitor': ['monitor', 'watch', 'track', 'observe'],
        'generate': ['generate', 'produce', 'output', 'create'],
        'scrape': ['scrape', 'extract', 'pull', 'fetch'],
        'process': ['process', 'handle', 'manage', 'work with'],
    }
    
    # Capability indicators
    CAPABILITY_PATTERNS = {
        'web': ['web', 'website', 'url', 'http', 'browser', 'html'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'webhook'],
        'file': ['file', 'document', 'pdf', 'csv', 'excel', 'json'],
        'database': ['database', 'sql', 'mongodb', 'data', 'store'],
        'email': ['email', 'mail', 'smtp', 'inbox'],
        'video': ['video', 'youtube', 'stream', 'media'],
        'image': ['image', 'photo', 'picture', 'screenshot'],
        'text': ['text', 'nlp', 'language', 'content'],
        'ai': ['ai', 'ml', 'model', 'gpt', 'claude', 'llm'],
        'automation': ['cron', 'schedule', 'trigger', 'workflow'],
    }
    
    # Tag patterns for categorization
    TAG_PATTERNS = {
        'productivity': ['productivity', 'efficiency', 'workflow'],
        'development': ['code', 'programming', 'developer', 'github'],
        'business': ['business', 'enterprise', 'company', 'work'],
        'personal': ['personal', 'home', 'private'],
        'security': ['security', 'safe', 'protect', 'encrypt'],
    }
    
    def __init__(self):
        # Compile patterns for efficiency
        self._action_regex = self._compile_patterns(self.ACTION_PATTERNS)
        self._capability_regex = self._compile_patterns(self.CAPABILITY_PATTERNS)
        self._tag_regex = self._compile_patterns(self.TAG_PATTERNS)
        
    def _compile_patterns(self, patterns: Dict[str, List[str]]) -> Dict[str, re.Pattern]:
        """Compile pattern lists into regex patterns"""
        compiled = {}
        for key, words in patterns.items():
            pattern = r'\b(' + '|'.join(re.escape(w) for w in words) + r')\b'
            compiled[key] = re.compile(pattern, re.IGNORECASE)
        return compiled
    
    def parse(self, request: str) -> ParsedIntent:
        """
        Parse a natural language request into structured intent.
        
        Args:
            request: Natural language description of what to build
            
        Returns:
            ParsedIntent with extracted information
        """
        # Clean the request
        cleaned = self._clean_request(request)
        
        # Extract primary action
        primary_action = self._extract_primary_action(cleaned)
        
        # Extract capabilities needed
        capabilities = self._extract_capabilities(cleaned)
        
        # Extract tags for categorization
        tags = self._extract_tags(cleaned)
        
        # Break down into steps
        steps = self._extract_steps(cleaned)
        
        # Generate suggested name
        suggested_name = self._generate_name(primary_action, capabilities)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            primary_action, capabilities, steps
        )
        
        return ParsedIntent(
            primary_action=primary_action,
            description=cleaned,
            capabilities=capabilities,
            tags=tags,
            steps=steps,
            suggested_name=suggested_name,
            confidence=confidence,
            raw_request=request
        )
    
    def _clean_request(self, request: str) -> str:
        """Clean and normalize the request"""
        # Remove extra whitespace
        cleaned = ' '.join(request.split())
        # Remove common filler words
        filler_words = ['please', 'i want to', 'i need to', 'can you', 
                       'could you', 'help me', 'i would like to']
        for filler in filler_words:
            cleaned = re.sub(rf'\b{filler}\b', '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _extract_primary_action(self, request: str) -> str:
        """Extract the main action from the request"""
        for action, pattern in self._action_regex.items():
            if pattern.search(request):
                # Extract the surrounding context
                match = pattern.search(request)
                start = max(0, match.start() - 20)
                end = min(len(request), match.end() + 50)
                context = request[start:end].strip()
                return context
                
        # If no pattern matches, use first sentence or phrase
        sentences = re.split(r'[.!?]', request)
        return sentences[0].strip() if sentences else request[:50]
    
    def _extract_capabilities(self, request: str) -> List[str]:
        """Extract required capabilities from the request"""
        capabilities = []
        for capability, pattern in self._capability_regex.items():
            if pattern.search(request):
                capabilities.append(capability)
        return capabilities if capabilities else ['general']
    
    def _extract_tags(self, request: str) -> List[str]:
        """Extract categorization tags from the request"""
        tags = []
        for tag, pattern in self._tag_regex.items():
            if pattern.search(request):
                tags.append(tag)
        return tags if tags else ['general']
    
    def _extract_steps(self, request: str) -> List[str]:
        """Break down the request into execution steps"""
        steps = []
        
        # Look for explicit step indicators
        step_patterns = [
            r'first[,:]?\s*(.+?)(?:then|next|after|finally|$)',
            r'then[,:]?\s*(.+?)(?:then|next|after|finally|$)',
            r'next[,:]?\s*(.+?)(?:then|next|after|finally|$)',
            r'finally[,:]?\s*(.+?)(?:$)',
            r'\d+\.\s*(.+?)(?=\d+\.|$)',
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, request, re.IGNORECASE | re.DOTALL)
            for match in matches:
                step = match.strip()
                if step and step not in steps:
                    steps.append(step)
                    
        # If no explicit steps, create based on capabilities
        if not steps:
            steps = self._infer_steps(request)
            
        return steps
    
    def _infer_steps(self, request: str) -> List[str]:
        """Infer steps based on the request content"""
        steps = []
        
        # Check for common action words
        action_words = [
            ('fetch', 'Fetch data'),
            ('get', 'Retrieve information'),
            ('read', 'Read input'),
            ('process', 'Process data'),
            ('transform', 'Transform content'),
            ('analyze', 'Analyze data'),
            ('generate', 'Generate output'),
            ('save', 'Save results'),
            ('send', 'Send output'),
            ('notify', 'Send notification'),
        ]
        
        for word, step_desc in action_words:
            if word in request.lower():
                steps.append(step_desc)
                
        # Add default steps if none found
        if not steps:
            steps = [
                'Initialize flow',
                'Execute main action',
                'Return results'
            ]
            
        return steps
    
    def _generate_name(self, action: str, capabilities: List[str]) -> str:
        """Generate a suggested name for the flow"""
        # Extract key words from action
        words = re.findall(r'\b[a-zA-Z]{3,}\b', action.lower())
        action_words = [w for w in words[:2] if w not in 
                       ['the', 'and', 'for', 'with', 'that', 'this']]
        
        # Combine with first capability
        cap = capabilities[0] if capabilities else 'flow'
        
        if action_words:
            name = f"{action_words[0]}_{cap}"
        else:
            name = f"{cap}_flow"
            
        return name.replace(' ', '_').lower()
    
    def _calculate_confidence(self, action: str, capabilities: List[str],
                             steps: List[str]) -> float:
        """Calculate confidence score for the parsed intent"""
        score = 0.0
        
        # Action clarity (0-40 points)
        if len(action) > 10:
            score += 20
        if len(action) > 30:
            score += 20
            
        # Capabilities identified (0-30 points)
        score += min(len(capabilities) * 10, 30)
        
        # Steps clarity (0-30 points)
        score += min(len(steps) * 10, 30)
        
        return min(score, 100) / 100
    
    def suggest_refinements(self, intent: ParsedIntent) -> List[str]:
        """
        Suggest ways to refine the request for better results.
        """
        suggestions = []
        
        if intent.confidence < 0.5:
            suggestions.append(
                "Try being more specific about what you want to accomplish"
            )
            
        if len(intent.capabilities) == 1 and intent.capabilities[0] == 'general':
            suggestions.append(
                "Mention specific technologies or data types involved"
            )
            
        if len(intent.steps) <= 1:
            suggestions.append(
                "Consider breaking down the task into clear steps"
            )
            
        return suggestions
