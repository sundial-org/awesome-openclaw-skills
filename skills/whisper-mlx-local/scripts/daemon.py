#!/usr/bin/env python3
"""
Clawdbot Whisper Daemon

HTTP server for fast speech-to-text transcription.
Pre-loads the model for sub-second response times.

Usage:
    python daemon.py [--port 8787] [--backend mlx] [--model distil-large-v3]

Endpoints:
    POST /transcribe   - Transcribe audio file
    GET  /health       - Health check
    GET  /status       - Transcriber info and stats
"""

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transcriber import Transcriber, TranscriptionError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global state
transcriber: Transcriber = None
stats = {
    "requests": 0,
    "successful": 0,
    "failed": 0,
    "total_audio_bytes": 0,
    "total_transcription_ms": 0,
    "started_at": None,
}


class WhisperHandler(BaseHTTPRequestHandler):
    """HTTP request handler for whisper daemon."""

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

    def send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/health':
            self.send_json({"status": "ok"})
        
        elif path == '/status':
            info = transcriber.get_info() if transcriber else {}
            self.send_json({
                "status": "ok",
                "transcriber": info,
                "stats": stats,
            })
        
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/transcribe':
            self.handle_transcribe()
        else:
            self.send_json({"error": "Not found"}, 404)

    def handle_transcribe(self):
        """Handle transcription request."""
        global stats
        stats["requests"] += 1

        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json({"error": "No audio data"}, 400)
                stats["failed"] += 1
                return

            # Check content type
            content_type = self.headers.get('Content-Type', '')
            
            # Handle multipart form data
            if 'multipart/form-data' in content_type:
                self.send_json({"error": "Use application/octet-stream or send file path as JSON"}, 400)
                stats["failed"] += 1
                return
            
            # Handle JSON with file path
            if 'application/json' in content_type:
                body = self.rfile.read(content_length)
                data = json.loads(body)
                audio_path = data.get('file') or data.get('path')
                language = data.get('language')
                translate = data.get('translate', False)
                
                if not audio_path:
                    self.send_json({"error": "Missing 'file' or 'path' in JSON"}, 400)
                    stats["failed"] += 1
                    return
                
                if not os.path.exists(audio_path):
                    self.send_json({"error": f"File not found: {audio_path}"}, 400)
                    stats["failed"] += 1
                    return
                
                stats["total_audio_bytes"] += os.path.getsize(audio_path)
                
            # Handle raw audio data
            else:
                audio_data = self.rfile.read(content_length)
                stats["total_audio_bytes"] += len(audio_data)
                
                # Parse query params for options
                query = parse_qs(urlparse(self.path).query)
                language = query.get('language', [None])[0]
                translate = query.get('translate', ['false'])[0].lower() == 'true'
                
                # Write to temp file
                ext = '.wav'  # Default, could detect from content-type
                if 'audio/ogg' in content_type or 'audio/opus' in content_type:
                    ext = '.ogg'
                elif 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                    ext = '.mp3'
                elif 'audio/m4a' in content_type:
                    ext = '.m4a'
                
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                    f.write(audio_data)
                    audio_path = f.name

            # Transcribe
            start_time = time.time()
            
            # Handle per-request translation mode
            if translate and not transcriber.translation_mode:
                # Create a temporary transcriber with translation mode
                try:
                    temp_transcriber = Transcriber(
                        backend=transcriber.backend,
                        model=transcriber.model,
                        translation_mode=True,
                    )
                    text = temp_transcriber.transcribe(audio_path, language=language)
                except Exception as e:
                    logger.warning(f"Translation mode failed, falling back to transcription: {e}")
                    text = transcriber.transcribe(audio_path, language=language)
            else:
                text = transcriber.transcribe(audio_path, language=language)
            
            duration_ms = int((time.time() - start_time) * 1000)
            stats["successful"] += 1
            stats["total_transcription_ms"] += duration_ms

            # Clean up temp file if we created one
            if 'audio_data' in locals():
                try:
                    os.unlink(audio_path)
                except:
                    pass

            self.send_json({
                "text": text,
                "duration_ms": duration_ms,
                "backend": transcriber.backend,
            })

        except TranscriptionError as e:
            logger.error(f"Transcription error: {e}")
            stats["failed"] += 1
            self.send_json({"error": str(e)}, 500)
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            stats["failed"] += 1
            self.send_json({"error": f"Internal error: {e}"}, 500)


def warmup_transcriber():
    """Warm up the transcriber with a silent audio file to prime all caches."""
    import wave
    import struct
    
    logger.info("Warming up transcriber...")
    warmup_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    try:
        # Create 1 second of silence (16kHz mono)
        with wave.open(warmup_file.name, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            # 1 second of silence
            wav.writeframes(struct.pack('<' + 'h' * 16000, *([0] * 16000)))
        
        # Transcribe it (result will be empty, but model is now warm)
        start = time.time()
        transcriber.transcribe(warmup_file.name)
        elapsed = int((time.time() - start) * 1000)
        logger.info(f"Warmup complete in {elapsed}ms")
    except Exception as e:
        logger.warning(f"Warmup failed (non-fatal): {e}")
    finally:
        try:
            os.unlink(warmup_file.name)
        except:
            pass


def main():
    global transcriber, stats

    parser = argparse.ArgumentParser(description='Clawdbot Whisper Daemon')
    parser.add_argument('--port', type=int, default=int(os.getenv('CLAWD_WHISPER_PORT', '8787')))
    parser.add_argument('--backend', default=os.getenv('CLAWD_WHISPER_BACKEND', 'auto'))
    parser.add_argument('--model', default=os.getenv('CLAWD_WHISPER_MODEL', 'distil-large-v3'))
    parser.add_argument('--translate', action='store_true', help='Translation mode (to English)')
    parser.add_argument('--no-warmup', action='store_true', help='Skip warmup transcription')
    args = parser.parse_args()

    # Initialize transcriber
    logger.info(f"Initializing transcriber: backend={args.backend}, model={args.model}")
    try:
        transcriber = Transcriber(
            backend=args.backend,
            model=args.model,
            translation_mode=args.translate,
        )
    except Exception as e:
        logger.error(f"Failed to initialize transcriber: {e}")
        sys.exit(1)

    # Warm up the model
    if not args.no_warmup:
        warmup_transcriber()

    # Start server
    stats["started_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
    server = HTTPServer(('127.0.0.1', args.port), WhisperHandler)
    
    logger.info(f"Whisper daemon listening on http://127.0.0.1:{args.port}")
    logger.info(f"Backend: {transcriber.backend}, Model: {transcriber.model}")
    logger.info("Endpoints: POST /transcribe, GET /health, GET /status")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
