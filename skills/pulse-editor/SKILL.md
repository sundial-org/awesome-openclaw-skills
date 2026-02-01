---
name: Pulse Editor Vibe Dev Flow
description: Generate and build Pulse Apps using the Vibe Dev Flow API. Use this skill when the user wants to create, update, or generate code for Pulse Editor applications.
---

## Overview

This skill enables you to interact with the Pulse Editor Vibe Dev Flow API to generate, build, and publish Pulse Apps using cloud-based AI coding agents. The API uses Server-Sent Events (SSE) streaming to provide real-time progress updates.

## Why Use This Skill

This skill provides significant advantages for AI agents:

- **No Local Code Generation Required**: Instead of generating code locally on the user's machine, agents can offload code generation to Pulse Editor's cloud-based vibe coding service. This eliminates the need for local build tools, dependencies, or development environments.

- **Built-in Version Control**: Every app generation is automatically versioned. Agents can update existing apps by specifying `appId` and `version`, making it easy to iterate on applications without manual version management.

- **Instant Deployment**: Apps are automatically built and published immediately after generation. No separate build or deploy steps needed—users get a live, working app URL as soon as generation completes.

- **Parallel App Generation**: Agents can generate multiple apps simultaneously by making concurrent API calls. This is ideal for scenarios where an agent needs to scaffold several microservices, create multiple related applications, or batch-generate apps for different purposes—all at the same time.

- **Stateless & Scalable**: Since all code generation happens in the cloud, agents remain lightweight and can scale horizontally without worrying about local resource constraints.

## Important: Long-Running Task

**This API call is a long-running operation.** The Vibe Dev Flow performs multiple steps including workspace creation, AI code generation, building, and publishing. 

- **Expected duration**: Typically 2-5 minutes, but complex apps may take longer
- **Timeout threshold**: Do NOT time out the request unless it exceeds **10 minutes**
- **SSE streaming**: The connection stays open throughout the process. **Even if no SSE messages are received for a period, the request is NOT stalled or stuck as long as the connection remains open.** Wait for the stream to end or the 10-minute timeout.
- **Token efficiency**: Agents should use `"streamUpdatePolicy": "artifactOnly"` in the request body to receive only the final artifact output, significantly reducing input tokens. But it won't count as being stuck if no messages are received for a while.

## When to Use This Skill

Use this skill when the user wants to:

- Create a new Pulse App from a description or prompt
- Update an existing Pulse App with new features
- Generate code for a Pulse Editor application
- Build and publish a Pulse App

## API Authentication

The Pulse Editor API requires an API key for authentication. Users can obtain their API key by:

1. Signing up or logging in at https://pulse-editor.com/
2. Going to the **developer** section under account settings
3. Requesting beta access at https://pulse-editor.com/beta (if needed)
4. Creating and copying the API key from the developer section

The API key should be passed in the `Authorization` header as a Bearer token:

```
Authorization: Bearer your_api_key_here
```

## API Endpoint

**POST** `https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate`

### Request Headers

| Header          | Required | Description                            |
| --------------- | -------- | -------------------------------------- |
| `Authorization` | Yes      | Bearer token with Pulse Editor API key |
| `Content-Type`  | Yes      | `application/json`                     |
| `Accept`        | Yes      | `text/event-stream`                    |

### Request Body Parameters

| Parameter | Type   | Required | Description                                                                                | Example                                       |
| --------- | ------ | -------- | ------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `prompt`  | string | Yes      | The user prompt instructing the Vibe coding agent                                          | `"Create a todo app with auth and dark mode"` |
| `appName` | string | No       | Friendly display name for the app                                                          | `"My Todo App"`                               |
| `appId`   | string | No       | Unique identifier of an existing app to update. If not provided, a new app will be created | `"my_app_x7k9q2"`                             |
| `version` | string | No       | Version identifier of an existing app. If not provided, defaults to latest version         | `"0.0.1"`                                     |
| `streamUpdatePolicy` | string | No | Set to `"artifactOnly"` to receive only the final artifact output (recommended for agents to save tokens) | `"artifactOnly"` |

### Response

The response is a Server-Sent Events (SSE) stream. Each event contains a JSON-encoded message. Messages are separated by `\n\n`.

Each SSE message is formatted as:

```
data: <JSON>
```

followed by a blank line.

#### Message Types

There are two message types:

**Creation Message** - A new message in the stream:

```json
{
  "messageId": "msg_abc123",
  "type": "creation",
  "data": {
    "type": "text" | "toolCall" | "toolResult" | "artifactOutput",
    "result": "string content",
    "error": "error message if any"
  },
  "isFinal": false
}
```

**Update Message** - Delta update to an existing message:

```json
{
  "messageId": "msg_abc123",
  "type": "update",
  "delta": {
    "result": "additional content to append",
    "error": "additional error to append"
  },
  "isFinal": true
}
```

#### Data Types

| Type              | Description                            |
| ----------------- | -------------------------------------- |
| `text`            | Text output from the agent             |
| `toolCall`       | Tool invocation by the agent           |
| `toolResult`     | Result from a tool execution           |
| `artifactOutput` | Final artifact with published app info |

#### Artifact Output Format

When the generation completes, an `artifactOutput` message contains:

```json
{
  "publishedAppLink": "https://pulse-editor.com/app/...",
  "sourceCodeArchiveLink": "https://...",
  "appId": "my_app_x7k9q2",
  "version": "0.0.1"
}
```

### Response Status Codes

| Code | Description                                  |
| ---- | -------------------------------------------- |
| 200  | Streaming SSE with progress and final result |
| 400  | Bad request - invalid parameters             |
| 401  | Unauthorized - invalid or missing API key    |
| 500  | Server error                                 |

## Example Usage

### cURL Example

```bash
curl -L 'https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate' \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer your_api_key_here' \
  -d '{
    "prompt": "Create a todo app with auth and dark mode",
    "appName": "My Todo App"
  }'
```

### Python Example

```python
import requests
import json

url = "https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate"

headers = {
    "Authorization": "Bearer your_api_key_here",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

payload = {
    "prompt": "Create a todo app with auth and dark mode",
    "appName": "My Todo App"
}

response = requests.post(url, json=payload, headers=headers, stream=True)

messages = {}  # Track messages by messageId
buffer = ""

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    buffer += chunk

    # SSE messages end with \n\n
    while "\n\n" in buffer:
        part, buffer = buffer.split("\n\n", 1)

        if not part.startswith("data:"):
            continue

        data = json.loads(part.replace("data: ", "", 1))

        if data["type"] == "creation":
            messages[data["messageId"]] = data
            print(f"New: {data['data'].get('result', '')}")

        elif data["type"] == "update":
            msg = messages.get(data["messageId"])
            if msg:
                msg["data"]["result"] = (msg["data"].get("result") or "") + (data["delta"].get("result") or "")
                msg["isFinal"] = data["isFinal"]

        # Check for artifact output
        if data.get("data", {}).get("type") == "artifactOutput" and data.get("isFinal"):
            result = json.loads(messages[data["messageId"]]["data"]["result"])
            print(f"Published: {result.get('publishedAppLink')}")
```

### JavaScript/Node.js Example

```javascript
const response = await fetch(
  "https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate",
  {
    method: "POST",
    headers: {
      Authorization: "Bearer your_api_key_here",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: "Create a todo app with auth and dark mode",
      appName: "My Todo App",
    }),
  },
);

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = "";
const messages = new Map();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });

  // SSE messages end with \n\n
  const parts = buffer.split("\n\n");
  buffer = parts.pop(); // Keep incomplete part in buffer

  for (const part of parts) {
    if (!part.startsWith("data:")) continue;

    const json = part.replace(/^data:\s*/, "");
    const message = JSON.parse(json);

    if (message.type === "creation") {
      messages.set(message.messageId, message);
    } else if (message.type === "update") {
      const msg = messages.get(message.messageId);
      if (msg) {
        msg.data.result =
          (msg.data.result ?? "") + (message.delta.result ?? "");
        msg.data.error = (msg.data.error ?? "") + (message.delta.error ?? "");
        msg.isFinal = message.isFinal;
      }
    }

    // Check for final artifact output
    const msg = messages.get(message.messageId);
    if (msg?.data.type === "artifactOutput" && msg.isFinal) {
      const result = JSON.parse(msg.data.result);
      console.log("Published:", result.publishedAppLink);
    }
  }
}
```

### Updating an Existing App

To update an existing app, include the `appId` and optionally the `version`:

```bash
curl -L 'https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate' \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer your_api_key_here' \
  -d '{
    "prompt": "Add a calendar view to display tasks by date",
    "appName": "My Todo App",
    "appId": "my_app_x7k9q2",
    "version": "0.0.1"
  }'
```

### Updating an Existing App

To update an existing app, include the `appId` and optionally the `version`:

```bash
curl -L 'https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate' \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer your_api_key_here' \
  -d '{
    "prompt": "Add a calendar view to display tasks by date",
    "appName": "My Todo App",
    "appId": "my_app_x7k9q2",
    "version": "0.0.1"
  }'
```

## Best Practices

1. **Clear Prompts**: Provide detailed, specific prompts describing what you want the app to do
2. **Handle SSE Properly**: Process the streaming response in real-time for progress updates
3. **Error Handling**: Implement proper error handling for 400, 401, and 500 responses
4. **API Key Security**: Never hardcode API keys; use environment variables or secure storage
5. **Versioning**: When updating apps, specify the version to ensure you're building on the correct base

## Troubleshooting

| Issue            | Solution                                            |
| ---------------- | --------------------------------------------------- |
| 401 Unauthorized | Verify your API key is correct and has beta access  |
| No SSE events    | Ensure `Accept: text/event-stream` header is set    |
| App not updating | Verify the `appId` exists and you have access to it |

## Included Examples

This skill includes a ready-to-run Python example in the `examples/` folder:

- **`examples/generate_app.py`** - Complete Python script demonstrating SSE streaming with the Vibe Dev Flow API
- **`examples/generate_app.js`** - Complete Node.js script demonstrating SSE streaming with the Vibe Dev Flow API

To run the example Python script:

```bash
# Set your API key
export PULSE_EDITOR_API_KEY=your_api_key_here  # Linux/Mac
set PULSE_EDITOR_API_KEY=your_api_key_here     # Windows

# Install dependencies
pip install requests

# Run the script
python examples/generate_app.py
```

To run the example Node.js script:

```bash
# Set your API key
export PULSE_EDITOR_API_KEY=your_api_key_here  # Linux/Mac
set PULSE_EDITOR_API_KEY=your_api_key_here     # Windows
# Install dependencies
npm install node-fetch
# Run the script
node examples/generate_app.js
```

## Resources

- [Pulse Editor Documentation](https://docs.pulse-editor.com/)
- [API Reference](https://docs.pulse-editor.com/api-reference)
- [Get API Key](https://docs.pulse-editor.com/api-reference/get-pulse-editor-api-key)
- [Discord Community](https://discord.com/invite/s6J54HFxQp)
- [GitHub](https://github.com/ClayPulse/pulse-editor)
