#!/usr/bin/env python3
"""
Transcribe audio using soundfile + Whisper (no FFmpeg needed)
Supports OGG, WAV, MP3, and other formats via libsndfile
"""
import json
import sys

if len(sys.argv) < 2:
    print(json.dumps({"error": "Usage: transcribe.py <audio-file>"}))
    sys.exit(1)

audio_file = sys.argv[1]

try:
    import soundfile as sf
    import numpy as np
    import whisper
    
    # Load audio with soundfile (supports OGG, WAV, FLAC, etc.)
    data, sr = sf.read(audio_file)
    
    # Ensure float32
    if data.dtype != np.float32:
        data = data.astype(np.float32)
    
    # Handle stereo -> mono
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Load Whisper model and transcribe
    model = whisper.load_model("base")
    result = model.transcribe(data, language="en")
    
    text = result.get("text", "").strip()
    print(json.dumps({"text": text, "success": True}))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
