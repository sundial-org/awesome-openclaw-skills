"""
Chunking strategies for splitting documents into embeddable pieces.

Unlike summarization (which condenses), chunking splits mechanically
by token count with overlap to preserve context across boundaries.
"""

from dataclasses import dataclass
from typing import Protocol, Iterator
import re


@dataclass(frozen=True)
class Chunk:
    """A piece of a document suitable for embedding."""
    text: str
    start_char: int
    end_char: int
    index: int  # 0-based chunk number within document
    
    @property
    def char_span(self) -> tuple[int, int]:
        return (self.start_char, self.end_char)


class ChunkingProvider(Protocol):
    """Protocol for document chunking strategies."""
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split text into overlapping chunks."""
        ...
    
    @property
    def target_tokens(self) -> int:
        """Target token count per chunk."""
        ...
    
    @property
    def overlap_tokens(self) -> int:
        """Overlap between adjacent chunks."""
        ...


class TokenChunker:
    """
    Chunk by approximate token count with overlap.
    
    Uses whitespace splitting as a rough token approximation
    (1 token ≈ 0.75 words for English). For precise tokenization,
    subclass and override _tokenize/_detokenize.
    
    OpenClaw defaults: target=400 tokens, overlap=80 tokens
    """
    
    def __init__(
        self,
        target_tokens: int = 400,
        overlap_tokens: int = 80,
        chars_per_token: float = 4.0,  # rough estimate
    ):
        self._target_tokens = target_tokens
        self._overlap_tokens = overlap_tokens
        self._chars_per_token = chars_per_token
        
    @property
    def target_tokens(self) -> int:
        return self._target_tokens
    
    @property
    def overlap_tokens(self) -> int:
        return self._overlap_tokens
    
    @property
    def target_chars(self) -> int:
        return int(self._target_tokens * self._chars_per_token)
    
    @property
    def overlap_chars(self) -> int:
        return int(self._overlap_tokens * self._chars_per_token)
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return
            
        # For short texts, return as single chunk
        if len(text) <= self.target_chars:
            yield Chunk(text=text, start_char=0, end_char=len(text), index=0)
            return
        
        stride = self.target_chars - self.overlap_chars
        start = 0
        index = 0
        
        while start < len(text):
            end = min(start + self.target_chars, len(text))
            
            # Try to break at word boundary
            if end < len(text):
                # Look for whitespace near the end
                break_point = self._find_break_point(text, end)
                if break_point > start:
                    end = break_point
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                yield Chunk(
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                    index=index,
                )
                index += 1
            
            # Move forward by stride, not by chunk length
            start += stride
            
            # Ensure progress even if stride is weird
            if start <= 0:
                start = end
    
    def _find_break_point(self, text: str, target: int, window: int = 50) -> int:
        """Find a good break point (whitespace) near target position."""
        # Search backwards from target for whitespace
        search_start = max(0, target - window)
        search_region = text[search_start:target]
        
        # Find last whitespace in region
        match = None
        for m in re.finditer(r'\s+', search_region):
            match = m
        
        if match:
            return search_start + match.end()
        return target


class SentenceChunker(TokenChunker):
    """
    Chunk by sentences, respecting token limits.
    
    Tries to keep sentences intact while staying under token limit.
    Falls back to mid-sentence breaks for very long sentences.
    """
    
    # Simple sentence boundary pattern
    SENTENCE_END = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split into sentence-aligned chunks."""
        if not text.strip():
            return
            
        if len(text) <= self.target_chars:
            yield Chunk(text=text, start_char=0, end_char=len(text), index=0)
            return
        
        sentences = self.SENTENCE_END.split(text)
        
        current_chunk = []
        current_len = 0
        chunk_start = 0
        char_pos = 0
        index = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If single sentence exceeds limit, fall back to token chunking
            if sentence_len > self.target_chars:
                # Flush current chunk first
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    yield Chunk(
                        text=chunk_text,
                        start_char=chunk_start,
                        end_char=char_pos,
                        index=index,
                    )
                    index += 1
                    current_chunk = []
                    current_len = 0
                
                # Chunk the long sentence
                for sub_chunk in super().chunk(sentence):
                    yield Chunk(
                        text=sub_chunk.text,
                        start_char=char_pos + sub_chunk.start_char,
                        end_char=char_pos + sub_chunk.end_char,
                        index=index,
                    )
                    index += 1
                
                char_pos += sentence_len + 1  # +1 for space
                chunk_start = char_pos
                continue
            
            # Would adding this sentence exceed limit?
            if current_len + sentence_len + 1 > self.target_chars and current_chunk:
                # Emit current chunk
                chunk_text = ' '.join(current_chunk)
                yield Chunk(
                    text=chunk_text,
                    start_char=chunk_start,
                    end_char=char_pos,
                    index=index,
                )
                index += 1
                
                # Start new chunk with overlap
                # Keep last sentence(s) up to overlap size
                overlap_sents = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) > self.overlap_chars:
                        break
                    overlap_sents.insert(0, s)
                    overlap_len += len(s) + 1
                
                current_chunk = overlap_sents
                current_len = overlap_len
                chunk_start = char_pos - overlap_len
            
            current_chunk.append(sentence)
            current_len += sentence_len + 1
            char_pos += sentence_len + 1
        
        # Emit final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            yield Chunk(
                text=chunk_text,
                start_char=chunk_start,
                end_char=len(text),
                index=index,
            )


class MarkdownChunker(TokenChunker):
    """
    Chunk Markdown documents respecting structure.
    
    Tries to break at:
    1. Heading boundaries (# ## ###)
    2. Paragraph boundaries (blank lines)
    3. Sentence boundaries
    4. Word boundaries (fallback)
    """
    
    HEADING = re.compile(r'^#{1,6}\s+', re.MULTILINE)
    PARAGRAPH = re.compile(r'\n\n+')
    
    def chunk(self, text: str) -> Iterator[Chunk]:
        """Split Markdown into structure-aware chunks."""
        if not text.strip():
            return
            
        if len(text) <= self.target_chars:
            yield Chunk(text=text, start_char=0, end_char=len(text), index=0)
            return
        
        # Split on headings first
        sections = []
        last_end = 0
        
        for match in self.HEADING.finditer(text):
            if match.start() > last_end:
                sections.append((last_end, match.start()))
            last_end = match.start()
        
        if last_end < len(text):
            sections.append((last_end, len(text)))
        
        # If no headings, fall back to paragraph splitting
        if len(sections) <= 1:
            yield from self._chunk_by_paragraphs(text)
            return
        
        index = 0
        for start, end in sections:
            section_text = text[start:end]
            
            if len(section_text) <= self.target_chars:
                if section_text.strip():
                    yield Chunk(
                        text=section_text.strip(),
                        start_char=start,
                        end_char=end,
                        index=index,
                    )
                    index += 1
            else:
                # Section too long, chunk it
                for sub in self._chunk_by_paragraphs(section_text):
                    yield Chunk(
                        text=sub.text,
                        start_char=start + sub.start_char,
                        end_char=start + sub.end_char,
                        index=index,
                    )
                    index += 1
    
    def _chunk_by_paragraphs(self, text: str) -> Iterator[Chunk]:
        """Fall back to paragraph-based chunking."""
        paragraphs = self.PARAGRAPH.split(text)
        
        current_chunk = []
        current_len = 0
        chunk_start = 0
        char_pos = 0
        index = 0
        
        for para in paragraphs:
            para_len = len(para)
            
            if para_len > self.target_chars:
                # Flush and chunk the long paragraph
                if current_chunk:
                    yield Chunk(
                        text='\n\n'.join(current_chunk),
                        start_char=chunk_start,
                        end_char=char_pos,
                        index=index,
                    )
                    index += 1
                    current_chunk = []
                    current_len = 0
                
                for sub in super().chunk(para):
                    yield Chunk(
                        text=sub.text,
                        start_char=char_pos + sub.start_char,
                        end_char=char_pos + sub.end_char,
                        index=index,
                    )
                    index += 1
                
                char_pos += para_len + 2
                chunk_start = char_pos
                continue
            
            if current_len + para_len + 2 > self.target_chars and current_chunk:
                yield Chunk(
                    text='\n\n'.join(current_chunk),
                    start_char=chunk_start,
                    end_char=char_pos,
                    index=index,
                )
                index += 1
                current_chunk = []
                current_len = 0
                chunk_start = char_pos
            
            current_chunk.append(para)
            current_len += para_len + 2
            char_pos += para_len + 2
        
        if current_chunk:
            yield Chunk(
                text='\n\n'.join(current_chunk),
                start_char=chunk_start,
                end_char=len(text),
                index=index,
            )
