#!/usr/bin/env python3
"""Create a Meshy Text-to-Image task and download the resulting image(s).

Usage:
  python3 text_to_image.py --prompt "a cute robot" --out-dir ./out

Env:
  MESHY_API_KEY (required)
  MESHY_BASE_URL (optional)

Docs:
  https://docs.meshy.ai/en/api/text-to-image
"""

from __future__ import annotations

import argparse
import os
import re

from meshy_client import MeshyError, create_task, poll_task, download


def _slug(s: str, max_len: int = 64) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return (s[:max_len] or "meshy")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--ai-model", default="nano-banana")
    ap.add_argument("--aspect-ratio", default=None)
    ap.add_argument("--generate-multi-view", action="store_true")
    ap.add_argument("--out-dir", default="./meshy-out")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    payload = {
        "ai_model": args.ai_model,
        "prompt": args.prompt,
    }
    if args.generate_multi_view:
        payload["generate_multi_view"] = True
    if args.aspect_ratio and not args.generate_multi_view:
        payload["aspect_ratio"] = args.aspect_ratio

    task_id = create_task("/openapi/v1/text-to-image", payload)
    task = poll_task(f"/openapi/v1/text-to-image/{task_id}", timeout_s=args.timeout)

    status = str(task.get("status", "")).upper()
    if status != "SUCCEEDED":
        raise MeshyError(f"Text-to-Image task did not succeed. status={status} task={task}")

    urls = task.get("image_urls") or []
    if not isinstance(urls, list) or not urls:
        raise MeshyError(f"No image_urls in task response: {task}")

    out_dir = os.path.join(args.out_dir, f"text-to-image_{task_id}_{_slug(args.prompt)}")
    os.makedirs(out_dir, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        out_path = os.path.join(out_dir, f"image_{i}.png")
        download(str(url), out_path)
        print(out_path)


if __name__ == "__main__":
    main()
