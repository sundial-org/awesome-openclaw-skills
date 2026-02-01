#!/usr/bin/env python3
"""Transcribe audio using mlx_audio.stt.generate."""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_MODEL = "mlx-community/GLM-ASR-Nano-2512-8bit"
MODEL_URL="https://github.com/Blaizzy/mlx-audio?tab=readme-ov-file#speech-to-text-stt"


def to_wav(source: Path, dest: Path) -> None:
    """Convert input audio to 16 kHz mono WAV for mlx-audio."""
    cmd = [
        "ffmpeg",
        "-i",
        str(source),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(dest),
        "-y",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_stt(model: str, language: str | None, audio: Path, output_base: Path) -> Path:
    """Invoke mlx_audio.stt.generate and return path to transcript."""
    cmd = [
        "mlx_audio.stt.generate",
        "--model",
        model,
        "--audio",
        str(audio),
        "--format",
        "txt",
        "--output",
        str(output_base),
    ]
    if language:
        cmd.extend(["--language", language])

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Path(f"{output_base}.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="speech-to-text on macOS with mlx-audio and glm-asr-nano-2512-8bit.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("audio", type=Path, help="Path to the input audio file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path (without extension). Defaults to a temp path.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model to use, more choices: {MODEL_URL}",
    )
    parser.add_argument(
        "-l",
        "--language",
        help="Language code for transcription (e.g., en, zh).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audio_path = args.audio.expanduser()
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_wav = Path(temp_dir) / "input.wav"
        output_base = args.output.expanduser() if args.output else Path(temp_dir) / "out"
        output_base.parent.mkdir(parents=True, exist_ok=True)

        try:
            to_wav(audio_path, temp_wav)
            transcript_path = run_stt(args.model, args.language, temp_wav, output_base)
            transcript = transcript_path.read_text(encoding="utf-8")
            print(transcript)
        except FileNotFoundError as exc:
            print(f"Missing dependency: {exc}", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"Command failed: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    main()
