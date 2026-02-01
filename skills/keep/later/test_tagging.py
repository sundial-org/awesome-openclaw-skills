"""
Tests for tagging providers.
"""

import pytest

from keep.providers.tagging import (
    KeywordTagger,
    EmbeddingDomainTagger,
    PassthroughTagger,
    DOMAINS,
)


# -----------------------------------------------------------------------------
# KeywordTagger Tests
# -----------------------------------------------------------------------------

class TestKeywordTagger:
    """Tests for keyword-based tagger."""
    
    @pytest.fixture
    def tagger(self):
        return KeywordTagger()
    
    def test_detects_technology_domain(self, tagger):
        """Technology content is detected."""
        content = """
        This Python module provides an API for managing database connections.
        It uses connection pooling for better performance with the server.
        The code implements secure encryption for all network traffic.
        """
        tags = tagger.tag(content)
        assert tags.get("domain") == "technology"
    
    def test_detects_business_domain(self, tagger):
        """Business content is detected."""
        content = """
        Our company's quarterly revenue exceeded expectations, driven by
        strong customer acquisition and improved sales team performance.
        The marketing strategy focused on enterprise clients resulted in
        significant growth in our B2B segment.
        """
        tags = tagger.tag(content)
        assert tags.get("domain") == "business"
    
    def test_detects_health_domain(self, tagger):
        """Health/medical content is detected."""
        content = """
        The patient presented with symptoms of fatigue and mild fever.
        After diagnosis, the doctor recommended a treatment plan including
        medication and therapy sessions. The hospital scheduled follow-up
        appointments to monitor the condition.
        """
        tags = tagger.tag(content)
        assert tags.get("domain") == "health"
    
    def test_detects_code_content_type(self, tagger):
        """Code is detected from patterns."""
        content = """
        def calculate_total(items):
            total = 0
            for item in items:
                if item.price > 0:
                    total += item.price
            return total
        """
        tags = tagger.tag(content)
        assert tags.get("content_type") == "code"
    
    def test_detects_python_language(self, tagger):
        """Python code is identified."""
        content = """
        class UserManager:
            def __init__(self, db):
                self.db = db
            
            def get_user(self, user_id):
                return self.db.query(User).filter_by(id=user_id).first()
        """
        tags = tagger.tag(content)
        assert tags.get("language") == "python"
    
    def test_detects_javascript_language(self, tagger):
        """JavaScript code is identified."""
        content = """
        const fetchUsers = async () => {
            const response = await fetch('/api/users');
            const data = await response.json();
            return data;
        };
        
        export default fetchUsers;
        """
        tags = tagger.tag(content)
        assert tags.get("language") == "javascript"
    
    def test_detects_documentation_content_type(self, tagger):
        """Markdown documentation is detected."""
        content = """
        # Installation Guide
        
        This guide explains how to install the package.
        
        ## Prerequisites
        
        **Important:** Make sure you have Python 3.8+ installed.
        
        > Note: This is a development version.
        
        See the [documentation](https://docs.example.com) for more info.
        """
        tags = tagger.tag(content)
        assert tags.get("content_type") == "documentation"
    
    def test_content_type_hint_from_extension(self, tagger):
        """File extension hint influences content type detection."""
        content = "minimal content"
        tags = tagger.tag(content, content_type_hint=".py")
        assert tags.get("content_type") == "code"
    
    def test_short_content_no_domain(self, tagger):
        """Very short content doesn't get domain assigned."""
        tags = tagger.tag("hello world")
        assert "domain" not in tags
    
    def test_empty_content(self, tagger):
        """Empty content returns empty tags."""
        tags = tagger.tag("")
        assert tags == {}


# -----------------------------------------------------------------------------
# EmbeddingDomainTagger Tests
# -----------------------------------------------------------------------------

class MockEmbedder:
    """Mock embedding provider for testing."""
    
    def __init__(self, dimension: int = 4):
        self._dimension = dimension
        # Simple: hash-based embeddings for deterministic testing
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def embed(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-embedding from text hash."""
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        # Convert first N bytes to floats in [-1, 1]
        return [(b / 127.5 - 1.0) for b in h[:self._dimension]]


class TestEmbeddingDomainTagger:
    """Tests for embedding-based domain tagger."""
    
    @pytest.fixture
    def embedder(self):
        return MockEmbedder(dimension=16)
    
    @pytest.fixture
    def tagger(self, embedder):
        return EmbeddingDomainTagger(embedder, threshold=0.3)
    
    def test_instantiation(self, tagger):
        """Tagger can be instantiated."""
        assert tagger is not None
    
    def test_tag_returns_dict(self, tagger):
        """Tagging returns a dictionary."""
        result = tagger.tag("Some content about programming and code")
        assert isinstance(result, dict)
    
    def test_cosine_similarity_identical(self, tagger):
        """Identical vectors have similarity 1.0."""
        vec = [0.1, 0.2, 0.3, 0.4]
        sim = tagger._cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 0.001
    
    def test_cosine_similarity_orthogonal(self, tagger):
        """Orthogonal vectors have similarity 0.0."""
        a = [1.0, 0.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0, 0.0]
        sim = tagger._cosine_similarity(a, b)
        assert abs(sim) < 0.001
    
    def test_uses_precomputed_embedding(self, embedder, tagger):
        """Can pass pre-computed embedding for efficiency."""
        content = "Test content"
        embedding = embedder.embed(content)
        
        # Should not error when embedding is provided
        tags = tagger.tag(content, content_embedding=embedding)
        assert isinstance(tags, dict)


# -----------------------------------------------------------------------------
# PassthroughTagger Tests
# -----------------------------------------------------------------------------

class TestPassthroughTagger:
    """Tests for no-op tagger."""
    
    def test_returns_empty_dict(self):
        """Passthrough returns empty tags."""
        tagger = PassthroughTagger()
        assert tagger.tag("anything") == {}


# -----------------------------------------------------------------------------
# Domain Taxonomy Tests
# -----------------------------------------------------------------------------

class TestDomainTaxonomy:
    """Tests for the domain taxonomy structure."""
    
    def test_all_domains_have_keywords(self):
        """Every domain has keywords defined."""
        for domain, info in DOMAINS.items():
            assert "keywords" in info, f"{domain} missing keywords"
            assert len(info["keywords"]) > 0, f"{domain} has empty keywords"
    
    def test_domains_cover_common_areas(self):
        """Key knowledge domains are represented."""
        expected = {"technology", "science", "business", "health", "education"}
        actual = set(DOMAINS.keys())
        assert expected.issubset(actual)
    
    def test_keywords_are_lowercase(self):
        """All keywords are lowercase for matching."""
        for domain, info in DOMAINS.items():
            for kw in info["keywords"]:
                assert kw == kw.lower(), f"{domain}: '{kw}' should be lowercase"
