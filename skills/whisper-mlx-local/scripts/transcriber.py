#!/usr/bin/env python3
"""
Transcription Module for Clawdbot
Based on MLX Whisper examples

Supports multiple backends:
- MLX (Apple Silicon) - fastest local option
- OpenAI Whisper API - cloud
- Groq API - fast & cheap cloud
- Local faster-whisper - CPU-based local
"""

import logging
import os
import platform
import time
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Check if running on Apple Silicon
IS_APPLE_SILICON = platform.system() == "Darwin" and platform.machine() == "arm64"

# Load environment variables
load_dotenv()

# Try to import OpenAI
try:
    from openai import OpenAI, OpenAIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.debug("OpenAI package not available")

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.debug("Groq package not available")

# Try to import faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.debug("faster-whisper not available")

# Try to import lightning-whisper-mlx (Apple Silicon only)
MLX_AVAILABLE = False
if IS_APPLE_SILICON:
    try:
        from lightning_whisper_mlx import LightningWhisperMLX
        MLX_AVAILABLE = True
    except ImportError:
        logger.debug("lightning-whisper-mlx not available")


class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass


class Transcriber:
    """
    Transcribes audio files to text using various backends.
    
    Backends:
    - mlx: Lightning Whisper MLX (Apple Silicon, fastest)
    - openai: OpenAI Whisper API
    - groq: Groq Whisper API
    - local: faster-whisper (CPU)
    """

    MLX_MODEL_MAP = {
        'tiny': 'tiny',
        'base': 'base',
        'small': 'small',
        'medium': 'medium',
        'large': 'large-v3',
        'large-v3': 'large-v3',
        'turbo': 'distil-large-v3',
        'distil-large-v3': 'distil-large-v3',
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        backend: str = "auto",
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30,
        translation_mode: bool = False
    ):
        """
        Initialize transcriber.

        Args:
            api_key: API key (reads from env if None)
            backend: 'auto', 'mlx', 'openai', 'groq', or 'local'
            model: Model name (auto-selected if None)
            max_retries: Retry attempts for API backends
            timeout: Request timeout in seconds
            translation_mode: Translate to English instead of transcribe
        """
        # Auto-select backend
        if backend == "auto":
            if MLX_AVAILABLE:
                backend = "mlx"
            elif OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                backend = "openai"
            elif GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
                backend = "groq"
            elif FASTER_WHISPER_AVAILABLE:
                backend = "local"
            else:
                raise ValueError("No transcription backend available. Install dependencies.")
        
        self.backend = backend.lower()
        self.translation_mode = translation_mode
        self.max_retries = max_retries
        self.timeout = timeout

        # Validate backend
        valid_backends = ['openai', 'groq', 'local', 'mlx']
        if self.backend not in valid_backends:
            raise ValueError(f"Invalid backend: {backend}. Choose from: {valid_backends}")

        # Translation mode not supported on Groq
        if self.translation_mode and self.backend == 'groq':
            raise ValueError("Translation mode not supported with Groq. Use OpenAI or local.")

        # Check availability
        if self.backend == 'mlx' and not MLX_AVAILABLE:
            if not IS_APPLE_SILICON:
                raise ValueError("MLX backend requires Apple Silicon")
            raise ValueError("MLX not available. Install: pip install lightning-whisper-mlx")
        
        if self.backend == 'openai' and not OPENAI_AVAILABLE:
            raise ValueError("OpenAI not available. Install: pip install openai")
        
        if self.backend == 'groq' and not GROQ_AVAILABLE:
            raise ValueError("Groq not available. Install: pip install groq")
        
        if self.backend == 'local' and not FASTER_WHISPER_AVAILABLE:
            raise ValueError("faster-whisper not available. Install: pip install faster-whisper")

        # Initialize backend
        self._init_backend(api_key, model)
        
        mode_str = "translation" if self.translation_mode else "transcription"
        logger.info(f"Transcriber ready: backend={self.backend}, model={self.model}, mode={mode_str}")

    def _init_backend(self, api_key: Optional[str], model: Optional[str]):
        """Initialize the selected backend."""
        
        if self.backend == 'mlx':
            model_name = model or os.getenv('CLAWD_WHISPER_MODEL', 'distil-large-v3')
            self.model = self.MLX_MODEL_MAP.get(model_name, 'distil-large-v3')
            self.api_key = None
            logger.info(f"Loading MLX model: {self.model}")
            self.client = LightningWhisperMLX(
                model=self.model,
                batch_size=12,
                quant=None
            )
            logger.info("MLX model loaded")
            
        elif self.backend == 'local':
            self.model = model or os.getenv('CLAWD_WHISPER_MODEL', 'base')
            self.api_key = None
            logger.info(f"Loading local model: {self.model}")
            self.client = WhisperModel(self.model, device='cpu', compute_type='int8')
            logger.info("Local model loaded")
            
        elif self.backend == 'openai':
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            self.model = model or "whisper-1"
            if not self.api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY.")
            self.client = OpenAI(api_key=self.api_key)
            
        elif self.backend == 'groq':
            self.api_key = api_key or os.getenv('GROQ_API_KEY')
            self.model = model or "whisper-large-v3-turbo"
            if not self.api_key:
                raise ValueError("Groq API key required. Set GROQ_API_KEY.")
            self.client = Groq(api_key=self.api_key)

    def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file
            language: ISO-639-1 language code (e.g., 'en', 'uk')
            prompt: Optional prompt to guide transcription style

        Returns:
            Transcribed text

        Raises:
            FileNotFoundError: If audio file doesn't exist
            TranscriptionError: If transcription fails
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        file_size = os.path.getsize(audio_file_path)
        logger.info(f"Transcribing: {audio_file_path} ({file_size} bytes)")

        if self.backend == 'mlx':
            return self._transcribe_mlx(audio_file_path, language)
        elif self.backend == 'local':
            return self._transcribe_local(audio_file_path, language, prompt)
        else:
            return self._transcribe_api(audio_file_path, language, prompt)

    def _transcribe_mlx(self, audio_file_path: str, language: Optional[str]) -> str:
        """MLX backend transcription."""
        try:
            start_time = time.time()
            result = self.client.transcribe(
                audio_file_path,
                language=language if language else None,
            )
            text = result.get('text', '').strip()
            elapsed = time.time() - start_time
            logger.info(f"MLX transcription: {elapsed:.2f}s, {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"MLX error: {e}")
            raise TranscriptionError(f"MLX transcription failed: {e}")

    def _transcribe_local(self, audio_file_path: str, language: Optional[str], prompt: Optional[str]) -> str:
        """Local faster-whisper transcription."""
        try:
            start_time = time.time()
            task = "translate" if self.translation_mode else "transcribe"
            segments, _ = self.client.transcribe(
                audio_file_path,
                language=language,
                initial_prompt=prompt,
                task=task
            )
            text = " ".join([seg.text for seg in segments]).strip()
            elapsed = time.time() - start_time
            logger.info(f"Local transcription: {elapsed:.2f}s, {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"Local error: {e}")
            raise TranscriptionError(f"Local transcription failed: {e}")

    def _transcribe_api(self, audio_file_path: str, language: Optional[str], prompt: Optional[str]) -> str:
        """API backend transcription (OpenAI/Groq) with retries."""
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                
                with open(audio_file_path, 'rb') as audio_file:
                    if self.translation_mode and self.backend == 'openai':
                        response = self.client.audio.translations.create(
                            model=self.model,
                            file=audio_file,
                            prompt=prompt,
                            timeout=self.timeout
                        )
                    else:
                        response = self.client.audio.transcriptions.create(
                            model=self.model,
                            file=audio_file,
                            language=language,
                            prompt=prompt,
                            timeout=self.timeout
                        )
                
                text = response.text.strip()
                elapsed = time.time() - start_time
                logger.info(f"API transcription: {elapsed:.2f}s, {len(text)} chars")
                return text

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                # Don't retry auth errors
                if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                    raise TranscriptionError(f"Authentication failed: {e}")
                
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.info(f"Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise TranscriptionError(f"Failed after {self.max_retries} attempts: {e}")
        
        raise TranscriptionError("Transcription failed")

    def get_info(self) -> dict:
        """Get transcriber info for status endpoint."""
        return {
            "backend": self.backend,
            "model": self.model,
            "translation_mode": self.translation_mode,
            "apple_silicon": IS_APPLE_SILICON,
            "available_backends": {
                "mlx": MLX_AVAILABLE,
                "openai": OPENAI_AVAILABLE,
                "groq": GROQ_AVAILABLE,
                "local": FASTER_WHISPER_AVAILABLE,
            }
        }
