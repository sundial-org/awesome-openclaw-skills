#!/usr/bin/env node

/**
 * LM Studio v1 REST API (POST /api/v1/chat)
 *
 * Calls LM Studio chat endpoint and parses v1 response.
 * Usage: node scripts/lmstudio-api.mjs <model> '<task>' [--temperature=0.7] [--max-output-tokens=2000] [--previous-response-id=resp_xxx] [--api-url=http://127.0.0.1:1234]
 */

const BASE_URL = process.env.LM_STUDIO_API_URL || 'http://127.0.0.1:1234';

async function callLMStudioAPI(model, taskContent, options = {}) {
  const {
    temperature = 0.7,
    maxOutputTokens = 2000,
    previousResponseId = null,
    apiUrl = BASE_URL
  } = options;

  const url = `${apiUrl.replace(/\/$/, '')}/api/v1/chat`;
  const payload = {
    model,
    input: taskContent,
    store: true,
    temperature: parseFloat(temperature),
    max_output_tokens: parseInt(maxOutputTokens)
  };
  if (previousResponseId) payload.previous_response_id = previousResponseId;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer lmstudio'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.error?.message || data.message || `HTTP ${response.status}`;
      console.error(JSON.stringify({ error: errorMsg, type: data.error?.type || 'api_error' }));
      process.exit(1);
    }

    if (!data.output || !Array.isArray(data.output)) {
      console.error(JSON.stringify({ error: 'Invalid API response structure', data }));
      process.exit(1);
    }

    const messages = data.output
      .filter(item => item.type === 'message')
      .map(item => item.content)
      .join('')
      .trim();

    const reasoning = data.output
      .filter(item => item.type === 'reasoning')
      .map(item => item.content)
      .join('')
      .trim();

    // Prefer normal assistant message content; fallback for "thinking" models
    // that only emit reasoning items.
    const content = (messages && messages.length > 0)
      ? messages
      : (reasoning || '');

    const result = {
      content,
      content_source: (messages && messages.length > 0) ? 'message' : 'reasoning',
      model_instance_id: data.model_instance_id || null,
      response_id: data.response_id || null,
      usage: data.stats ? {
        input_tokens: data.stats.input_tokens,
        total_output_tokens: data.stats.total_output_tokens,
        model_load_time_seconds: data.stats.model_load_time_seconds
      } : null
    };

    console.log(JSON.stringify(result));
    return result;

  } catch (error) {
    console.error(JSON.stringify({
      error: error.message,
      type: 'network_error',
      url
    }));
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [model, taskContent, ...args] = process.argv.slice(2);

  if (!model || !taskContent) {
    console.error('Usage: node scripts/lmstudio-api.mjs <model> \'<task>\' [--temperature=0.7] [--max-output-tokens=2000] [--previous-response-id=resp_xxx] [--api-url=http://127.0.0.1:1234]');
    process.exit(1);
  }

  const options = {};
  args.forEach(arg => {
    if (arg.startsWith('--temperature=')) {
      options.temperature = arg.split('=')[1];
    } else if (arg.startsWith('--max-output-tokens=')) {
      options.maxOutputTokens = arg.split('=')[1];
    } else if (arg.startsWith('--previous-response-id=')) {
      options.previousResponseId = arg.split('=')[1];
    } else if (arg.startsWith('--api-url=')) {
      options.apiUrl = arg.split('=')[1];
    }
  });

  callLMStudioAPI(model, taskContent, options).catch(err => {
    console.error(JSON.stringify({ error: err.message, type: 'unexpected_error' }));
    process.exit(1);
  });
}

export { callLMStudioAPI };
