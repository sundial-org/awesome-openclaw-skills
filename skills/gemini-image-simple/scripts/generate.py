#!/usr/bin/env python3
"""
Gemini Image Generation - Pure Python stdlib, no dependencies.

Usage:
    python3 generate.py "prompt" output.png
    python3 generate.py "edit instructions" output.png --input original.png

Requires GEMINI_API_KEY environment variable.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path


def get_api_key():
    """Get API key from environment."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def load_image_as_base64(path):
    """Load an image file and return base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def detect_mime_type(path):
    """Detect MIME type from file extension."""
    ext = Path(path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "image/png")


def generate_image(prompt, output_path, input_image_path=None):
    """Generate or edit an image using Gemini API."""
    api_key = get_api_key()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key}"
    
    # Build request parts
    parts = [{"text": prompt}]
    
    # Add input image if provided (for editing)
    if input_image_path:
        if not os.path.exists(input_image_path):
            print(f"Error: Input image not found: {input_image_path}", file=sys.stderr)
            sys.exit(1)
        
        img_data = load_image_as_base64(input_image_path)
        mime_type = detect_mime_type(input_image_path)
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": img_data
            }
        })
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    # Extract image from response
    try:
        candidates = result.get("candidates", [])
        if not candidates:
            print("Error: No candidates in response", file=sys.stderr)
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        
        for part in parts:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                
                # Ensure output directory exists
                output_dir = Path(output_path).parent
                if output_dir and not output_dir.exists():
                    output_dir.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(img_data)
                
                print(f"Saved: {output_path}")
                return output_path
        
        print("Error: No image data in response", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
        
    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Gemini API (pure stdlib, no dependencies)"
    )
    parser.add_argument("prompt", help="Image prompt or edit instructions")
    parser.add_argument("output", help="Output file path (e.g., output.png)")
    parser.add_argument("--input", "-i", help="Input image for editing (optional)")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.output, args.input)


if __name__ == "__main__":
    main()
