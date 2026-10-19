---
name: levea-ai-video-editor
description: "Levea OpenClaw AI video editor & natural language video editing MCP: turn raw video or YouTube links into viral clips, TikTok video, Instagram Reels & YouTube Shorts with auto captions, subtitles, 9:16 vertical reframe, silence removal, audio cleanup, smart jump cuts, B-roll, motion graphics, multi-cam multicam podcast sync, chroma key green screen, background removal, color grading, voiceover, music generation, face blur privacy redaction, brand kit, thumbnails, CapCut alternative & MP4 export."
version: 1.1.5
author: brajendrak00068
license: MIT
platforms: [linux, macos, windows]
metadata:
  openclaw:
    requires:
      env:
        - LEVEA_API_URL
        - LEVEA_API_KEY
      bins:
        - curl
        - jq
    primaryEnv: LEVEA_API_KEY
    skillKey: openclaw_ai_video_editor
    homepage: "https://github.com/brajendrak00068/agentic-ai-video-production#readme"
---

# Levea Agentic Video Editor

A full agentic video-editing surface. Send a prompt and get a planned, verified, executed edit. The autonomous editor chooses its own internal tools, applies safety gates, exports when needed, and returns the final scene/video result. Every edit goes through one HTTP tool — `autonomous_edit` — so there is only one call to learn.

## When to use this skill

Use when the user asks for AI video editing, natural-language video edits, viral clips, TikTok videos, Instagram Reels, YouTube Shorts, auto captions / subtitles, chroma key / green-screen removal, background removal, B-roll, motion tracking, motion graphics, multi-cam editing, smart jump cuts, silence / audio cleanup, voiceover, music generation, object / face blur, privacy redaction, beat sync, brand kits, thumbnails, style presets, vertical (9:16) reframe, safe-zone repair, final delivery checks, export presets, multi-platform export, or MP4 export.

> **Beta**: outputs can be wrong. Before executing any mutating edit on user content, describe the planned edit and ask for explicit confirmation. For destructive or irreversible workflows, pass `requirePlanApproval: true` so the editor halts after planning and the user can approve before execution.

## Setup

This skill calls the Levea HTTP API with `curl` and parses responses with `jq`.

Required binaries: `curl`, `jq`.

Required environment variables:

- `ADSCENE_API_URL` — base URL for the Levea API, e.g. `https://api.livecore.ai`. Do **not** use the Studio URL or the in-product `/api/v1/misc/editor` route.
- `ADSCENE_API_KEY` — API key generated from Studio at `https://livecore.ai/` (sign up / sign in, then create a key). Studio is only for signup, login, and key management.

```bash
export ADSCENE_API_URL="https://api.livecore.ai"
export ADSCENE_API_KEY="your-api-key"
```

## Endpoint

`POST {ADSCENE_API_URL}/api/v1/misc/openclaw/v1/execute`

Auth: `Authorization: Bearer {ADSCENE_API_KEY}`

Accepts single-shot JSON (default) or SSE (`Accept: text/event-stream` or `?stream=true`).

Request body:

```json
{
  "tool": "autonomous_edit",
  "params": { "prompt": "..." },
  "project_id": "optional-project-id",
  "scene": { "_comment": "optional client scene; server-side committed scene wins if newer" }
}
```

## How to use it

Pass a natural-language description in `params.prompt`. The agent classifies intent, decomposes into atomic steps, plans, executes through safety gates, and verifies the result.

```bash
curl -sS -X POST "$ADSCENE_API_URL/api/v1/misc/openclaw/v1/execute" \
  -H "Authorization: Bearer $ADSCENE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "autonomous_edit",
    "params": {
      "prompt": "Make this a TikTok-ready viral clip: vertical reframe, add bold captions, remove silences, and motion-track the speaker."
    },
    "project_id": "my-project"
  }'
```

Behind a single `autonomous_edit` call the agent can compose any of:

**Read / inspect** — timeline + layer structure, CV frame analysis (object/face/scene), transcript search (keyword / semantic / timestamp), video intelligence (narrative peaks, diarization, sentiment, pacing), asset-gallery search, async job polling, property-schema introspection.

**Structural editing** — insert / update / replace / delete layers (video, audio, image, text, shape, solid, adjustment, group, light, vfx, visualizer, lottie); trim / split / retime (slow-mo, fast-forward, freeze-frame); smart jump cuts, filler-word + silence + low-energy cleanup; timeline sequencing, multi-cam sync + angle switching, gap heal, duration reconcile, multi-step undo / redo.

**Visual editing** — color grade (brightness/contrast/saturation/hue, lift-gamma-gain, RGB curves); procedural VFX shaders (smoke, dust, fire, lightning, snow, glitch, grain, bokeh, lava, portal, …); chroma key (similarity/smoothness/spill, luma/alpha/depth masks); clip shapes; crop + 3D rotation/perspective; glow / shadow / gradient fills; vertical reframe (9:16) + montage; split screen + PiP; brand overlays / kits; motion + face tracking with zoom-follow; object hide / blur, face blur, privacy redaction, safe-zone repair.

**Captions & text** — auto captions from transcript; built-in templates or an AI caption director; motion graphics (kinetic captions, lower thirds, stat callouts, charts, comparison overlays, concept-icon Lottie); curved text paths; per-word entrance / exit animations; Lottie playback control.

**Audio** — silence / breath / filler-word cleanup; profanity mute / bleep / cut; auto-ducking; mix / normalize / denoise / EQ; external master-audio sync; beat-synced cuts (`beat_times` or `bpm`); SFX, music generation (mood / genre / BPM), voiceover (TTS or cloned); waveform visualizers.

**Async generation** — AI video / B-roll, AI images (single or batch at timestamps), AI music, AI voiceover, auto-thumbnail or AI thumbnail variants, face blur, instruction-based image edit.

**Export** — `EXPORT_VIDEO` (MP4), `EXPORT_PRESET` (platform / codec / aspect presets + safe-zone repair), `FINAL_DELIVERY_CHECK`, `GENERATE_VIRAL_CLIPS` (auto-segment short-form clips as ZIP), `GENERATE_MULTI_PLATFORM` (TikTok + Reels + Shorts + YouTube + Instagram in one pass).

## Auto-export follow-up

After any **mutating** `autonomous_edit` call where the scene actually changed and the agent did not already queue an export, the route fires one automatically as a second run. The final response carries `videoUrl` (when ready) or `jobId` (for polling). Read-only / conversational calls do **not** trigger auto-export.

## Optional input parameters

Pass any of these inside `params` (or at the top level of the body):

- `prompt` — required on every call (the natural-language edit description)
- `workingMemory` — durable working-memory snapshot; re-send to resume after `awaiting_approval`
- `requirePlanApproval` — `true` stops the agent after planning (`awaiting_approval`); resume with the same `workingMemory` + an approval prompt
- `attachedImages` — array of base64 screenshots / reference images
- `flaggedIssues` — array of strings describing specific problems to fix
- `captionTemplatePreset`, `captionTemplateMode` — caption style routing
- `brandId`, `projectBrandId` — brand-kit selection (colors, fonts, logo, grade bias, voice)
- `core_only` (also `?core_only=true`) — minimal scene shape (rendering-only)
- `assets` — additional asset descriptors to make available to the agent

## Response shape (JSON, default)

```json
{
  "type": "success",
  "tool": "autonomous_edit",
  "success": true,
  "status": "completed",
  "scene": { "_comment": "updated scene" },
  "reply": "Human-readable summary of what changed",
  "videoUrl": "https://.../output.mp4",
  "jobId": "1234567",
  "viral_clips": [],
  "zip_url": "https://.../clips.zip",
  "activeTasks": [],
  "pendingAsyncJobs": [],
  "verificationPassed": true,
  "verificationIssues": [],
  "workingMemory": { "_comment": "return this in the next call to resume approval-paused runs" }
}
```

Failure (HTTP 4xx/5xx): `{ "success": false, "error": "...", "code": "MISSING_PROMPT" }`.

`status` is one of `completed`, `failed`, `awaiting_approval`.

## Async job lifecycle

Generation actions (`generate_*`, `EXPORT_VIDEO`) return immediately with a `jobId` in `activeTasks` / `pendingAsyncJobs`. Poll:

```bash
curl -sS "$ADSCENE_API_URL/api/v1/misc/openclaw/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $ADSCENE_API_KEY" | jq '{status, progress, message, result}'
```

`status` is `queued` | `processing` | `completed` | `failed`. To harvest async-generated content into the timeline, issue an `autonomous_edit` prompt like `"apply any pending generated content"`.

## Plan-approval flow

With `requirePlanApproval: true`, the response carries `status: "awaiting_approval"` + a populated `workingMemory`. To proceed, call again with `params.prompt` = an approval phrase (`yes`, `approve`, `go ahead`, `do it`, `confirm`, …) and the returned `workingMemory`.

## Safety, verification, and limits

Every run flows through three deterministic gates (`ActionPermissionGate`, `ArchitectureControlPlane`, `EditorSafetyPolicy`). Destructive actions (`CLEAR`, mass deletes) require explicit confirmation params. Verification runs after execution and may trigger up to 2 repair loops; failures surface in `verificationPassed: false` + `verificationIssues[]`. Identical concurrent requests for the same `(user, project, prompt, scene fingerprint)` are deduplicated server-side. Rate-limited per API key. Read-only ~1–3s, structural edits ~3–10s, async generation 30s–5min per artifact, viral-clip / multi-platform exports several minutes.

## Supported formats

- **Video in**: MP4, MOV, WebM (HTTP/HTTPS URLs, YouTube URLs, gallery IDs)
- **Image in**: JPG, PNG, WebP
- **Audio in**: MP3, WAV, M4A, AAC (or extracted from video)
- **Output**: MP4 (export), ZIP (viral clips / multi-platform bundles)
- **Max video length**: up to ~3 hours per asset (plan-dependent); sync edits and async handles longer
- **Recommended resolution**: 1080p or 4K; canvas configurable per project

## Example: end-to-end viral-clip generation

```bash
# 1) Kick off the viral-clip pipeline (auto-export follow-up queues rendering)
curl -sS -X POST "$ADSCENE_API_URL/api/v1/misc/openclaw/v1/execute" \
  -H "Authorization: Bearer $ADSCENE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "autonomous_edit",
    "params": {
      "prompt": "Generate 5 viral clips, 15-30 seconds each, on the most engaging moments. Add bold captions, vertical reframe, remove silences."
    },
    "project_id": "my-project"
  }' | tee /tmp/levea_result.json | jq -r '.jobId // .activeTasks[0].intent.job_id'

# 2) Poll until done
JOB_ID=$(jq -r '.jobId // .activeTasks[0].intent.job_id' /tmp/levea_result.json)
while true; do
  STATUS=$(curl -sS "$ADSCENE_API_URL/api/v1/misc/openclaw/v1/jobs/$JOB_ID" \
    -H "Authorization: Bearer $ADSCENE_API_KEY" | jq -r '.status')
  echo "Status: $STATUS"
  { [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; } && break
  sleep 5
done

# 3) Fetch the final artifact URL(s)
curl -sS "$ADSCENE_API_URL/api/v1/misc/openclaw/v1/jobs/$JOB_ID" \
  -H "Authorization: Bearer $ADSCENE_API_KEY" | jq '.result'
```
