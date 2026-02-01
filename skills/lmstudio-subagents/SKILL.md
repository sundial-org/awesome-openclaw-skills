---
name: lmstudio-subagents
description: "Reduces token usage from paid providers by offloading work to local LM Studio models. Use when: (1) Cutting costs—use local models for summarization, extraction, classification, rewriting, first-pass review, brainstorming when quality suffices, (2) Avoiding paid API calls for high-volume or repetitive tasks, (3) No extra model configuration—JIT loading and REST API work with existing LM Studio setup, (4) Local-only or privacy-sensitive work. Requires LM Studio 0.4+ with server (default :1234). No CLI required."
metadata: {"openclaw":{"requires":{},"tags":["local-model","local-llm","lm-studio","token-management","privacy","subagents"]}}
license: MIT
---

# LM Studio Models

Offload tasks to local models when quality suffices; avoid web/proprietary/high-stakes.

## Key Terms

- **model**: From GET models key; use in chat and optional load.
- **lm_studio_api_url**: Default http://127.0.0.1:1234 (paths /api/v1/...).
- **response_id** / **previous_response_id**: Chat returns response_id; pass as previous_response_id for stateful.
- **instance_id**: loaded_instances[].id or model_instance_id; for unload.

Trigger in frontmatter; below = implementation.

## Prerequisites

LM Studio 0.4+, server :1234, models on disk; load/unload via API (JIT optional); Node for script (curl ok).

## Complete Workflow

### Step 0: Preflight

GET <base>/api/v1/models; non-200 or connection error = server not ready.

```bash
exec command:"curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer lmstudio' http://127.0.0.1:1234/api/v1/models"
```

### Step 1: List Models and Check Loaded

```bash
exec command:"curl -s -H 'Authorization: Bearer lmstudio' http://127.0.0.1:1234/api/v1/models"
```

Parse models[] (key, type, loaded_instances, max_context_length, capabilities, params_string). If a model has loaded_instances.length > 0 and fits task, skip to Step 5; else pick key for chat (and optional load). Note loaded_instances[].id for optional unload.

### Step 2: Model Selection

Pick key from GET response; use as model in chat (optional load). Constraints: vision -> capabilities.vision; embedding -> type=embedding; context -> max_context_length. Prefer loaded (loaded_instances non-empty), smaller for speed/larger for reasoning; fallback primary. Optional POST load; else JIT on first chat.

### Step 3: Load Model (optional)

Optional: POST /api/v1/models/load { model, context_length?, ... }. JIT: first chat loads; explicit load only for specific options.

### Step 4: Verify Loaded (optional)

If explicit load: GET models, confirm loaded_instances. If JIT: no verify; first chat returns model_instance_id, stats.model_load_time_seconds.

### Step 5: Call API

From the skill folder: node scripts/lmstudio-api.mjs &lt;model&gt; '&lt;task&gt;' [options].

```bash
exec command:"node scripts/lmstudio-api.mjs <model> '<task>' --temperature=0.7 --max-output-tokens=2000"
```

Stateful: add --previous-response-id=<response_id>. Curl: POST <base>/api/v1/chat, body model, input, store, temperature, max_output_tokens; optional previous_response_id. Parse: output (type message) -> content; response_id, model_instance_id, stats. Script outputs content, model_instance_id, response_id, usage.

### Step 6: Unload (optional)

Optional: POST /api/v1/models/unload { instance_id }. instance_id from loaded_instances[].id or chat model_instance_id. JIT+TTL auto-unload; explicit when needed.

```bash
exec command:"curl -s -X POST http://127.0.0.1:1234/api/v1/models/unload -H 'Content-Type: application/json' -H 'Authorization: Bearer lmstudio' -d '{\"instance_id\": \"<instance_id>\"}'"
```

## Error Handling

- Model not found -> pick another model from GET response.
- API/server errors -> GET models, check URL.
- Invalid output -> retry.
- Memory -> unload or smaller model.
- Unload fails -> instance_id must match loaded_instances[].id.

## Examples

GET /api/v1/models, then script with model key and task. Optional unload per Step 6 (instance_id from response or GET).

```bash
exec command:"curl -s -H 'Authorization: Bearer lmstudio' http://127.0.0.1:1234/api/v1/models"
exec command:"node scripts/lmstudio-api.mjs meta-llama-3.1-8b-instruct 'Summarize and extract 5 key points' --temperature=0.7 --max-output-tokens=2000"
```

## LM Studio API Details

Helper/API: see Step 5. Output: content, model_instance_id, response_id, usage. Auth: Bearer lmstudio. List GET /api/v1/models. Load POST /api/v1/models/load (optional). Unload POST /api/v1/models/unload { instance_id }.

## Notes

- LM Studio 0.4+.
- JIT (first chat loads; model_load_time_seconds in stats); stateful (response_id / previous_response_id).
