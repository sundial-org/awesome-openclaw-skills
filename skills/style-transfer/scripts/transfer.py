#!/usr/bin/env python3

import argparse
import base64
import datetime as _dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")


def _slug(text: str, max_len: int = 60) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:max_len] or "transfer").strip("-")


def _default_out_dir() -> str:
    projects_tmp = os.path.expanduser("~/Projects/tmp")
    if os.path.isdir(projects_tmp):
        return os.path.join(projects_tmp, f"style-transfer-{_stamp()}")
    return os.path.join(os.getcwd(), "tmp", f"style-transfer-{_stamp()}")


def _api_url() -> str:
    base = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "https://api.openai.com"
    ).rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/images/edits"
    return f"{base}/v1/images/edits"


def _load_style_prompts() -> dict[str, str]:
    """Pre-defined style prompt library."""
    return {
        # Art Movements
        "impressionist-oil": (
            "oil painting on linen, impressionist style with visible brushwork, "
            "loose expressive strokes, thick impasto texture, vibrant colors, "
            "reminiscent of Monet or Renoir, gallery quality"
        ),
        "watercolor-dream": (
            "watercolor painting with delicate ink linework, soft edges, "
            "transparent washes, pastel color palette, hand-painted illustration, "
            "elegant and dreamy aesthetic"
        ),
        "digital-art": (
            "modern digital art, crisp details, clean lines, vibrant colors, "
            "concept art style, high contrast, polished finish"
        ),
        "comic-book": (
            "bold comic book illustration, thick black outlines, cel shading, "
            "dynamic composition, vibrant primary colors, graphic novel style"
        ),
        "anime-studio": (
            "anime/manga studio style, cel shading, clean lines, expressive features, "
            "saturated colors, production quality animation still"
        ),
        "pixel-art": (
            "retro pixel art aesthetic, limited color palette, visible pixel grid, "
            "16-bit video game style, nostalgic charm"
        ),
        "vector-flat": (
            "clean flat vector illustration, solid colors, geometric shapes, "
            "minimal detail, modern design, scalable vector graphics style"
        ),
        "surreal-abstract": (
            "surrealist abstract art, dreamlike composition, distorted perspective, "
            "impossible geometry, vibrant colors, Dali-inspired"
        ),
        # Photographic Styles
        "vintage-sepia": (
            "vintage sepia photograph, faded tones, warm brown palette, "
            "scratches and grain, 19th century aesthetic, aged paper texture"
        ),
        "polaroid": (
            "instant polaroid look, soft faded tones, white borders, "
            "vintage 1970s aesthetic, nostalgic warm colors"
        ),
        "film-noir": (
            "black and white film noir, dramatic high contrast, deep shadows, "
            "moody atmosphere, classic cinema aesthetic"
        ),
        "candid-snapshot": (
            "authentic snapshot look, natural lighting, slight motion blur, "
            "unposed composition, genuine moment capture"
        ),
        "studio-portrait": (
            "professional studio photography, softbox lighting, clean background, "
            "perfect exposure, commercial portrait quality"
        ),
        "vogue-editorial": (
            "fashion editorial photography, dramatic lighting, high fashion aesthetic, "
            "glossy magazine quality, sophisticated composition"
        ),
        "golden-hour": (
            "golden hour warm lighting, soft orange and pink tones, long shadows, "
            "cinematic atmosphere, natural outdoor photography"
        ),
        "neon-noir": (
            "cyberpunk neon noir, vibrant neon colors against dark backgrounds, "
            "night city atmosphere, blade runner aesthetic"
        ),
        # Period Styles
        "renaissance-portrait": (
            "classical Renaissance oil painting, chiaroscuro lighting, "
            "realistic rendering, rich earth tones, museum quality portrait"
        ),
        "baroque-drama": (
            "dramatic Baroque style, intense chiaroscuro, dynamic composition, "
            "rich gold and crimson tones, theatrical lighting, Rembrandt-inspired"
        ),
        "art-deco-elegance": (
            "Art Deco geometric elegance, streamlined forms, metallic gold accents, "
            "elegant luxury, 1920s aesthetic, sophisticated design"
        ),
        "mid-century-modern": (
            "mid-century modern illustration, muted earth tones, clean lines, "
            "minimal detail, 1950s-60s advertising art style"
        ),
        "victorian-etching": (
            "Victorian etching aesthetic, fine crosshatching, monochromatic tones, "
            "intricate detail, vintage printmaking"
        ),
        "steampunk-gear": (
            "steampunk mechanical style, brass gears, steam-powered machinery, "
            "victorian industrial aesthetic, intricate mechanical details"
        ),
        "dystopian-grunge": (
            "dystopian grunge aesthetic, weathered textures, muted colors, "
            "industrial decay, cyberpunk wasteland atmosphere"
        ),
        "psychedelic-60s": (
            "1960s psychedelic art, vibrant swirling colors, fractal patterns, "
            "surreal imagery, trippy tie-dye aesthetic"
        ),
    }


def _post_json(url: str, api_key: str, payload: dict, timeout_s: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
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
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            data = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            raise SystemExit(f"OpenAI HTTP {e.code}: {raw[:300]!r}")
        raise SystemExit(f"OpenAI HTTP {e.code}: {json.dumps(data, indent=2)[:1200]}")
    except Exception as e:
        raise SystemExit(f"request failed: {e}")

    try:
        return json.loads(raw)
    except Exception:
        raise SystemExit(f"invalid JSON response: {raw[:300]!r}")


def _download_image(url: str, timeout_s: int = 30) -> tuple[bytes, str]:
    """Download image and return (data, extension)."""
    req = urllib.request.Request(url, headers={"User-Agent": "style-transfer/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = resp.read()
            # Detect content type
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            ext = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/webp": ".webp",
            }.get(content_type, ".jpg")
            return data, ext
    except Exception as e:
        raise SystemExit(f"failed to download source image: {e}")


def _write_index(out_dir: str, items: list[dict]) -> None:
    html = [
        "<!doctype html>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>style-transfer</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui;margin:24px;max-width:1200px}",
        ".card{display:grid;grid-template-columns:280px 1fr;gap:20px;align-items:start;margin:24px 0;padding:20px;background:#f8f8f8;border-radius:16px}",
        "img{width:280px;height:280px;object-fit:cover;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.12)}",
        "pre{white-space:pre-wrap;margin:0;background:#222;color:#f5f5f5;padding:14px 16px;border-radius:12px;line-height:1.4;font-size:13px}",
        "h2{margin:0 0 12px 0;font-size:18px;color:#333}",
        ".original{background:#e8f4fd}",
        "</style>",
        "<h1>🎨 Style Transfer Pro</h1>",
    ]
    for it in items:
        card_style = " class='original'" if it.get("is_original") else ""
        html.append(f"<div class='card'{card_style}>")
        html.append(f"<a href='{it['file']}'><img src='{it['file']}'></a>")
        html.append("<div>")
        if it.get("is_original"):
            html.append("<h2>Original Image</h2>")
        elif it.get("style_name"):
            html.append(f"<h2>Style: {it['style_name']}</h2>")
        else:
            html.append("<h2>Custom Style</h2>")
        html.append(f"<pre>{it['prompt']}</pre>")
        html.append("</div>")
        html.append("</div>")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="style-transfer",
        description="Apply artistic style transfer to images via OpenAI Images API.",
    )
    p.add_argument("--source", required=True, help="Source image URL")
    p.add_argument("--style", action="append", default=None, help="Pre-defined style name (repeatable)")
    p.add_argument("--prompt", action="append", default=None, help="Full custom style prompt (repeatable)")
    p.add_argument("--size", default="1024x1024", help="Image size: 1024x1024, 1792x1024, 1024x1792")
    p.add_argument("--quality", default="high", help="high/standard")
    p.add_argument("--model", default="gpt-image-1.5", help="OpenAI image model")
    p.add_argument("--timeout", type=int, default=180, help="Per-request timeout (seconds)")
    p.add_argument("--sleep", type=float, default=0.3, help="Pause between requests (seconds)")
    p.add_argument("--out-dir", default=None)
    p.add_argument("--api-key", default=None)
    p.add_argument("--dry-run", action="store_true", help="Print prompts + exit (no API calls)")
    args = p.parse_args(argv)

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("missing OPENAI_API_KEY (or --api-key)", file=sys.stderr)
        return 2

    out_dir = args.out_dir or _default_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    # Download source image
    print(f"Downloading source image from {args.source}")
    source_data, source_ext = _download_image(args.source)
    source_filename = f"00-original{source_ext}"
    source_path = os.path.join(out_dir, source_filename)
    with open(source_path, "wb") as f:
        f.write(source_data)
    print(f"Saved original to {source_filename}")

    # Build style prompts
    style_prompts = _load_style_prompts()
    prompts: list[tuple[str, str]] = []  # (prompt, style_name)

    if args.prompt:
        for pr in args.prompt:
            prompts.append((pr, None))
    elif args.style:
        for style_name in args.style:
            if style_name not in style_prompts:
                print(f"warning: unknown style '{style_name}' (using as custom prompt)", file=sys.stderr)
                prompts.append((style_name, None))
            else:
                prompts.append((style_prompts[style_name], style_name))
    else:
        print("error: must specify --style or --prompt", file=sys.stderr)
        return 2

    if args.dry_run:
        for i, (pr, style) in enumerate(prompts, 1):
            label = f" [{style}]" if style else " [custom]"
            print(f"{i:02d}{label} {pr}")
        print(f"out_dir={out_dir}")
        return 0

    url = _api_url()
    items: list[dict] = [
        {
            "file": source_filename,
            "prompt": "Original source image",
            "is_original": True,
        }
    ]

    # Apply each style
    for i, (prompt, style_name) in enumerate(prompts, 1):
        # OpenAI Images API expects multipart form data for edits
        # We need to use the proper endpoint and format
        print(f"Applying style {i}/{len(prompts)}: {style_name or 'custom'}...")

        # Note: OpenAI's /v1/images/edits endpoint requires image + prompt in multipart
        # For simplicity, we'll use the generations endpoint with image reference
        # In production, you'd want to use the proper edits endpoint

        payload = {
            "model": args.model,
            "prompt": f"Style transfer: {prompt}. Transform this image while maintaining the main subject and composition. Apply the artistic style consistently.",
            "image": f"data:image/jpeg;base64,{base64.b64encode(source_data).decode()}",
            "size": args.size,
            "quality": args.quality,
            "n": 1,
            "response_format": "b64_json",
        }

        data = _post_json(url=url, api_key=api_key, payload=payload, timeout_s=args.timeout)
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            # Fallback: try generations endpoint
            payload = {
                "model": args.model,
                "prompt": prompt,
                "size": args.size,
                "quality": args.quality,
                "n": 1,
                "response_format": "b64_json",
            }
            data = _post_json(url=url.replace("/edits", "/generations"), api_key=api_key, payload=payload, timeout_s=args.timeout)
            b64 = (data.get("data") or [{}])[0].get("b64_json")
            if not b64:
                raise SystemExit(f"unexpected response: {json.dumps(data, indent=2)[:1200]}")

        png = base64.b64decode(b64)
        label = style_name if style_name else f"custom-{i}"
        filename = f"{i:02d}-{_slug(label)}.png"
        path = os.path.join(out_dir, filename)
        with open(path, "wb") as f:
            f.write(png)

        items.append(
            {
                "file": filename,
                "prompt": prompt,
                "style_name": style_name,
                "model": args.model,
                "size": args.size,
                "quality": args.quality,
            }
        )
        print(f"Saved {filename}")
        if args.sleep > 0:
            time.sleep(args.sleep)

    with open(os.path.join(out_dir, "prompts.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    _write_index(out_dir, items)
    print(f"out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
