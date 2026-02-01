#!/usr/bin/env python3
"""Convert raw PCM audio data to WAV format.

Azure OpenAI Realtime API outputs PCM audio (24kHz, 16-bit, mono).
This script converts it to standard WAV format for browser playback.

Usage:
    from pcm_to_wav import pcm_to_wav
    wav_bytes = pcm_to_wav(pcm_data, sample_rate=24000)
"""

import struct
import io


def pcm_to_wav(
    pcm_data: bytes,
    sample_rate: int = 24000,
    channels: int = 1,
    sample_width: int = 2
) -> bytes:
    """Convert raw PCM audio data to WAV format.
    
    Args:
        pcm_data: Raw PCM audio bytes
        sample_rate: Samples per second (default 24000 for gpt-realtime-mini)
        channels: Number of audio channels (default 1 for mono)
        sample_width: Bytes per sample (default 2 for 16-bit)
    
    Returns:
        WAV-formatted audio bytes
    """
    wav_buffer = io.BytesIO()
    
    # RIFF header
    wav_buffer.write(b'RIFF')
    wav_buffer.write(struct.pack('<I', 36 + len(pcm_data)))  # File size - 8
    wav_buffer.write(b'WAVE')
    
    # fmt subchunk
    wav_buffer.write(b'fmt ')
    wav_buffer.write(struct.pack('<I', 16))                    # Subchunk size
    wav_buffer.write(struct.pack('<H', 1))                     # Audio format (1 = PCM)
    wav_buffer.write(struct.pack('<H', channels))              # Number of channels
    wav_buffer.write(struct.pack('<I', sample_rate))           # Sample rate
    wav_buffer.write(struct.pack('<I', sample_rate * channels * sample_width))  # Byte rate
    wav_buffer.write(struct.pack('<H', channels * sample_width))  # Block align
    wav_buffer.write(struct.pack('<H', sample_width * 8))      # Bits per sample
    
    # data subchunk
    wav_buffer.write(b'data')
    wav_buffer.write(struct.pack('<I', len(pcm_data)))
    wav_buffer.write(pcm_data)
    
    return wav_buffer.getvalue()


def calculate_duration(pcm_data: bytes, sample_rate: int = 24000, sample_width: int = 2) -> int:
    """Calculate audio duration in seconds from PCM data length."""
    return len(pcm_data) // (sample_rate * sample_width)


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            pcm_data = f.read()
        wav_data = pcm_to_wav(pcm_data)
        output_path = sys.argv[1].replace('.pcm', '.wav')
        with open(output_path, 'wb') as f:
            f.write(wav_data)
        print(f"Converted to {output_path} ({calculate_duration(pcm_data)}s)")
