---
name: antigravity-image-gen
description: Generate images using the internal Google Antigravity API (Gemini 3 Pro Image). High quality, native generation without browser automation.
read_when:
  - User asks to generate an image
  - User wants to create visual content
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["node"]}}}
---

# Antigravity Image Generation

Generate high-quality images using the internal Google Antigravity API (Gemini 3 Pro Image). This skill bypasses the need for browser automation by using the `daily-cloudcode-pa.sandbox` endpoint directly with your OAuth credentials.

## Prerequisites

- **Google Antigravity OAuth Profile**: Must be present in `~/.clawdbot/agents/main/agent/auth-profiles.json`.
- **Node.js**: Available in the environment.

## Usage

### Direct Script Execution

```bash
/home/ubuntu/clawd/skills/antigravity-image-gen/scripts/generate.js \
  --prompt "A futuristic city on Mars" \
  --output "/tmp/mars.png" \
  --aspect-ratio "16:9"
```

### Arguments

- `--prompt` (Required): The description of the image.
- `--output` (Optional): Path to save the image (default: `/tmp/antigravity_<ts>.png`).
- `--aspect-ratio` (Optional): `1:1` (default), `16:9`, `9:16`, `4:3`, `3:4`.

## Output

- The script writes the image to the specified path.
- It prints `MEDIA: <path>` to stdout, which allows Clawdbot to automatically detect and display the image.

## Troubleshooting

- **429 Resource Exhausted**: Quota limit reached. Wait or check your project limits.
- **No image data found**: The model might have refused the prompt (safety) or the API structure changed. Check the "Model message" output.
- **Auth Error**: Ensure you have logged in via `google-antigravity` provider.
