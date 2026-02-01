#!/usr/bin/env python3
"""
Runware Image Generation - Text-to-image, image-to-image, inpainting, upscaling.
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
import uuid
from pathlib import Path


def api_request(api_key: str, tasks: list, timeout: int = 180) -> dict:
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


def download_image(url: str, output_path: str):
    """Download image from URL to file."""
    req = urllib.request.Request(url, headers={"User-Agent": "runware-skill/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(output_path, "wb") as f:
            f.write(resp.read())


def cmd_generate(args):
    """Text-to-image generation."""
    api_key = args.api_key or os.environ.get("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set (use --api-key or env var)", file=sys.stderr)
        sys.exit(1)
    
    task = {
        "taskType": "imageInference",
        "taskUUID": str(uuid.uuid4()),
        "positivePrompt": args.prompt,
        "model": args.model,
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "CFGScale": args.cfg,
        "numberResults": args.count,
        "outputType": "URL",
        "outputFormat": args.format.upper(),
        "includeCost": True,
    }
    
    if args.negative:
        task["negativePrompt"] = args.negative
    if args.seed:
        task["seed"] = args.seed
    if args.lora:
        task["lora"] = [{"model": args.lora, "weight": args.lora_weight}]
    
    result = api_request(api_key, [task], timeout=args.timeout)
    
    if not result.get("data"):
        print("Error: No data in response", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, item in enumerate(result["data"], 1):
        url = item.get("imageURL")
        if not url:
            continue
        
        ext = args.format.lower()
        filename = f"{i:02d}-{args.prompt[:40].replace(' ', '-')}.{ext}"
        filepath = output_dir / filename
        
        download_image(url, str(filepath))
        print(f"Saved: {filepath}")
        if item.get("cost"):
            print(f"  Cost: ${item['cost']:.4f}")
        if item.get("seed"):
            print(f"  Seed: {item['seed']}")
    
    print(f"\nTotal images: {len(result['data'])}")


def cmd_img2img(args):
    """Image-to-image transformation."""
    api_key = args.api_key or os.environ.get("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    seed_image = args.input
    if not seed_image.startswith(("http://", "https://", "data:")):
        seed_image = load_image_as_datauri(args.input)
    
    task = {
        "taskType": "imageInference",
        "taskUUID": str(uuid.uuid4()),
        "positivePrompt": args.prompt,
        "model": args.model,
        "seedImage": seed_image,
        "strength": args.strength,
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "CFGScale": args.cfg,
        "numberResults": args.count,
        "outputType": "URL",
        "outputFormat": args.format.upper(),
        "includeCost": True,
    }
    
    if args.negative:
        task["negativePrompt"] = args.negative
    
    result = api_request(api_key, [task], timeout=args.timeout)
    
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, item in enumerate(result.get("data", []), 1):
        url = item.get("imageURL")
        if not url:
            continue
        
        ext = args.format.lower()
        filename = f"img2img-{i:02d}.{ext}"
        filepath = output_dir / filename
        
        download_image(url, str(filepath))
        print(f"Saved: {filepath}")


def cmd_upscale(args):
    """Upscale an image."""
    api_key = args.api_key or os.environ.get("RUNWARE_API_KEY")
    if not api_key:
        print("Error: RUNWARE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    input_image = args.input
    if not input_image.startswith(("http://", "https://", "data:")):
        input_image = load_image_as_datauri(args.input)
    
    task = {
        "taskType": "imageUpscale",
        "taskUUID": str(uuid.uuid4()),
        "inputImage": input_image,
        "upscaleFactor": args.factor,
        "outputType": "URL",
        "outputFormat": args.format.upper(),
        "includeCost": True,
    }
    
    result = api_request(api_key, [task], timeout=args.timeout)
    
    if result.get("data") and result["data"][0].get("imageURL"):
        url = result["data"][0]["imageURL"]
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        download_image(url, str(output_path))
        print(f"Saved: {output_path}")
        if result["data"][0].get("cost"):
            print(f"Cost: ${result['data'][0]['cost']:.4f}")
    else:
        print("Error: No image in response", file=sys.stderr)
        sys.exit(1)


def cmd_models(args):
    """List popular models (reference info)."""
    models = {
        "FLUX.1 Dev": "runware:101@1",
        "FLUX.1 Schnell": "runware:100@1",
        "FLUX.1 Kontext": "runware:106@1",
        "Stable Diffusion XL": "civitai:101055@128080",
        "RealVisXL": "civitai:139562@297320",
        "Juggernaut XL": "civitai:133005@357609",
    }
    print("Popular Runware models:\n")
    for name, model_id in models.items():
        print(f"  {name}: {model_id}")
    print("\nMore at: https://runware.ai/models")


def main():
    parser = argparse.ArgumentParser(prog="runware-image", description="Runware Image Generation")
    parser.add_argument("--api-key", help="Runware API key (or set RUNWARE_API_KEY)")
    parser.add_argument("--timeout", type=int, default=180, help="Request timeout in seconds")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate (text-to-image)
    gen = subparsers.add_parser("generate", aliases=["gen", "t2i"], help="Text-to-image generation")
    gen.add_argument("prompt", help="Image description")
    gen.add_argument("--model", default="runware:101@1", help="Model ID (default: FLUX.1 Dev)")
    gen.add_argument("--width", type=int, default=1024)
    gen.add_argument("--height", type=int, default=1024)
    gen.add_argument("--steps", type=int, default=25)
    gen.add_argument("--cfg", type=float, default=7.5, help="CFG scale")
    gen.add_argument("--count", "-n", type=int, default=1, help="Number of images")
    gen.add_argument("--negative", help="Negative prompt")
    gen.add_argument("--seed", type=int, help="Random seed")
    gen.add_argument("--lora", help="LoRA model ID")
    gen.add_argument("--lora-weight", type=float, default=0.8)
    gen.add_argument("--format", default="png", choices=["png", "jpg", "webp"])
    gen.add_argument("--output", "-o", default="./runware-output", help="Output directory")
    gen.set_defaults(func=cmd_generate)
    
    # Image-to-image
    i2i = subparsers.add_parser("img2img", aliases=["i2i"], help="Image-to-image transformation")
    i2i.add_argument("input", help="Input image (path or URL)")
    i2i.add_argument("prompt", help="Transformation prompt")
    i2i.add_argument("--model", default="runware:101@1")
    i2i.add_argument("--strength", type=float, default=0.7, help="Transformation strength (0-1)")
    i2i.add_argument("--width", type=int, default=1024)
    i2i.add_argument("--height", type=int, default=1024)
    i2i.add_argument("--steps", type=int, default=25)
    i2i.add_argument("--cfg", type=float, default=7.5)
    i2i.add_argument("--count", "-n", type=int, default=1)
    i2i.add_argument("--negative", help="Negative prompt")
    i2i.add_argument("--format", default="png", choices=["png", "jpg", "webp"])
    i2i.add_argument("--output", "-o", default="./runware-output")
    i2i.set_defaults(func=cmd_img2img)
    
    # Upscale
    up = subparsers.add_parser("upscale", aliases=["up"], help="Upscale an image")
    up.add_argument("input", help="Input image (path or URL)")
    up.add_argument("--factor", type=int, default=2, choices=[2, 4], help="Upscale factor")
    up.add_argument("--format", default="png", choices=["png", "jpg", "webp"])
    up.add_argument("--output", "-o", default="./upscaled.png", help="Output file path")
    up.set_defaults(func=cmd_upscale)
    
    # Models
    models = subparsers.add_parser("models", help="List popular models")
    models.set_defaults(func=cmd_models)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
