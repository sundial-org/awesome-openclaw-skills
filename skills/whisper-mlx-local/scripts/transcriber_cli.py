#!/usr/bin/env python3
"""
Direct CLI for local-whisper transcription.
Used as fallback when daemon is not running.

Usage:
    python transcriber_cli.py <audio_file> [--translate] [--language XX] [--backend mlx]
"""

import argparse
import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transcriber import Transcriber, TranscriptionError


def main():
    parser = argparse.ArgumentParser(description='Transcribe audio file')
    parser.add_argument('file', help='Audio file to transcribe')
    parser.add_argument('--translate', '-t', action='store_true', help='Translate to English')
    parser.add_argument('--language', '-l', help='Source language (ISO-639-1)')
    parser.add_argument('--backend', '-b', default='auto', help='Backend: auto, mlx, openai, groq, local')
    parser.add_argument('--model', '-m', help='Model name')
    parser.add_argument('--json', '-j', action='store_true', help='Output JSON')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        transcriber = Transcriber(
            backend=args.backend,
            model=args.model,
            translation_mode=args.translate,
        )
        
        text = transcriber.transcribe(args.file, language=args.language)
        
        if args.json:
            import json
            print(json.dumps({
                "text": text,
                "backend": transcriber.backend,
                "model": transcriber.model,
            }))
        else:
            print(text)
            
    except TranscriptionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
