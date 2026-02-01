"""
Default tagging providers - lightweight, zero/minimal dependencies.

These taggers provide basic domain identification without requiring
heavy ML models or API keys. They're useful as fallbacks and for
bootstrapping before more sophisticated tagging is enabled.
"""

import re
from typing import Any

from .base import TaggingProvider, get_registry


# -----------------------------------------------------------------------------
# Domain Taxonomy
# -----------------------------------------------------------------------------

# Pragmatic domains for knowledge work, inspired by DDC but modernized.
# Each domain has keywords that strongly suggest that domain.

DOMAINS = {
    "technology": {
        "keywords": [
            "software", "hardware", "computer", "programming", "code", "api",
            "database", "server", "cloud", "network", "algorithm", "data structure",
            "machine learning", "ai", "artificial intelligence", "devops",
            "kubernetes", "docker", "linux", "windows", "macos", "mobile",
            "web", "frontend", "backend", "fullstack", "security", "encryption",
        ],
        "extensions": [".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".h"],
    },
    "science": {
        "keywords": [
            "research", "experiment", "hypothesis", "data", "analysis",
            "biology", "chemistry", "physics", "mathematics", "statistics",
            "scientific", "laboratory", "study", "findings", "methodology",
            "peer review", "journal", "citation", "theory", "model",
        ],
        "extensions": [".r", ".jl", ".ipynb"],
    },
    "business": {
        "keywords": [
            "business", "company", "startup", "enterprise", "market",
            "revenue", "profit", "customer", "client", "sales", "marketing",
            "strategy", "management", "leadership", "organization", "team",
            "investor", "funding", "growth", "product", "service",
            "quarterly", "annual", "fiscal", "roi", "kpi",
        ],
        "extensions": [".xlsx", ".csv"],
    },
    "finance": {
        "keywords": [
            "finance", "financial", "investment", "stock", "bond", "equity",
            "portfolio", "asset", "liability", "balance sheet", "income statement",
            "cash flow", "dividend", "interest rate", "mortgage", "loan",
            "credit", "debit", "accounting", "audit", "tax", "budget",
        ],
        "extensions": [],
    },
    "legal": {
        "keywords": [
            "legal", "law", "contract", "agreement", "liability", "compliance",
            "regulation", "statute", "court", "judge", "attorney", "lawyer",
            "plaintiff", "defendant", "jurisdiction", "intellectual property",
            "patent", "trademark", "copyright", "license", "terms of service",
            "privacy policy", "gdpr", "hipaa",
        ],
        "extensions": [],
    },
    "health": {
        "keywords": [
            "health", "medical", "medicine", "doctor", "patient", "diagnosis",
            "treatment", "symptom", "disease", "condition", "therapy",
            "hospital", "clinic", "pharmaceutical", "drug", "prescription",
            "wellness", "fitness", "nutrition", "mental health", "psychology",
        ],
        "extensions": [],
    },
    "education": {
        "keywords": [
            "education", "learning", "teaching", "student", "teacher",
            "curriculum", "course", "lecture", "tutorial", "training",
            "school", "university", "college", "degree", "certification",
            "exam", "assignment", "homework", "syllabus", "pedagogy",
        ],
        "extensions": [],
    },
    "arts": {
        "keywords": [
            "art", "music", "literature", "poetry", "fiction", "novel",
            "painting", "sculpture", "photography", "film", "cinema",
            "theater", "dance", "creative", "design", "aesthetic",
            "culture", "history", "philosophy", "religion", "spirituality",
        ],
        "extensions": [],
    },
    "personal": {
        "keywords": [
            "personal", "diary", "journal", "reflection", "goal", "habit",
            "relationship", "family", "friend", "emotion", "feeling",
            "gratitude", "meditation", "mindfulness", "self-improvement",
            "life", "death", "meaning", "purpose", "identity",
        ],
        "extensions": [],
    },
    "communication": {
        "keywords": [
            "email", "message", "chat", "conversation", "meeting", "call",
            "presentation", "report", "memo", "announcement", "newsletter",
            "feedback", "review", "comment", "discussion", "collaboration",
        ],
        "extensions": [],
    },
}

# Content type detection patterns
CONTENT_TYPES = {
    "code": {
        "patterns": [
            r"^\s*(def|class|function|import|from|const|let|var|public|private)\s",
            r"^\s*(if|else|for|while|return|try|catch|except)\s*[\(\{:]",
            r"[{};]\s*$",
            r"self\.",  # Python
            r"this\.",  # JavaScript/Java
        ],
        "extensions": [".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".rb"],
    },
    "documentation": {
        "patterns": [
            r"^#\s+",  # Markdown headers
            r"^\*\*[^*]+\*\*",  # Bold text
            r"^>\s+",  # Blockquotes
            r"\[.+\]\(.+\)",  # Links
        ],
        "extensions": [".md", ".rst", ".txt", ".adoc"],
    },
    "configuration": {
        "patterns": [
            r"^\[.+\]\s*$",  # INI/TOML sections
            r"^[a-z_]+\s*[:=]\s*",  # Key-value pairs
        ],
        "extensions": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"],
    },
    "data": {
        "patterns": [
            r"^\s*\{[\s\S]*\"[^\"]+\":", # JSON object with string keys
            r"^[^,\n]+,[^,\n]+,[^,\n]+$",  # CSV-like (3+ columns)
        ],
        "extensions": [".json", ".csv", ".xml", ".parquet"],
    },
}

# Language detection for code
LANGUAGE_PATTERNS = {
    "python": [r"^\s*(def|class)\s+\w+", r"self\.", r"__\w+__", r":\s*$"],
    "javascript": [r"^\s*(const|let|var|function)\s", r"=>\s*[{\(]", r"require\(", r"export\s"],
    "typescript": [r":\s*(string|number|boolean|any)\s*[;=]", r"interface\s+\w+", r"<[A-Z]\w*>"],
    "rust": [r"^\s*(fn|let|mut|impl|struct|enum)\s", r"->\s*\w+", r"&mut\s", r"unwrap\(\)"],
    "go": [r"^\s*(func|package|import)\s", r":=\s*", r"go\s+\w+\(", r"defer\s"],
    "java": [r"^\s*(public|private|protected)\s+(class|void|static)", r"System\.out"],
    "sql": [r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s", r"\bFROM\b", r"\bWHERE\b"],
}


class KeywordTagger:
    """
    Lightweight tagger using keyword matching and patterns.
    
    Zero ML dependencies - uses simple heuristics for fast domain
    identification. Good as a default fallback or for bootstrapping.
    
    Detected tags:
    - domain: Primary knowledge domain (technology, science, business, etc.)
    - content_type: Type of content (code, documentation, configuration, data)
    - language: Programming language if code is detected
    """
    
    def __init__(self, threshold: float = 0.1):
        """
        Args:
            threshold: Minimum keyword density to assign a domain (0-1)
        """
        self.threshold = threshold
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._content_type_patterns = {
            ct: [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in info["patterns"]]
            for ct, info in CONTENT_TYPES.items()
        }
        self._language_patterns = {
            lang: [re.compile(p, re.MULTILINE) for p in patterns]
            for lang, patterns in LANGUAGE_PATTERNS.items()
        }
    
    def _detect_domain(self, text: str) -> str | None:
        """Detect primary knowledge domain from content."""
        text_lower = text.lower()
        word_count = len(text_lower.split())
        
        if word_count < 10:
            return None
        
        scores = {}
        for domain, info in DOMAINS.items():
            matches = sum(1 for kw in info["keywords"] if kw in text_lower)
            # Normalize by keyword count and text length
            density = matches / (len(info["keywords"]) * 0.5 + word_count * 0.01)
            if density > self.threshold:
                scores[domain] = density
        
        if not scores:
            return None
        
        return max(scores, key=scores.get)
    
    def _detect_content_type(self, text: str, content_type_hint: str | None = None) -> str | None:
        """Detect content type from patterns and structure."""
        # Use hint from file extension if available
        if content_type_hint:
            for ct, info in CONTENT_TYPES.items():
                if any(content_type_hint.endswith(ext) for ext in info.get("extensions", [])):
                    return ct
        
        # Fall back to pattern matching
        scores = {}
        for ct, patterns in self._content_type_patterns.items():
            matches = sum(1 for p in patterns if p.search(text))
            if matches > 0:
                scores[ct] = matches / len(patterns)
        
        if not scores:
            return None
        
        return max(scores, key=scores.get)
    
    def _detect_language(self, text: str) -> str | None:
        """Detect programming language if content is code."""
        scores = {}
        for lang, patterns in self._language_patterns.items():
            matches = sum(1 for p in patterns if p.search(text))
            if matches >= 2:  # Require at least 2 pattern matches
                scores[lang] = matches
        
        if not scores:
            return None
        
        return max(scores, key=scores.get)
    
    def tag(self, content: str, *, content_type_hint: str | None = None) -> dict[str, str]:
        """
        Generate tags for content.
        
        Args:
            content: Text content to analyze
            content_type_hint: Optional hint (e.g., file extension or MIME type)
            
        Returns:
            Dict of generated tags
        """
        tags = {}
        
        # Detect domain
        domain = self._detect_domain(content)
        if domain:
            tags["domain"] = domain
        
        # Detect content type
        content_type = self._detect_content_type(content, content_type_hint)
        if content_type:
            tags["content_type"] = content_type
        
        # Detect programming language (if code)
        if content_type == "code" or (content_type_hint and any(
            content_type_hint.endswith(ext) 
            for ext in CONTENT_TYPES.get("code", {}).get("extensions", [])
        )):
            language = self._detect_language(content)
            if language:
                tags["language"] = language
        
        return tags


class EmbeddingDomainTagger:
    """
    Domain tagger using embedding similarity.
    
    Compares document embeddings against pre-computed domain exemplar
    embeddings. Reuses the embedding provider — no extra model needed.
    
    More accurate than keyword matching, especially for nuanced content.
    """
    
    # Domain descriptions used to generate exemplar embeddings
    DOMAIN_DESCRIPTIONS = {
        "technology": "Software development, programming, computer systems, APIs, databases, cloud computing, DevOps, machine learning, artificial intelligence, web development, mobile apps, cybersecurity",
        "science": "Scientific research, experiments, hypotheses, data analysis, biology, chemistry, physics, mathematics, peer-reviewed studies, laboratory work, academic journals",
        "business": "Business strategy, management, marketing, sales, startups, entrepreneurship, corporate operations, team leadership, product development, customer relations",
        "finance": "Financial markets, investments, stocks, bonds, banking, accounting, budgeting, portfolio management, economic analysis, taxation",
        "legal": "Law, contracts, regulations, compliance, intellectual property, litigation, legal agreements, privacy policies, terms of service",
        "health": "Healthcare, medicine, medical diagnosis, treatment, pharmaceuticals, mental health, wellness, nutrition, fitness, patient care",
        "education": "Learning, teaching, curriculum, courses, training, academic programs, student education, pedagogy, tutorials, certifications",
        "arts": "Art, music, literature, creative writing, film, theater, design, culture, philosophy, history, humanities",
        "personal": "Personal reflections, journaling, goals, habits, relationships, emotions, self-improvement, life experiences, mindfulness",
        "communication": "Emails, messages, meetings, presentations, reports, discussions, feedback, collaboration, announcements",
    }
    
    def __init__(self, embedding_provider: Any, threshold: float = 0.5):
        """
        Args:
            embedding_provider: Provider implementing EmbeddingProvider protocol
            threshold: Minimum similarity score to assign a domain (0-1)
        """
        self._embedder = embedding_provider
        self._threshold = threshold
        self._domain_embeddings: dict[str, list[float]] | None = None
    
    def _ensure_domain_embeddings(self):
        """Lazily compute domain exemplar embeddings."""
        if self._domain_embeddings is not None:
            return
        
        self._domain_embeddings = {}
        for domain, description in self.DOMAIN_DESCRIPTIONS.items():
            self._domain_embeddings[domain] = self._embedder.embed(description)
    
    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def tag(self, content: str, *, content_embedding: list[float] | None = None) -> dict[str, str]:
        """
        Generate domain tags using embedding similarity.
        
        Args:
            content: Text content (used if embedding not provided)
            content_embedding: Pre-computed embedding (optional, for efficiency)
            
        Returns:
            Dict with 'domain' tag if above threshold
        """
        self._ensure_domain_embeddings()
        
        # Get content embedding
        if content_embedding is None:
            content_embedding = self._embedder.embed(content)
        
        # Compare against all domains
        scores = {}
        for domain, domain_embedding in self._domain_embeddings.items():
            similarity = self._cosine_similarity(content_embedding, domain_embedding)
            if similarity >= self._threshold:
                scores[domain] = similarity
        
        if not scores:
            return {}
        
        # Return top domain
        best_domain = max(scores, key=scores.get)
        return {"domain": best_domain}


class PassthroughTagger:
    """
    No-op tagger that returns empty tags.
    
    Useful as a placeholder or when tagging is disabled.
    """
    
    def tag(self, content: str) -> dict[str, str]:
        """Return empty tags."""
        return {}


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

_registry = get_registry()
_registry.register_tagging("keyword", KeywordTagger)
_registry.register_tagging("none", PassthroughTagger)
# Note: EmbeddingDomainTagger requires an embedding provider, so it's 
# instantiated manually in AssociativeMemory rather than via registry
