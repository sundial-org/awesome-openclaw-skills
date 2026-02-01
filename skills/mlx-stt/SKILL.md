---
name: mlx-stt
description: Transcribe audio to text with MLX (Apple Silicon) and GLM-ASR.
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://github.com/Blaizzy/mlx-audio","os":["darwin"],"requires":{"bins":["uv"],"anyBins":[],"env":[],"config":[]},"install":["uv"]}}
---

# MLX Speech to Text

Transcribe audio to text with MLX (Apple Silicon) and GLM-ASR. Free and Accurate.

## Requirements

- `mlx`(macOS with Apple Silicon)
- any of `uv|python|python3`, ability to run python script.
- `ffmpeg`
- `mlx_audio.generate.stt` installed and in PATH: `uv tool install --force mlx-audio --prerelease=allow`

## Usage

To transcribe an audio file, run the `mlx-stt.py` with any of these:

```bash
uv run  ${baseDir}/mlx-stt.py <audio_file_path>
python  ${baseDir}/mlx-stt.py <audio_file_path>
python3 ${baseDir}/mlx-stt.py <audio_file_path>
```

If none of these works, can fallback to `mlx-stt.sh` bash script:
```bash
bash ${baseDir}/mlx-stt.sh <audio_file_path>
```

The transcript result will be printed to tty.
