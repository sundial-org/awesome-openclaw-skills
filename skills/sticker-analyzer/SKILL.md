---
name: sticker-analyzer
description: Analyze images in media/stickers using Vision API to identify and filter meme/sticker content vs screenshots or documents.
tags: [vision, image-analysis, stickers, memes]
---

# Sticker Analyzer Skill

Analyzes images in `media/stickers` using Google Gemini Vision API to filter out non-stickers (screenshots, documents).

## Tools

### analyze_stickers
Runs the analysis script.

- No arguments required. Scans `~/.openclaw/media/stickers`.

## Setup
1.  Requires `npm install @google/generative-ai`.
2.  Requires a valid Google AI Studio API Key in `.env` (GEMINI_API_KEY).

## Status
Active. Configured with Gemini 2.5 Flash for high-speed sticker filtering.
