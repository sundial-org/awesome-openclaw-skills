#!/usr/bin/env python3
"""
Gemini-based Speech-to-Text transcription.

Supports two authentication methods:
1. GEMINI_API_KEY - Direct Gemini API access
2. Google Vertex AI - Using Application Default Credentials (ADC)

For Vertex AI, requires:
- gcloud auth application-default login
- GOOGLE_CLOUD_PROJECT or CLOUDSDK_CORE_PROJECT env var

Usage:
    python transcribe.py <audio_file> [--model MODEL] [--vertex] [--project PROJECT] [--region REGION]

Supports: audio/ogg (opus), audio/mp3, audio/wav, audio/m4a
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-2.0-flash-lite"
DEFAULT_VERTEX_REGION = "us-central1"

SUPPORTED_EXTENSIONS = {
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
}


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return SUPPORTED_EXTENSIONS.get(ext, "audio/ogg")


def get_gcloud_access_token() -> str | None:
    """Get access token from gcloud CLI (Application Default Credentials)."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def get_gcloud_project() -> str | None:
    """Get project ID from gcloud config."""
    # Check env vars first
    for env_var in ["GOOGLE_CLOUD_PROJECT", "CLOUDSDK_CORE_PROJECT", "GCLOUD_PROJECT"]:
        project = os.environ.get(env_var)
        if project:
            return project
    
    # Fall back to gcloud config
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def transcribe_with_api_key(file_path: str, api_key: str, model: str) -> str:
    """Transcribe using direct Gemini API with API key."""
    with open(file_path, "rb") as f:
        audio_data = f.read()

    b64_data = base64.b64encode(audio_data).decode("utf-8")
    mime_type = get_mime_type(file_path)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Transcribe this audio file exactly. Return only the transcription text, no preamble."
                    },
                    {"inline_data": {"mime_type": mime_type, "data": b64_data}},
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]


def transcribe_with_vertex(file_path: str, access_token: str, project: str, region: str, model: str) -> str:
    """Transcribe using Google Vertex AI with ADC."""
    with open(file_path, "rb") as f:
        audio_data = f.read()

    b64_data = base64.b64encode(audio_data).decode("utf-8")
    mime_type = get_mime_type(file_path)

    url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google/models/{model}:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Transcribe this audio file exactly. Return only the transcription text, no preamble."
                    },
                    {"inline_data": {"mime_type": mime_type, "data": b64_data}},
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]


def transcribe(file_path: str, api_key: str | None = None, model: str = DEFAULT_MODEL,
               use_vertex: bool = False, project: str | None = None, region: str = DEFAULT_VERTEX_REGION) -> str:
    """
    Transcribe an audio file using Gemini API or Vertex AI.

    Args:
        file_path: Path to the audio file
        api_key: Gemini API key (optional if using Vertex)
        model: Gemini model to use
        use_vertex: Force use of Vertex AI
        project: GCP project ID (for Vertex)
        region: GCP region (for Vertex, default: us-central1)

    Returns:
        Transcribed text

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If API call fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        # If API key is provided and not forcing Vertex, use direct API
        if api_key and not use_vertex:
            return transcribe_with_api_key(file_path, api_key, model)
        
        # Try Vertex AI with ADC
        access_token = get_gcloud_access_token()
        if access_token:
            project = project or get_gcloud_project()
            if not project:
                raise RuntimeError("No GCP project configured. Set GOOGLE_CLOUD_PROJECT or run 'gcloud config set project PROJECT_ID'")
            return transcribe_with_vertex(file_path, access_token, project, region, model)
        
        # Fall back to API key if available
        if api_key:
            return transcribe_with_api_key(file_path, api_key, model)
        
        raise RuntimeError("No authentication available. Set GEMINI_API_KEY or run 'gcloud auth application-default login'")
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected API response format: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Google's Gemini API or Vertex AI"
    )
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--vertex",
        "-v",
        action="store_true",
        help="Force use of Vertex AI (uses ADC)",
    )
    parser.add_argument(
        "--project",
        "-p",
        help="GCP project ID (for Vertex AI, defaults to gcloud config)",
    )
    parser.add_argument(
        "--region",
        "-r",
        default=DEFAULT_VERTEX_REGION,
        help=f"GCP region (for Vertex AI, default: {DEFAULT_VERTEX_REGION})",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    
    # If no API key and not forcing vertex, auto-detect
    if not api_key and not args.vertex:
        # Check if ADC is available
        if get_gcloud_access_token():
            args.vertex = True
        else:
            print("Error: No authentication available.", file=sys.stderr)
            print("  Option 1: Set GEMINI_API_KEY environment variable", file=sys.stderr)
            print("  Option 2: Run 'gcloud auth application-default login' for Vertex AI", file=sys.stderr)
            sys.exit(1)

    try:
        text = transcribe(
            args.audio_file,
            api_key=api_key,
            model=args.model,
            use_vertex=args.vertex,
            project=args.project,
            region=args.region,
        )
        print(text)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
