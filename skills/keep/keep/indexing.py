"""
Indexing modes for controlling embedding granularity.

Summarization ALWAYS happens (it's cheap and aids retrieval).
The mode controls what gets embedded:

- DOCUMENT: Embed summary only (1 vector per doc, fast)
- CHUNKED: Embed chunks only (N vectors per doc, OpenClaw-compatible)  
- HYBRID: Embed summary + chunks (best recall, more storage)
- BM25_ONLY: Fulltext index only (no embeddings, keyword search)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Protocol


class IndexingMode(Enum):
    """Controls embedding granularity. Summary is always stored."""
    
    DOCUMENT = "document"
    """
    Embed summary only.
    - One vector per document
    - Fast, good for "what is this document about?"
    - Summary always available for display
    """
    
    CHUNKED = "chunked"
    """
    Embed chunks only.
    - N vectors per document (one per ~400-token chunk)
    - OpenClaw-compatible mode
    - Good for passage-level retrieval
    - Summary stored but not embedded
    """
    
    HYBRID = "hybrid"
    """
    Embed summary AND chunks.
    - 1+N vectors per document
    - Best recall (semantic anchor + passage-level)
    - More storage, more embedding calls
    """
    
    BM25_ONLY = "bm25_only"
    """
    Fulltext index only.
    - No embeddings at all
    - Summary stored for display
    - Keyword search only (exact token matching)
    - Fastest, minimal resource usage
    """


@dataclass
class IndexingConfig:
    """Configuration for the indexing pipeline."""
    
    mode: IndexingMode = IndexingMode.DOCUMENT
    """Which embedding strategy to use. Summary always stored."""
    
    # Chunking settings (for CHUNKED/HYBRID modes)
    chunk_target_tokens: int = 400
    """Target tokens per chunk (OpenClaw default: 400)."""
    
    chunk_overlap_tokens: int = 80
    """Overlap between chunks (OpenClaw default: 80)."""
    
    tokens_per_word: float = 1.3
    """Approximation for token estimation."""
    
    # Summarization settings (always used)
    summary_max_chars: int = 500
    """Maximum summary length in characters."""
    
    # BM25 settings
    enable_fulltext: bool = True
    """Whether to build FTS index alongside vectors."""
    
    # Hybrid search weights (vector + BM25)
    vector_weight: float = 0.7
    """Weight for vector similarity in hybrid search."""
    
    text_weight: float = 0.3
    """Weight for BM25 score in hybrid search."""
    
    @classmethod
    def document_mode(cls) -> "IndexingConfig":
        """Fast: embed summary only."""
        return cls(mode=IndexingMode.DOCUMENT)
    
    @classmethod
    def chunked_mode(cls) -> "IndexingConfig":
        """OpenClaw-compatible: embed chunks."""
        return cls(
            mode=IndexingMode.CHUNKED,
            chunk_target_tokens=400,
            chunk_overlap_tokens=80,
            enable_fulltext=True,
            vector_weight=0.7,
            text_weight=0.3,
        )
    
    @classmethod
    def hybrid_mode(cls) -> "IndexingConfig":
        """Best recall: embed summary + chunks."""
        return cls(
            mode=IndexingMode.HYBRID,
            chunk_target_tokens=400,
            chunk_overlap_tokens=80,
        )
    
    @classmethod
    def bm25_only(cls) -> "IndexingConfig":
        """Fastest: no embeddings, keyword search only."""
        return cls(
            mode=IndexingMode.BM25_ONLY,
            enable_fulltext=True,
        )
    
    def __post_init__(self):
        # Normalize weights
        total = self.vector_weight + self.text_weight
        if total > 0:
            self.vector_weight = self.vector_weight / total
            self.text_weight = self.text_weight / total


# --- Chunking ---

@dataclass(frozen=True)
class Chunk:
    """A chunk of text with position info."""
    text: str
    start_char: int
    end_char: int
    index: int  # 0-based chunk number


class Chunker(Protocol):
    """Protocol for text chunking strategies."""
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split text into overlapping chunks."""
        ...


@dataclass
class TokenChunker:
    """Chunk by approximate token count with overlap.
    
    OpenClaw defaults: ~400 tokens target, 80 token overlap.
    """
    target_tokens: int = 400
    overlap_tokens: int = 80
    tokens_per_word: float = 1.3
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split text into overlapping chunks by token estimate."""
        if not text.strip():
            return
        
        words = text.split()
        if not words:
            return
            
        target_words = int(self.target_tokens / self.tokens_per_word)
        overlap_words = int(self.overlap_tokens / self.tokens_per_word)
        step_words = max(1, target_words - overlap_words)
        
        # Track character positions
        word_positions: list[tuple[int, int]] = []
        pos = 0
        for word in words:
            start = text.find(word, pos)
            end = start + len(word)
            word_positions.append((start, end))
            pos = end
        
        chunk_index = 0
        word_index = 0
        
        while word_index < len(words):
            end_word = min(word_index + target_words, len(words))
            chunk_words = words[word_index:end_word]
            
            start_char = word_positions[word_index][0]
            end_char = word_positions[end_word - 1][1]
            
            yield Chunk(
                text=" ".join(chunk_words),
                start_char=start_char,
                end_char=end_char,
                index=chunk_index,
            )
            
            chunk_index += 1
            word_index += step_words
            
            # Don't create tiny final chunks
            if word_index < len(words) and len(words) - word_index < overlap_words:
                break


def estimate_tokens(text: str, tokens_per_word: float = 1.3) -> int:
    """Estimate token count from text."""
    return int(len(text.split()) * tokens_per_word)
