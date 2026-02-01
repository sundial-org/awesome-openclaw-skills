#!/usr/bin/env python3

import argparse
import base64
import datetime as _dt
import json
import os
import random
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
    return (s[:max_len] or "illustration").strip("-")


def _default_out_dir() -> str:
    projects_tmp = os.path.expanduser("~/Projects/tmp")
    if os.path.isdir(projects_tmp):
        return os.path.join(projects_tmp, f"creative-illustration-{_stamp()}")
    return os.path.join(os.getcwd(), "tmp", f"creative-illustration-{_stamp()}")


def _api_url() -> str:
    base = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "https://api.openai.com"
    ).rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/images/generations"
    return f"{base}/v1/images/generations"


def _build_prompt(
    subject: str,
    ill_type: str,
    style: str,
    mood: str,
    palette: str | None,
    composition: str | None,
) -> str:
    """Build illustration prompt from components."""
    parts = []

    # Style prefix
    style_prefixes = {
        "watercolor": "Watercolor painting",
        "oil-painting": "Oil painting on canvas",
        "charcoal-sketch": "Charcoal sketch",
        "ink-wash": "Ink wash painting",
        "pastel": "Pastel drawing",
        "colored-pencil": "Colored pencil illustration",
        "gouache": "Gouache painting",
        "acrylic": "Acrylic painting",
        "lino-cut": "Linocut print",
        "woodcut": "Woodcut print",
        "digital-painting": "Digital painting",
        "vector-illustration": "Vector illustration",
        "flat-design": "Flat design illustration",
        "isometric": "Isometric illustration",
        "pixel-art": "Pixel art",
        "concept-art": "Concept art",
        "cel-shaded": "Cel shaded illustration",
        "low-poly": "Low poly art",
        "picture-book": "Picture book illustration",
        "storybook-illustration": "Storybook illustration",
        "editorial-illustration": "Editorial illustration",
        "newspaper-engraving": "Newspaper engraving style",
        "poster-art": "Vintage poster art",
        "woodblock-print": "Japanese woodblock print",
        "screen-print": "Screen print",
    }

    style_prefix = style_prefixes.get(style, style)
    parts.append(style_prefix)

    # Type-specific additions
    type_additions = {
        "chapter-opener": "full-page illustration",
        "character-intro": "character portrait illustration",
        "landscape-scene": "landscape establishing shot",
        "action-moment": "dynamic action scene",
        "emotional-scene": "emotional scene illustration",
        "cover-art": "book cover style illustration",
        "conceptual-art": "conceptual illustration",
        "info-graphic": "informational illustration",
        "portrait-editorial": "editorial portrait",
        "spot-illustration": "spot illustration",
        "full-page-spread": "full-page magazine spread",
        "picture-book": "children's book illustration",
        "whimsical": "whimsical illustration",
        "educational": "educational illustration",
        "bedtime-story": "bedtime story art",
        "adventure-map": "adventure map illustration",
    }

    if ill_type in type_additions:
        parts.append(type_additions[ill_type])

    # Subject
    parts.append(subject)

    # Mood
    if mood:
        mood_words = {
            "whimsical": "whimsical and playful",
            "magical": "magical and enchanting",
            "mysterious": "mysterious and intriguing",
            "peaceful": "peaceful and serene",
            "dramatic": "dramatic and intense",
            "nostalgic": "warm and nostalgic",
            "gloomy": "dark and atmospheric",
            "vibrant": "bright and energetic",
            "romantic": "soft and romantic",
            "quirky": "quirky and eccentric",
        }
        mood_word = mood_words.get(mood, mood)
        parts.append(f"mood: {mood_word}")

    # Palette
    if palette:
        palette_descriptions = {
            "pastel": "soft pastel color palette",
            "earth tones": "natural earth tones (browns, greens, golds)",
            "vibrant": "bright saturated colors",
            "muted": "desaturated, subtle colors",
            "monochrome": "monochrome color scheme",
            "jewel tones": "rich jewel tones (ruby, emerald, sapphire)",
            "autumn": "autumn colors (orange, red, yellow, brown)",
            "winter": "winter colors (blue, white, silver, purple)",
            "tropical": "bright tropical colors (greens, teals, pinks)",
            "vintage": "warm vintage tones, sepia",
        }
        palette_desc = palette_descriptions.get(palette, f"{palette} color palette")
        parts.append(f"palette: {palette_desc}")

    # Composition
    if composition:
        comp_descriptions = {
            "wide shot": "wide shot composition",
            "close-up": "close-up, intimate composition",
            "panoramic": "panoramic landscape composition",
            "rule-of-thirds": "balanced rule-of-thirds composition",
            "centered": "centered subject",
            "diagonal": "dynamic diagonal composition",
            "triangular": "triangular composition",
            "circular": "circular composition",
            "symmetrical": "perfectly symmetrical",
            "asymmetrical": "asymmetrical balance",
            "symbolic": "symbolic composition",
        }
        comp_desc = comp_descriptions.get(composition, composition)
        parts.append(comp_desc)

    # Quality tags
    parts.append("detailed, high quality, professional illustration")

    return ". ".join(parts) + "."


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


def _write_index(out_dir: str, items: list[dict]) -> None:
    html = [
        "<!doctype html>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>creative-illustration</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui;margin:24px;max-width:1200px}",
        ".card{display:grid;grid-template-columns:260px 1fr;gap:18px;align-items:start;margin:20px 0;padding:16px;background:#fafafa;border-radius:12px}",
        "img{width:260px;height:260px;object-fit:cover;border-radius:10px;box-shadow:0 10px 28px rgba(0,0,0,.12)}",
        "pre{white-space:pre-wrap;margin:0;background:#222;color:#f5f5f5;padding:12px 14px;border-radius:10px;line-height:1.4;font-size:13px}",
        ".meta{margin:8px 0;color:#666;font-size:13px}",
        "h3{margin:0 0 8px 0;font-size:16px;color:#333}",
        ".tags{display:inline-block;background:#e8f4fd;padding:4px 10px;border-radius:20px;font-size:12px;margin-right:6px}",
        "</style>",
        "<h1>🎨 Creative Illustration Factory</h1>",
    ]
    for it in items:
        html.append("<div class='card'>")
        html.append(f"<a href='{it['file']}'><img src='{it['file']}'></a>")
        html.append("<div>")
        if it.get("metadata"):
            meta = it["metadata"]
            html.append("<h3>" + meta.get("subject", "Illustration") + "</h3>")

            tags = []
            if meta.get("style"):
                tags.append(f"style: {meta['style']}")
            if meta.get("mood"):
                tags.append(f"mood: {meta['mood']}")
            if meta.get("type"):
                tags.append(f"type: {meta['type']}")
            if meta.get("palette"):
                tags.append(f"palette: {meta['palette']}")
            if meta.get("composition"):
                tags.append(f"comp: {meta['composition']}")

            if tags:
                tag_html = " ".join(f'<span class="tags">{tag}</span>' for tag in tags)
                html.append(f'<div class="meta">{tag_html}</div>')

        html.append(f"<pre>{it['prompt']}</pre>")
        html.append("</div>")
        html.append("</div>")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="creative-illustration",
        description="Generate creative illustrations via OpenAI Images API.",
    )
    p.add_argument("--subject", action="append", default=None, help="Illustration subject (repeatable)")
    p.add_argument("--type", default="illustration", help="Illustration type")
    p.add_argument("--style", default="watercolor", help="Artistic style")
    p.add_argument("--mood", default="peaceful", help="Mood/atmosphere")
    p.add_argument("--palette", default=None, help="Color palette")
    p.add_argument("--composition", default=None, help="Composition guidance")
    p.add_argument("--prompt", action="append", default=None, help="Full custom prompt (repeatable)")
    p.add_argument("--count", type=int, default=1, help="Number of variants per subject")
    p.add_argument("--size", default="1024x1024", help="Image size")
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

    # Build prompts
    prompts_with_meta: list[tuple[str, dict]] = []

    if args.prompt:
        # Custom prompts
        for pr in args.prompt:
            prompts_with_meta.append((pr, {}))
    elif args.subject:
        # Build prompts from components
        for subject in args.subject:
            prompt = _build_prompt(
                subject=subject,
                ill_type=args.type,
                style=args.style,
                mood=args.mood,
                palette=args.palette,
                composition=args.composition,
            )
            metadata = {
                "subject": subject,
                "type": args.type,
                "style": args.style,
                "mood": args.mood,
                "palette": args.palette,
                "composition": args.composition,
            }
            for _ in range(args.count):
                prompts_with_meta.append((prompt, metadata))
    else:
        # Default random subjects
        default_subjects = [
            "a magical library with floating books",
            "a lighthouse at sunset",
            "a robot tending a rooftop garden",
            "a whimsical cottage in an enchanted forest",
        ]
        for subject in default_subjects:
            prompt = _build_prompt(
                subject=subject,
                ill_type=args.type,
                style=args.style,
                mood=args.mood,
                palette=args.palette,
                composition=args.composition,
            )
            metadata = {
                "subject": subject,
                "type": args.type,
                "style": args.style,
                "mood": args.mood,
            }
            prompts_with_meta.append((prompt, metadata))

    if args.dry_run:
        for i, (pr, meta) in enumerate(prompts_with_meta, 1):
            subject = meta.get("subject", "")
            if subject:
                print(f"{i:02d} [{subject}] {pr}")
            else:
                print(f"{i:02d} {pr}")
        print(f"out_dir={out_dir}")
        return 0

    url = _api_url()
    items: list[dict] = []

    for i, (prompt, metadata) in enumerate(prompts_with_meta, 1):
        print(f"Generating illustration {i}/{len(prompts_with_meta)}...")

        payload = {
            "model": args.model,
            "prompt": prompt,
            "size": args.size,
            "quality": args.quality,
            "n": 1,
            "response_format": "b64_json",
        }

        data = _post_json(url=url, api_key=api_key, payload=payload, timeout_s=args.timeout)
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            raise SystemExit(f"unexpected response: {json.dumps(data, indent=2)[:1200]}")

        png = base64.b64decode(b64)
        subject_label = metadata.get("subject", "illustration") if metadata else "illustration"
        filename = f"{i:02d}-{_slug(subject_label)}.png"
        path = os.path.join(out_dir, filename)
        with open(path, "wb") as f:
            f.write(png)

        item = {
            "file": filename,
            "prompt": prompt,
            "model": args.model,
            "size": args.size,
            "quality": args.quality,
        }
        if metadata:
            item["metadata"] = metadata

        items.append(item)
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
