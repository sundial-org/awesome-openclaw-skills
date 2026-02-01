#!/usr/bin/env python3
"""
fal.ai API - Image, Video, and Audio Generation Skill

Usage:
    python fal_api.py --prompt "A beautiful sunset" --model flux-dev

Or use as a module:
    from fal_api import FalAPI
    api = FalAPI()
    urls = api.generate_and_wait(prompt="...")
"""

import json
import os
import time
import urllib.request
import urllib.error
import argparse
from typing import Optional, List, Dict, Any


class FalAPI:
    """Client for fal.ai generative media API."""
    
    QUEUE_URL = "https://queue.fal.run"
    
    # Available models and their endpoints
    MODELS = {
        # Image generation
        "flux-schnell": "fal-ai/flux/schnell",
        "flux-dev": "fal-ai/flux/dev",
        "flux-pro": "fal-ai/flux-pro/v1.1-ultra",
        "fast-sdxl": "fal-ai/fast-sdxl",
        "recraft-v3": "fal-ai/recraft-v3",
        "sd35-large": "fal-ai/stable-diffusion-v35-large",
        # Video generation
        "minimax-video": "fal-ai/minimax-video/image-to-video",
        "wan-video": "fal-ai/wan/v2.1/1.3b/text-to-video",
        # Audio
        "whisper": "fal-ai/whisper",
    }
    
    # Preset image sizes
    IMAGE_SIZES = {
        "square": "square",
        "square_hd": "square_hd", 
        "portrait_4_3": "portrait_4_3",
        "portrait_16_9": "portrait_16_9",
        "landscape_4_3": "landscape_4_3",
        "landscape_16_9": "landscape_16_9",
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize the fal.ai API client.
        
        Args:
            api_key: Your FAL_KEY (or set via env/config)
        """
        if not api_key:
            api_key = os.environ.get("FAL_KEY") or self._get_config("key")
        
        if not api_key:
            raise ValueError("FAL_KEY required. Set via env or clawdbot config.")
        
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Klawf/1.0; +https://clawdhub.com/agmmnn/fal-api)"
        }
    
    def _get_config(self, key: str) -> Optional[str]:
        """Get config from clawdbot config if available."""
        try:
            import subprocess
            result = subprocess.run(
                ["clawdbot", "config", "get", f"skill.fal_api.{key}"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _request(self, method: str, url: str, data: dict = None) -> dict:
        """Make HTTP request to fal.ai API."""
        req = urllib.request.Request(url, method=method)
        for k, v in self.headers.items():
            if method == "GET" and k.lower() == "content-type":
                continue
            req.add_header(k, v)
        
        if data:
            req.data = json.dumps(data).encode()
        
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode())
    
    def submit(
        self,
        model: str,
        payload: Dict[str, Any],
    ) -> dict:
        """
        Submit a job to the queue.
        
        Args:
            model: Model name or full endpoint
            payload: Request payload
            
        Returns:
            dict with request_id, status_url, response_url
        """
        endpoint = self.MODELS.get(model, model)
        url = f"{self.QUEUE_URL}/{endpoint}"
        return self._request("POST", url, payload)
    
    def get_status(self, model: str, request_id: str) -> dict:
        """Get the status of a queued request."""
        endpoint = self.MODELS.get(model, model)
        url = f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}/status"
        return self._request("GET", url)
    
    def get_result(self, model: str, request_id: str) -> dict:
        """Get the result of a completed request."""
        endpoint = self.MODELS.get(model, model)
        url = f"{self.QUEUE_URL}/{endpoint}/requests/{request_id}"
        return self._request("GET", url)
    
    def wait_for_completion(
        self,
        model: str,
        request_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0
    ) -> dict:
        """Poll until job completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_status(model, request_id)
            state = status.get("status")
            
            if state == "COMPLETED":
                return self.get_result(model, request_id)
            elif state == "FAILED":
                raise Exception(f"Job failed: {status}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {request_id} did not complete within {timeout}s")
    
    def generate_image(
        self,
        prompt: str,
        model: str = "flux-dev",
        image_size: str = "landscape_16_9",
        num_images: int = 1,
        seed: Optional[int] = None,
        **kwargs
    ) -> dict:
        """
        Submit an image generation job.
        
        Args:
            prompt: Text description of the image
            model: Model name (default: "flux-dev")
            image_size: Size preset (default: "landscape_16_9")
            num_images: Number of images (default: 1)
            seed: Random seed for reproducibility
            **kwargs: Additional model-specific parameters
            
        Returns:
            dict with request_id and status URLs
        """
        payload = {
            "prompt": prompt,
            "image_size": self.IMAGE_SIZES.get(image_size, image_size),
            "num_images": num_images,
            **kwargs
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        return self.submit(model, payload)
    
    def generate_video(
        self,
        prompt: str,
        image_url: str = None,
        model: str = "minimax-video",
        **kwargs
    ) -> dict:
        """
        Submit a video generation job.
        
        Args:
            prompt: Text description
            image_url: Source image URL (for image-to-video)
            model: Video model name
            **kwargs: Additional parameters
            
        Returns:
            dict with request_id and status URLs
        """
        payload = {"prompt": prompt, **kwargs}
        if image_url:
            payload["image_url"] = image_url
        
        return self.submit(model, payload)
    
    def transcribe(
        self,
        audio_url: str,
        model: str = "whisper",
        **kwargs
    ) -> dict:
        """
        Submit an audio transcription job.
        
        Args:
            audio_url: URL of audio file
            model: Whisper model variant
            **kwargs: Additional parameters
            
        Returns:
            dict with request_id and status URLs
        """
        payload = {"audio_url": audio_url, **kwargs}
        return self.submit(model, payload)
    
    def generate_and_wait(
        self,
        prompt: str,
        model: str = "flux-dev",
        **kwargs
    ) -> List[str]:
        """Generate an image and wait for the result."""
        job = self.generate_image(prompt, model, **kwargs)
        request_id = job["request_id"]
        print(f"Job submitted: {request_id}")
        
        result = self.wait_for_completion(model, request_id)
        
        # Extract URLs from result (format varies by model)
        images = result.get("images", [])
        if images:
            return [img.get("url") for img in images if img.get("url")]
        
        # Fallback for different response formats
        if "image" in result:
            return [result["image"].get("url")]
        
        return []


def main():
    parser = argparse.ArgumentParser(description="Generate media with fal.ai API")
    parser.add_argument("--prompt", help="Text description")
    parser.add_argument("--model", default="flux-dev", help="Model name (default: flux-dev)")
    parser.add_argument("--size", default="landscape_16_9", help="Image size preset")
    parser.add_argument("--num-images", type=int, default=1, help="Number of images")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--api-key", help="FAL_KEY (or set via environment)")

    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        for name, endpoint in FalAPI.MODELS.items():
            print(f"  {name:20} → {endpoint}")
        return

    if not args.prompt:
        parser.error("--prompt is required unless --list-models is set")

    api = FalAPI(api_key=args.api_key)

    print(f"Generating '{args.prompt[:50]}...' with {args.model}...")
    urls = api.generate_and_wait(
        prompt=args.prompt,
        model=args.model,
        image_size=args.size,
        num_images=args.num_images,
        seed=args.seed
    )

    print("\nGenerated images:")
    for url in urls:
        print(f"  {url}")


if __name__ == "__main__":
    main()
