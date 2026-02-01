# AI SDK UI - Top 18 Errors & Solutions

Common AI SDK UI errors with actionable solutions.

**Last Updated**: 2026-01-20

---

## 1. useChat Failed to Parse Stream

**Error**: `SyntaxError: Unexpected token in JSON at position X`

**Cause**: API route not returning proper stream format.

**Solution**:
```typescript
// ✅ CORRECT (App Router)
export async function POST(req: Request) {
  const result = streamText({ /* ... */ });
  return result.toDataStreamResponse();  // Correct method
}

// ✅ CORRECT (Pages Router)
export default async function handler(req, res) {
  const result = streamText({ /* ... */ });
  return result.pipeDataStreamToResponse(res);  // Correct method
}

// ❌ WRONG
return new Response(result.textStream);  // Missing stream protocol
```

---

## 2. useChat No Response

**Cause**: API route not streaming correctly or wrong method.

**Solution**:
```typescript
// Check 1: Are you using the right method?
// App Router: toDataStreamResponse()
// Pages Router: pipeDataStreamToResponse()

// Check 2: Is your API route returning a Response?
export async function POST(req: Request) {
  const result = streamText({ model: openai('gpt-5'), messages });
  return result.toDataStreamResponse();  // Must return this!
}

// Check 3: Check network tab - is the request completing?
// If status is 200 but no data: likely streaming issue
```

---

## 3. Unclosed Streams

**Cause**: Stream not properly closed in API.

**Solution**:
```typescript
// ✅ GOOD: SDK handles closing automatically
export async function POST(req: Request) {
  const result = streamText({ model: openai('gpt-5'), messages });
  return result.toDataStreamResponse();
}

// ❌ BAD: Manual stream handling (error-prone)
const encoder = new TextEncoder();
const stream = new ReadableStream({
  async start(controller) {
    // ...must manually close!
    controller.close();
  }
});
```

**GitHub Issue**: #4123

---

## 4. Streaming Not Working When Deployed

**Cause**: Deployment platform buffering responses.

**Solution**:
- **Vercel**: Auto-detects streaming (no config needed)
- **Netlify**: Ensure Edge Functions enabled
- **Cloudflare Workers**: Use `toDataStreamResponse()`
- **Other platforms**: Check for response buffering settings

```typescript
// Vercel - works out of the box
export async function POST(req: Request) {
  const result = streamText({ /* ... */ });
  return result.toDataStreamResponse();
}
```

**Docs**: https://vercel.com/docs/functions/streaming

---

## 5. Streaming Not Working When Proxied

**Cause**: Proxy (nginx, Cloudflare, etc.) buffering responses.

**Solution**:

**Nginx**:
```nginx
location /api/ {
    proxy_pass http://localhost:3000;
    proxy_buffering off;  # Disable buffering
    proxy_cache off;
}
```

**Cloudflare**: Disable "Auto Minify" in dashboard

---

## 6. Strange Stream Output (0:... characters)

**Error**: Seeing raw stream protocol like `0:"Hello"` in browser.

**Cause**: Not using correct hook or consuming stream directly.

**Solution**:
```tsx
// ✅ CORRECT: Use useChat hook
const { messages } = useChat({ api: '/api/chat' });

// ❌ WRONG: Consuming stream directly
const response = await fetch('/api/chat');
const reader = response.body.getReader();  // Don't do this!
```

---

## 7. Stale Body Values with useChat

**Error**: API receives outdated values for dynamic context (user ID, session data, feature flags)

**Source**: [GitHub Issue #7819](https://github.com/vercel/ai/issues/7819)

**Cause**: `body` and transport options captured at first render only. The `useChat` hook stores options in a `useRef` that only updates if the `id` prop changes. The `shouldRecreateChat` check doesn't detect deep option changes.

**Solution 1 (Recommended by maintainer)**: Pass data in `sendMessage`
```tsx
const { userId } = useUser();
const { messages, sendMessage } = useChat();

sendMessage({
  content: input,
  data: { userId },  // ✅ Fresh value on each send
});
```

**Solution 2**: Use `useRef` for dynamic transport
```tsx
const bodyRef = useRef(body);
bodyRef.current = body; // Update on each render

useChat({
  transport: new DefaultChatTransport({
    body: () => bodyRef.current, // ✅ Always fresh
  }),
});
```

**Solution 3**: Change `useChat` id to force recreation (not recommended)
```tsx
useChat({
  id: `${sessionId}-${taskId}-${userId}`, // Forces recreation on changes
  body: { taskId, userId },
});
```

**Maintainer Note**: "We are aware that this is a problem. We just couldn't prioritize it yet, sorry. At least there is a workaround, albeit gross 😁" - @gr2m

**Related Issues**: [#11686](https://github.com/vercel/ai/issues/11686) (stale closures in onData/onFinish), [#8956](https://github.com/vercel/ai/issues/8956) (transport doesn't update)

---

## 8. Custom Headers Not Working with useChat

**Cause**: Headers not passed correctly.

**Solution**:
```tsx
// ✅ CORRECT
const { messages } = useChat({
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Custom-Header': 'value',
  },
});

// OR use fetch options
const { messages } = useChat({
  fetch: (url, options) => {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      },
    });
  },
});
```

---

## 9. React Maximum Update Depth

**Error**: `Maximum update depth exceeded`

**Cause**: Infinite loop in useEffect.

**Solution**:
```tsx
// ❌ BAD: Infinite loop
const saveMessages = (messages) => { /* ... */ };

useEffect(() => {
  saveMessages(messages);
}, [messages, saveMessages]);  // saveMessages changes every render!

// ✅ GOOD: Only depend on messages
useEffect(() => {
  localStorage.setItem('messages', JSON.stringify(messages));
}, [messages]);  // saveMessages not needed in deps
```

---

## 10. Repeated Assistant Messages

**Cause**: Duplicate message handling or multiple sendMessage calls.

**Solution**:
```tsx
// ❌ BAD: Calling sendMessage multiple times
const handleSubmit = (e) => {
  e.preventDefault();
  sendMessage({ content: input });
  sendMessage({ content: input });  // Duplicate!
};

// ✅ GOOD: Single call
const handleSubmit = (e) => {
  e.preventDefault();
  if (!input.trim()) return;  // Guard
  sendMessage({ content: input });
  setInput('');
};
```

---

## 11. onFinish Not Called When Stream Aborted

**Cause**: Stream abort doesn't trigger onFinish callback.

**Solution**:
```tsx
const { stop } = useChat({
  onFinish: (message) => {
    console.log('Finished:', message);
  },
});

// Handle abort separately
const handleStop = () => {
  stop();
  console.log('Stream aborted by user');
  // Do cleanup here
};
```

---

## 12. Type Error with Message Parts (v5)

**Error**: `Property 'parts' does not exist on type 'Message'`

**Cause**: v5 changed message structure for tool calls.

**Solution**:
```tsx
// ✅ CORRECT (v5)
messages.map(message => {
  // Use content for simple messages
  if (message.content) {
    return <div>{message.content}</div>;
  }

  // Use toolInvocations for tool calls
  if (message.toolInvocations) {
    return message.toolInvocations.map(tool => (
      <div key={tool.toolCallId}>
        Tool: {tool.toolName}
      </div>
    ));
  }
});

// ❌ WRONG (v4 style)
message.toolCalls  // Doesn't exist in v5
```

---

## 13. TypeError with resume: true and onFinish

**Error**: `TypeError: Cannot read properties of undefined (reading 'state')`

**Source**: [GitHub Issue #8477](https://github.com/vercel/ai/issues/8477)

**Cause**: When using `resume: true` with an `onFinish` callback, navigating away mid-stream and then resuming causes `this.activeResponse` to become undefined. This happens because concurrent `makeRequest` calls overwrite the reference.

**Reproduction**:
```tsx
const { messages, sendMessage } = useChat({
  api: '/api/chat',
  resume: true,
  onFinish: (message) => {
    console.log('Finished:', message);
  },
});

// 1. Start streaming
// 2. Navigate to new page
// 3. Resume stream → TypeError
```

**Workaround**: Use patch-package to capture `activeResponse` locally in the finally block:
```typescript
// In ai package (dist/index.mjs)
let activeResponse;
try {
  activeResponse = {
    state: createStreamingUIMessageState({ /* ... */ })
  };
  // ... rest of makeRequest
} finally {
  if (activeResponse) { // ✅ Check before accessing
    this.onFinish?.call(this, {
      message: activeResponse.state.message,
      // ...
    });
  }
}
```

**Status**: A PR was opened (#8689) but closed without explanation. Community using patch-package workaround.

---

## 14. Concurrent sendMessage Calls Cause State Corruption

**Error**: `TypeError: Cannot read properties of undefined (reading 'state')`

**Source**: [GitHub Issue #11024](https://github.com/vercel/ai/issues/11024)

**Cause**: Calling `sendMessage()` before the previous request finishes streaming overwrites `this.activeResponse`, causing state corruption. The SDK doesn't guard against concurrent requests.

**Reproduction**:
```tsx
const { sendMessage, isLoading } = useChat();

// Rapid double-click or programmatic double-send
sendMessage({ content: 'First' });
sendMessage({ content: 'Second' }); // ❌ Overwrites activeResponse
```

**Solution**: Guard against concurrent sends
```tsx
const [isSending, setIsSending] = useState(false);

const handleSend = async (content: string) => {
  if (isSending) return; // ✅ Block concurrent calls
  setIsSending(true);
  try {
    await sendMessage({ content });
  } finally {
    setIsSending(false);
  }
};
```

**Maintainer Response**: "Simply restrict sending request until in flight requests finish streaming response"

---

## 15. Tool Approval with onFinish Callback Breaks Workflow

**Error**: TypeError when calling `sendMessage()` or `regenerate()` inside callbacks

**Source**: [GitHub Issue #10169](https://github.com/vercel/ai/issues/10169)

**Cause**: When using `needsApproval` tools with `onFinish` or `onError` callbacks, calling `sendMessage()` or `regenerate()` inside the callback triggers the TypeError from Issue #13. The callback runs synchronously within stream finalization, and re-entering `makeRequest` corrupts `activeResponse`.

**Reproduction**:
```tsx
const { sendMessage, regenerate } = useChat({
  onFinish: () => {
    void sendMessage({ content: 'Continue...' }); // ❌ Breaks
  },
  onError: () => {
    void regenerate(); // ❌ Breaks
  },
});
```

**Solution**: Defer the call to next tick
```tsx
const { sendMessage } = useChat({
  onFinish: () => {
    queueMicrotask(() => {
      void sendMessage({ content: 'Continue...' }); // ✅ Works
    });
  },
});
```

---

## 16. ZodError "Message must contain at least one part" When Stopping Stream Early

**Error**: `ZodError: Message must contain at least one part`

**Source**: [GitHub Issue #11444](https://github.com/vercel/ai/issues/11444)

**Cause**: When using `createAgentUIStreamResponse` with `validateUIMessage`, calling `stop()` before the AI generates any response parts creates an empty assistant message. The validation function requires at least one part.

**Reproduction**:
```tsx
const { messages, stop } = useChat({
  api: '/api/chat', // Uses createAgentUIStreamResponse + validateUIMessage
});

// User stops immediately after sending
stop(); // ❌ ZodError if no parts generated yet
```

**Solution**: Filter out empty messages before validation
```typescript
// In API route
const filteredMessages = messages.filter(m => m.parts && m.parts.length > 0);
const validMessages = validateUIMessages(filteredMessages);
```

**Maintainer Response**: Suggested filtering empty messages before sending to `validateUIMessages`.

---

## 17. convertToModelMessages Fails with Tool Approval Parts

**Error**: `Error: no tool invocation found for tool call [id]`

**Source**: [GitHub Issue #9968](https://github.com/vercel/ai/issues/9968)

**Cause**: When using `convertToModelMessages` with messages containing tool approval parts (`tool-approval-request`, `tool-approval-response`), the function doesn't properly handle the three-part approval flow structure.

**Reproduction**:
```tsx
const tools = { myTool };
const convertedMessages = convertToModelMessages(messages, { tools });

// ❌ Error: no tool invocation found for tool call toolu_123
// Message structure:
// - tool-call part
// - tool-approval-request part
// - tool-approval-response part (approved: true)
// - (expects tool-result but conversion fails before that)
```

**Status**: Issue is still open. Maintainer suggested passing tools in second arg but multiple users confirm it doesn't fix the issue.

**Additional Symptom**: UI shows duplicate assistant messages with same message ID when this error occurs.

---

## 18. Passing undefined id to useChat Causes Infinite Rerenders

**Error**: Component enters infinite rerender loop

**Source**: [GitHub Issue #8087](https://github.com/vercel/ai/issues/8087) (Community-sourced)

**Cause**: Passing `id: undefined` to `useChat` causes infinite rerenders. This can happen accidentally when using conditional logic to compute the id.

**Reproduction**:
```tsx
const chatId = someCondition ? 'chat-123' : undefined;
useChat({ id: chatId }); // ❌ Infinite loop if undefined
```

**Solution**: Always provide a stable id
```tsx
const chatId = someCondition ? 'chat-123' : 'default';
useChat({ id: chatId }); // ✅
```

**Verification**: Single report, matches expected behavior of useRef with undefined key.

---

## For More Errors

See complete error reference (28 total types):
https://ai-sdk.dev/docs/reference/ai-sdk-errors

---

**Last Updated**: 2026-01-20
