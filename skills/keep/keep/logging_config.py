"""
Logging configuration for keep.

Suppress verbose library output by default for better UX.
"""

import os
import sys
import warnings

# Set environment variables BEFORE any imports to suppress warnings early
if not os.environ.get("KEEP_VERBOSE"):
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def configure_quiet_mode(quiet: bool = True):
    """
    Configure logging to suppress verbose library output.
    
    This silences:
    - HuggingFace transformers progress bars
    - MLX model loading messages
    - Library warnings (deprecation, etc.)
    
    Args:
        quiet: If True, suppress verbose output. If False, show everything.
    """
    if quiet:
        # Suppress HuggingFace progress bars and warnings
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Suppress Python warnings (including deprecation warnings)
        warnings.filterwarnings("ignore")
        
        # Suppress MLX verbosity if available
        try:
            import mlx.core as mx
            # MLX doesn't have a global verbosity setting currently,
            # but we can redirect stderr if needed
        except ImportError:
            pass
        
        # Configure Python logging to be less verbose
        import logging
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
        logging.getLogger("mlx").setLevel(logging.ERROR)
        logging.getLogger("chromadb").setLevel(logging.ERROR)


def enable_verbose_mode():
    """Re-enable verbose output for debugging."""
    configure_quiet_mode(quiet=False)
    
    # Restore defaults
    os.environ.pop("HF_HUB_DISABLE_PROGRESS_BARS", None)
    os.environ.pop("TRANSFORMERS_VERBOSITY", None)
    
    # Re-enable warnings
    warnings.filterwarnings("default")
    
    # Reset logging levels
    import logging
    logging.getLogger("transformers").setLevel(logging.INFO)
    logging.getLogger("sentence_transformers").setLevel(logging.INFO)
    logging.getLogger("mlx").setLevel(logging.INFO)
    logging.getLogger("chromadb").setLevel(logging.INFO)
