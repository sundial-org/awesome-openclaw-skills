#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Nano Banana Pro (Gemini 3 Pro Image) via Google Antigravity OAuth.

Uses existing OpenClaw Antigravity OAuth credentials - no separate API key needed!

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png"
    uv run generate_image.py --prompt "edit this" --filename "output.png" -i input.png
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Antigravity OAuth credentials (same as OpenClaw/opencode plugins)
ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
ANTIGRAVITY_CLIENT_SECRET = "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"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# CloudCode API endpoints
CLOUDCODE_ENDPOINTS = [
    "https://daily-cloudcode-pa.googleapis.com",
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://cloudcode-pa.googleapis.com",
]

# Image model
IMAGE_MODEL = "gemini-3-pro-image"
IMAGE_MODEL_PRO = "gemini-3-pro-image-preview"  # Nano Banana Pro

CLOUDCODE_METADATA = {
    "ideType": "ANTIGRAVITY",
    "platform": "PLATFORM_UNSPECIFIED",
    "pluginType": "GEMINI",
}


def find_all_antigravity_credentials() -> list[dict]:
    """Find ALL OpenClaw Antigravity credentials for rotation."""
    
    all_creds = []
    
    # Priority 1: OpenClaw auth-profiles.json (primary location)
    auth_profiles_paths = [
        Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json",
        Path.home() / ".openclaw" / "auth-profiles.json",
    ]
    
    for path in auth_profiles_paths:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                profiles = data.get("profiles", {})
                
                # Find ALL google-antigravity profiles with refresh token
                for key, profile in profiles.items():
                    if profile.get("provider") == "google-antigravity" and profile.get("refresh"):
                        email = profile.get("email", key.split(":")[-1] if ":" in key else "unknown")
                        all_creds.append({
                            "email": email,
                            "refreshToken": profile["refresh"],
                            "accessToken": profile.get("access"),
                            "projectId": profile.get("projectId"),
                        })
                
                if all_creds:
                    print(f"Found {len(all_creds)} Antigravity accounts for rotation", file=sys.stderr)
                    return all_creds
                    
            except Exception as e:
                print(f"Error reading {path}: {e}", file=sys.stderr)
                continue
    
    return all_creds


def find_openclaw_credentials() -> Optional[dict]:
    """Find first OpenClaw Antigravity credential (legacy function)."""
    all_creds = find_all_antigravity_credentials()
    if all_creds:
        print(f"Using account: {all_creds[0]['email']}", file=sys.stderr)
        return all_creds[0]
    return None
    
    # Priority 2: Legacy paths
    legacy_paths = [
        Path.home() / ".openclaw" / "credentials" / "google-antigravity.json",
        Path.home() / ".config" / "opencode" / "antigravity-accounts.json",
        Path.home() / ".opencode" / "antigravity-accounts.json",
    ]
    
    for path in legacy_paths:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                # opencode format: {"accounts": [...]}
                if "accounts" in data:
                    for account in data["accounts"]:
                        if account.get("refreshToken"):
                            print(f"Found credentials for: {account.get('email', 'unknown')}", file=sys.stderr)
                            return account
                # Direct format
                elif data.get("refreshToken"):
                    return data
            except Exception as e:
                print(f"Error reading {path}: {e}", file=sys.stderr)
                continue
    
    return None


def refresh_access_token(refresh_token: str) -> str:
    """Refresh OAuth access token."""
    import requests
    
    response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": ANTIGRAVITY_CLIENT_ID,
            "client_secret": ANTIGRAVITY_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    
    if not response.ok:
        raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")
    
    return response.json()["access_token"]


def load_code_assist(access_token: str, base_url: str) -> dict:
    """Load code assist info to get project ID."""
    import requests
    
    response = requests.post(
        f"{base_url}/v1internal:loadCodeAssist",
        json={"metadata": CLOUDCODE_METADATA},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "antigravity",
        },
    )
    
    if not response.ok:
        raise Exception(f"loadCodeAssist failed: {response.status_code}")
    
    return response.json()


def extract_project_id(project) -> Optional[str]:
    """Extract project ID from cloudaicompanionProject field."""
    if not project:
        return None
    if isinstance(project, str):
        return project
    return project.get("id")


def generate_image(
    access_token: str,
    project_id: str,
    prompt: str,
    input_images: Optional[list[Path]] = None,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
) -> tuple[bytes, str]:
    """Generate an image using Nano Banana Pro."""
    import requests
    
    # Build content parts
    parts = [{"text": prompt}]
    
    # Add input images for editing
    if input_images:
        for img_path in input_images:
            if img_path.exists():
                img_data = base64.b64encode(img_path.read_bytes()).decode()
                mime_type = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
                parts.append({
                    "inlineData": {
                        "data": img_data,
                        "mimeType": mime_type,
                    }
                })
    
    # Build request
    request_body = {
        "project": project_id,
        "requestId": f"req_{int(time.time())}_{os.urandom(4).hex()}",
        "model": IMAGE_MODEL_PRO,  # Try Nano Banana Pro first
        "userAgent": "antigravity",
        "requestType": "agent",
        "request": {
            "contents": [{"role": "user", "parts": parts}],
            "session_id": f"sess_{int(time.time())}_{os.urandom(4).hex()}",
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size,
                },
            },
        },
    }
    
    last_error = None
    
    for base_url in CLOUDCODE_ENDPOINTS:
        try:
            print(f"Trying endpoint: {base_url}", file=sys.stderr)
            
            response = requests.post(
                f"{base_url}/v1internal:streamGenerateContent?alt=sse",
                json=request_body,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "antigravity",
                },
                timeout=120,
            )
            
            if response.status_code == 429:
                print(f"Rate limited on {base_url}, trying next...", file=sys.stderr)
                continue
            
            if not response.ok:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                # Try fallback to regular model
                if IMAGE_MODEL_PRO in request_body["model"]:
                    print("Trying fallback to regular Nano Banana...", file=sys.stderr)
                    request_body["model"] = IMAGE_MODEL
                    continue
                continue
            
            # Parse SSE response
            for line in response.text.split("\n"):
                if not line.startswith("data: "):
                    continue
                
                json_str = line[6:]
                if json_str == "[DONE]":
                    continue
                
                try:
                    data = json.loads(json_str)
                    
                    if "error" in data:
                        last_error = f"{data['error'].get('code')}: {data['error'].get('message')}"
                        continue
                    
                    candidates = data.get("response", {}).get("candidates", [])
                    for candidate in candidates:
                        parts = candidate.get("content", {}).get("parts", [])
                        for part in parts:
                            inline_data = part.get("inlineData", {})
                            if inline_data.get("data") and inline_data.get("mimeType", "").startswith("image/"):
                                image_bytes = base64.b64decode(inline_data["data"])
                                mime_type = inline_data["mimeType"]
                                return image_bytes, mime_type
                except json.JSONDecodeError:
                    continue
            
            last_error = "No image in response"
            
        except requests.exceptions.Timeout:
            print(f"Timeout on {base_url}, trying next...", file=sys.stderr)
            continue
        except Exception as e:
            last_error = str(e)
            continue
    
    raise Exception(f"All endpoints failed. Last error: {last_error}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro via Antigravity OAuth"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        dest="input_images",
        metavar="IMAGE",
        help="Input image path(s) for editing. Can be specified multiple times."
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        default="1:1",
        help="Aspect ratio (default: 1:1)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    
    args = parser.parse_args()
    
    # Find ALL credentials for rotation
    print("Looking for Antigravity OAuth credentials...", file=sys.stderr)
    all_creds = find_all_antigravity_credentials()
    
    if not all_creds:
        print("Error: No Antigravity credentials found.", file=sys.stderr)
        print("Make sure you have authenticated with OpenClaw:", file=sys.stderr)
        print("  openclaw models auth login --provider google-antigravity", file=sys.stderr)
        sys.exit(1)
    
    # Parse input images
    input_images = None
    if args.input_images:
        input_images = [Path(p) for p in args.input_images]
        for p in input_images:
            if not p.exists():
                print(f"Warning: Input image not found: {p}", file=sys.stderr)
    
    # Try each account until one succeeds
    last_error = None
    for i, creds in enumerate(all_creds):
        try:
            print(f"Trying account {i+1}/{len(all_creds)}: {creds['email']}", file=sys.stderr)
            
            # Refresh access token
            access_token = refresh_access_token(creds["refreshToken"])
            
            # Get project ID if not cached
            project_id = creds.get("projectId")
            if not project_id:
                print("Getting project ID...", file=sys.stderr)
                code_assist = load_code_assist(access_token, CLOUDCODE_ENDPOINTS[0])
                project_id = extract_project_id(code_assist.get("cloudaicompanionProject"))
            
            if not project_id:
                print(f"  Could not determine project ID, trying next account...", file=sys.stderr)
                continue
            
            print(f"  Using project: {project_id}", file=sys.stderr)
            
            # Generate image
            print(f"Generating image with Nano Banana Pro...", file=sys.stderr)
            print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}", file=sys.stderr)
            
            image_bytes, mime_type = generate_image(
                access_token=access_token,
                project_id=project_id,
                prompt=args.prompt,
                input_images=input_images,
                aspect_ratio=args.aspect_ratio,
                image_size=args.resolution,
            )
            
            # Determine output path
            output_path = Path(args.filename)
            if not output_path.is_absolute():
                output_path = Path.cwd() / output_path
            
            # Ensure correct extension based on mime type
            ext = ".jpg" if "jpeg" in mime_type else ".png"
            if output_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                output_path = output_path.with_suffix(ext)
            
            # Save image
            output_path.write_bytes(image_bytes)
            
            size_kb = len(image_bytes) / 1024
            print(f"Image saved: {output_path} ({size_kb:.1f} KB)", file=sys.stderr)
            print(f"  (used account: {creds['email']})", file=sys.stderr)
            
            # Output MEDIA line for OpenClaw
            print(f"MEDIA:{output_path}")
            return  # Success!
            
        except Exception as e:
            last_error = str(e)
            print(f"  Failed: {e}", file=sys.stderr)
            if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                print(f"  Rate limited, trying next account...", file=sys.stderr)
                continue
            # For other errors, also try next account
            continue
    
    # All accounts failed
    print(f"Error: All {len(all_creds)} accounts failed. Last error: {last_error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
