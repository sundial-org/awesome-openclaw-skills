#!/usr/bin/env python3
"""
Runware Video Generation - Text-to-video, image-to-video.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
import uuid
from pathlib import Path


def api_request(api_key: str, tasks: list, timeout: int = 300) -> dict:
    """Send request to Runware API."""
    url = "https://api.runware.ai/v1"
    body = json.dumps(tasks).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            error_data = json.loads(error_body)
            print(f"API Error ({e.code}): {json.dumps(error_data, indent=2)}", file=sys.stderr)
        except:
            print(f"API Error ({e.code}): {error_body[:500]}", file=sys.stderr)
        sys.exit(1)


def load_image_as_datauri(path: str) -> str:
    """Load image file as data URI."""
    path = Path(path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    suffix = path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(suffix.lstrip("."), "image/png")
    
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def download_file(url: str, output_path: str):
    """Download file from URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "runware-skill/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(output_path, "wb") as f:
            f.write(resp.read())


def poll_for_result(api_key: str, task_uuid: str, max_wait: int = 600, interval: int = 5) -> dict:
    """Poll for async task result."""
    print(f"Video generation started. Polling for result (max {max_wait}s)...")
    
    elapsed = 0
    while elapsed < max_wait:
        task = {
            "taskType": "getResponse",
            "taskUUID": task_uuid,
        }
        
        result = api_request(api_key, [task], timeout=30)
        
        if result.get("data"):
            for item in result["data"]:
                if item.get("taskUUID") == task_uuid:
                    status = item.get("status", "")
                    if status == "success" or item.get("videoURL"):
                        return item
                    elif status == "failed":
                        print(f"Error: Task failed - {item.get('error', 'Unknown error')}", file=sys.stderr)
                        sys.exit(1)
        
        print(f"  Waiting... ({elapsed}s elapsed)")
        time.sleep(interval)
        elapsed += interval
    
    print(f"Error: Timed out after {max_wait}s", file=sys.stderr)
    sys.exit(1)


def cmd_generate(args):
    """Text-to-video generation."""
    api_key = args.api_key or os.environ.get("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set (use --api-key or env var)", file=sys.stderr)
        sys.exit(1)
    
    task_uuid = str(uuid.uuid4())
    
    task = {
        "taskType": "videoInference",
        "taskUUID": task_uuid,
        "positivePrompt": args.prompt,
        "model": args.model,
        "duration": args.duration,
        "width": args.width,
        "height": args.height,
        "numberResults": 1,
        "outputType": "URL",
        "outputFormat": args.format.upper(),
        "deliveryMethod": "async",
        "includeCost": True,
    }
    
    if args.negative:
        task["negativePrompt"] = args.negative
    if args.seed:
        task["seed"] = args.seed
    
    # Submit the task
    result = api_request(api_key, [task], timeout=60)
    
    # Check for immediate result (unlikely for video)
    if result.get("data") and result["data"][0].get("videoURL"):
        video_url = result["data"][0]["videoURL"]
    else:
        # Poll for result
        final = poll_for_result(api_key, task_uuid, max_wait=args.max_wait)
        video_url = final.get("videoURL")
        if not video_url:
            print("Error: No video URL in result", file=sys.stderr)
            print(json.dumps(final, indent=2), file=sys.stderr)
            sys.exit(1)
    
    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading video...")
    download_file(video_url, str(output_path))
    print(f"Saved: {output_path}")


def cmd_img2vid(args):
    """Image-to-video generation."""
    api_key = args.api_key or os.environ.get("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    task_uuid = str(uuid.uuid4())
    
    # Load frame images
    frame_images = []
    for i, img_path in enumerate(args.images):
        if img_path.startswith(("http://", "https://")):
            img_data = img_path
        else:
            img_data = load_image_as_datauri(img_path)
        
        frame = "first" if i == 0 else ("last" if i == len(args.images) - 1 else None)
        frame_obj = {"inputImage": img_data}
        if frame:
            frame_obj["frame"] = frame
        frame_images.append(frame_obj)
    
    task = {
        "taskType": "videoInference",
        "taskUUID": task_uuid,
        "positivePrompt": args.prompt or "smooth animation, natural movement, cinematic quality",
        "model": args.model,
        "duration": args.duration,
        "width": args.width,
        "height": args.height,
        "frameImages": frame_images,
        "numberResults": 1,
        "outputType": "URL",
        "outputFormat": args.format.upper(),
        "deliveryMethod": "async",
        "includeCost": True,
    }
    
    if args.negative:
        task["negativePrompt"] = args.negative
    
    result = api_request(api_key, [task], timeout=60)
    
    if result.get("data") and result["data"][0].get("videoURL"):
        video_url = result["data"][0]["videoURL"]
    else:
        final = poll_for_result(api_key, task_uuid, max_wait=args.max_wait)
        video_url = final.get("videoURL")
        if not video_url:
            print("Error: No video URL in result", file=sys.stderr)
            sys.exit(1)
    
    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading video...")
    download_file(video_url, str(output_path))
    print(f"Saved: {output_path}")


def cmd_models(args):
    """List popular video models."""
    models = {
        "Kling AI 1.6 Pro": "klingai:5@3",
        "Kling AI 1.5 Pro": "klingai:3@2",
        "Kling AI 1.0 Standard": "klingai:1@1",
        "Runway Gen-3": "runwayml:1@1",
        "MiniMax": "minimax:1@1",
    }
    print("Popular Runware video models:\n")
    for name, model_id in models.items():
        print(f"  {name}: {model_id}")
    print("\nMore at: https://runware.ai/models")


def main():
    parser = argparse.ArgumentParser(prog="runware-video", description="Runware Video Generation")
    parser.add_argument("--api-key", help="Runware API key (or set RUNWARE_API_KEY)")
    parser.add_argument("--max-wait", type=int, default=600, help="Max seconds to wait for video")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate (text-to-video)
    gen = subparsers.add_parser("generate", aliases=["gen", "t2v"], help="Text-to-video generation")
    gen.add_argument("prompt", help="Video description")
    gen.add_argument("--model", default="klingai:5@3", help="Model ID (default: Kling AI 1.6 Pro)")
    gen.add_argument("--duration", type=int, default=5, help="Duration in seconds")
    gen.add_argument("--width", type=int, default=1920)
    gen.add_argument("--height", type=int, default=1080)
    gen.add_argument("--negative", help="Negative prompt")
    gen.add_argument("--seed", type=int, help="Random seed")
    gen.add_argument("--format", default="mp4", choices=["mp4", "webm", "mov"])
    gen.add_argument("--output", "-o", default="./output.mp4", help="Output file path")
    gen.set_defaults(func=cmd_generate)
    
    # Image-to-video
    i2v = subparsers.add_parser("img2vid", aliases=["i2v"], help="Image-to-video generation")
    i2v.add_argument("images", nargs="+", help="Input images (paths or URLs, first/last frames)")
    i2v.add_argument("--prompt", help="Motion/style prompt")
    i2v.add_argument("--model", default="klingai:5@3")
    i2v.add_argument("--duration", type=int, default=5)
    i2v.add_argument("--width", type=int, default=1920)
    i2v.add_argument("--height", type=int, default=1080)
    i2v.add_argument("--negative", help="Negative prompt")
    i2v.add_argument("--format", default="mp4", choices=["mp4", "webm", "mov"])
    i2v.add_argument("--output", "-o", default="./output.mp4")
    i2v.set_defaults(func=cmd_img2vid)
    
    # Models
    models = subparsers.add_parser("models", help="List popular video models")
    models.set_defaults(func=cmd_models)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
