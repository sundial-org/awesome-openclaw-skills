#!/usr/bin/env python3
"""Create a Meshy Image-to-3D task and download the resulting OBJ (and MTL if present).

Usage:
  # Local image file
  python3 image_to_3d_obj.py --image ./input.png --out-dir ./out

  # Public URL
  python3 image_to_3d_obj.py --image-url "https://example.com/input.png" --out-dir ./out

Env:
  MESHY_API_KEY (required)
  MESHY_BASE_URL (optional)

Docs:
  https://docs.meshy.ai/en/api/image-to-3d
"""

from __future__ import annotations

import argparse
import os
import re

from meshy_client import MeshyError, create_task, poll_task, download, file_to_data_uri


def _slug(path_or_url: str, max_len: int = 64) -> str:
    s = path_or_url.strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return (s[:max_len] or "meshy")


def main() -> None:
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", help="Local .png/.jpg/.jpeg path")
    src.add_argument("--image-url", help="Public URL or data: URI")

    ap.add_argument("--ai-model", default="latest")
    ap.add_argument("--model-type", default=None, choices=[None, "standard", "lowpoly"], help="standard|lowpoly")
    ap.add_argument("--topology", default=None, choices=[None, "triangle", "quad"])
    ap.add_argument("--target-polycount", type=int, default=None)
    ap.add_argument("--should-texture", action="store_true", help="Force should_texture=true")
    ap.add_argument("--no-texture", action="store_true", help="Force should_texture=false")

    ap.add_argument("--out-dir", default="./meshy-out")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    image_url = args.image_url
    if args.image:
        image_url = file_to_data_uri(args.image)

    payload = {
        "image_url": image_url,
        "ai_model": args.ai_model,
    }
    if args.model_type:
        payload["model_type"] = args.model_type
    if args.topology:
        payload["topology"] = args.topology
    if args.target_polycount is not None:
        payload["target_polycount"] = args.target_polycount

    if args.should_texture and args.no_texture:
        raise MeshyError("Choose only one of --should-texture or --no-texture")
    if args.should_texture:
        payload["should_texture"] = True
    if args.no_texture:
        payload["should_texture"] = False

    task_id = create_task("/openapi/v1/image-to-3d", payload)
    task = poll_task(f"/openapi/v1/image-to-3d/{task_id}", timeout_s=args.timeout)

    status = str(task.get("status", "")).upper()
    if status != "SUCCEEDED":
        raise MeshyError(f"Image-to-3D task did not succeed. status={status} task={task}")

    model_urls = task.get("model_urls") or {}
    if not isinstance(model_urls, dict) or not model_urls.get("obj"):
        raise MeshyError(f"No model_urls.obj in task response: {task}")

    out_dir = os.path.join(args.out_dir, f"image-to-3d_{task_id}_{_slug(args.image or args.image_url)}")
    os.makedirs(out_dir, exist_ok=True)

    obj_path = os.path.join(out_dir, "model.obj")
    download(str(model_urls["obj"]), obj_path)
    print(obj_path)

    # If present, also download MTL.
    if model_urls.get("mtl"):
        mtl_path = os.path.join(out_dir, "model.mtl")
        download(str(model_urls["mtl"]), mtl_path)
        print(mtl_path)


if __name__ == "__main__":
    main()
