---
name: ai-sdk-ui
description: |
  Build React chat interfaces with Vercel AI SDK v6. Covers useChat/useCompletion/useObject hooks, message parts structure, tool approval workflows, and 18 UI error solutions. Prevents documented issues with React Strict Mode, concurrent requests, stale closures, and tool approval edge cases.

  Use when: implementing AI chat UIs, migrating v5→v6, troubleshooting "useChat failed to parse stream", "stale body values", "React maximum update depth", "Cannot read properties of undefined (reading 'state')", or tool approval workflow errors.
user-invocable: true
---

# AI SDK UI - Frontend React Hooks

Frontend React hooks for AI-powered user interfaces with Vercel AI SDK v6.

**Version**: AI SDK v6.0.42 (Stable)
**Framework**: React 18+/19, Next.js 14+/15+
**Last Updated**: 2026-01-20

---

## AI SDK v6 Stable (January 2026)

**Status:** Stable Release
**Latest:** ai@6.0.42, @ai-sdk/react@3.0.44, @ai-sdk/openai@3.0.7
**Migration:** Minimal breaking changes from v5 → v6

### New UI Features in v6

**1. Message Parts Structure (Breaking Change)**
In v6, message content is now accessed via `.parts` array instead of `.content`:

```tsx
// ❌ v5 (OLD)
{messages.map(m => (
  <div key={m.id}>{m.content}</div>
))}

// ✅ v6 (NEW)
{messages.map(m => (
  <div key={m.id}>
    {m.parts.map((part, i) => {
      if (part.type === 'text') return <span key={i}>{part.text}</span>;
      if (part.type === 'tool-invocation') return <ToolCall key={i} tool={part} />;
      if (part.type === 'file') return <FilePreview key={i} file={part} />;
      return null;
    })}
  </div>
))}
```

**Part Types:**
- `text` - Text content with `.text` property
- `tool-invocation` - Tool calls with `.toolName`, `.args`, `.result`
- `file` - File attachments with `.mimeType`, `.data`
- `reasoning` - Model reasoning (when available)
- `source` - Source citations

**3. Agent Integration**
Type-safe messaging with agents using `InferAgentUIMessage<typeof agent>`:

```tsx
import { useChat } from '@ai-sdk/react';
import type { InferAgentUIMessage } from 'ai';
import { myAgent } from './agent';

export default function AgentChat() {
  const { messages, sendMessage } = useChat<InferAgentUIMessage<typeof myAgent>>({
    api: '/api/chat',
  });
  // messages are now type-checked against agent schema
}
```

**4. Tool Approval Workflows (Human-in-the-Loop)**
Request user confirmation before executing tools:

```tsx
import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export default function ChatWithApproval() {
  const { messages, sendMessage, addToolApprovalResponse } = useChat({
    api: '/api/chat',
  });

  const handleApprove = (toolCallId: string) => {
    addToolApprovalResponse({
      toolCallId,
      approved: true,  // or false to deny
    });
  };

  return (
    <div>
      {messages.map(message => (
        <div key={message.id}>
          {message.toolInvocations?.map(tool => (
            tool.state === 'awaiting-approval' && (
              <div key={tool.toolCallId}>
                <p>Approve tool call: {tool.toolName}?</p>
                <button onClick={() => handleApprove(tool.toolCallId)}>
                  Approve
                </button>
                <button onClick={() => addToolApprovalResponse({
                  toolCallId: tool.toolCallId,
                  approved: false
                })}>
                  Deny
                </button>
              </div>
            )
          ))}
        </div>
      ))}
    </div>
  );
}
```

**5. Auto-Submit Capability**
Automatically continue conversation after handling approvals:

```tsx
import { useChat, lastAssistantMessageIsCompleteWithApprovalResponses } from '@ai-sdk/react';

export default function AutoSubmitChat() {
  const { messages, sendMessage } = useChat({
    api: '/api/chat',
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithApprovalResponses,
    // Automatically resubmit after all approval responses provided
  });
}
```

**6. Structured Output in Chat**
Generate structured data alongside tool calling (previously only available in `useObject`):

```tsx
import { useChat } from '@ai-sdk/react';
import { z } from 'zod';

const schema = z.object({
  summary: z.string(),
  sentiment: z.enum(['positive', 'neutral', 'negative']),
});

export default function StructuredChat() {
  const { messages, sendMessage } = useChat({
    api: '/api/chat',
    // Server can now stream structured output with chat messages
  });
}
```

---

## useChat Hook - v4 → v5 Breaking Changes

**CRITICAL: useChat no longer manages input state in v5!**

**v4 (OLD - DON'T USE):**
```tsx
const { messages, input, handleInputChange, handleSubmit, append } = useChat();

<form onSubmit={handleSubmit}>
  <input value={input} onChange={handleInputChange} />
</form>
```

**v5 (NEW - CORRECT):**
```tsx
const { messages, sendMessage } = useChat();
const [input, setInput] = useState('');

<form onSubmit={(e) => {
  e.preventDefault();
  sendMessage({ content: input });
  setInput('');
}}>
  <input value={input} onChange={(e) => setInput(e.target.value)} />
</form>
```

**Summary of v5 Changes:**
1. **Input management removed**: `input`, `handleInputChange`, `handleSubmit` no longer exist
2. **`append()` → `sendMessage()`**: New method for sending messages
3. **`onResponse` removed**: Use `onFinish` instead
4. **`initialMessages` → controlled mode**: Use `messages` prop for full control
5. **`maxSteps` removed**: Handle on server-side only

See `references/use-chat-migration.md` for complete migration guide.

---

## useAssistant Hook (Deprecated)

> **⚠️ Deprecation Notice**: `useAssistant` is deprecated as of AI SDK v5. OpenAI Assistants API v2
> will sunset on August 26, 2026. For new projects, use `useChat` with custom backend logic instead.
> See the **openai-assistants** skill for migration guidance.

Interact with OpenAI-compatible assistant APIs with automatic UI state management.

**Import:**
```tsx
import { useAssistant } from '@ai-sdk/react';
```

**Basic Usage:**
```tsx
'use client';
import { useAssistant } from '@ai-sdk/react';
import { useState, FormEvent } from 'react';

export default function AssistantChat() {
  const { messages, sendMessage, isLoading, error } = useAssistant({
    api: '/api/assistant',
  });
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage({ content: input });
    setInput('');
  };

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
      </form>
      {error && <div>{error.message}</div>}
    </div>
  );
}
```

**Use Cases:**
- Building OpenAI Assistant-powered UIs
- Managing assistant threads and runs
- Streaming assistant responses with UI state management
- File search and code interpreter integrations

See official docs for complete API reference: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-assistant

---

## Top UI Errors & Solutions

See `references/top-ui-errors.md` for complete documentation. Quick reference:

### 1. useChat Failed to Parse Stream

**Error**: `SyntaxError: Unexpected token in JSON at position X`

**Cause**: API route not returning proper stream format.

**Solution**:
```typescript
// ✅ CORRECT
return result.toDataStreamResponse();

// ❌ WRONG
return new Response(result.textStream);
```

### 2. useChat No Response

**Cause**: API route not streaming correctly.

**Solution**:
```typescript
// App Router - use toDataStreamResponse()
export async function POST(req: Request) {
  const result = streamText({ /* ... */ });
  return result.toDataStreamResponse(); // ✅
}

// Pages Router - use pipeDataStreamToResponse()
export default async function handler(req, res) {
  const result = streamText({ /* ... */ });
  return result.pipeDataStreamToResponse(res); // ✅
}
```

### 3. Streaming Not Working When Deployed

**Cause**: Deployment platform buffering responses.

**Solution**: Vercel auto-detects streaming. Other platforms may need configuration.

### 4. Stale Body Values with useChat

**Cause**: `body` option captured at first render only.

**Solution**:
```typescript
// ❌ WRONG - body captured once
const { userId } = useUser();
const { messages } = useChat({
  body: { userId },  // Stale!
});

// ✅ CORRECT - use controlled mode
const { userId } = useUser();
const { messages, sendMessage } = useChat();

sendMessage({
  content: input,
  data: { userId },  // Fresh on each send
});
```

### 5. React Maximum Update Depth

**Cause**: Infinite loop in useEffect.

**Solution**:
```typescript
// ❌ WRONG
useEffect(() => {
  saveMessages(messages);
}, [messages, saveMessages]); // saveMessages triggers re-render!

// ✅ CORRECT
useEffect(() => {
  saveMessages(messages);
}, [messages]); // Only depend on messages
```

See `references/top-ui-errors.md` for 13 more common errors (18 total documented).

---

## Streaming Best Practices

### Performance

**Always use streaming for better UX:**
```tsx
// ✅ GOOD - Streaming (shows tokens as they arrive)
const { messages } = useChat({ api: '/api/chat' });

// ❌ BAD - Non-streaming (user waits for full response)
const response = await fetch('/api/chat', { method: 'POST' });
```

### UX Patterns

**Show loading states:**
```tsx
{isLoading && <div>AI is typing...</div>}
```

**Provide stop button:**
```tsx
{isLoading && <button onClick={stop}>Stop</button>}
```

**Auto-scroll to latest message:**
```tsx
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
}, [messages]);
```

**Disable input while loading:**
```tsx
<input disabled={isLoading} />
```

See `references/streaming-patterns.md` for comprehensive best practices.

---

## React Strict Mode Considerations

React Strict Mode intentionally double-invokes effects to catch bugs. When using `useChat` or `useCompletion` in effects (auto-resume, initial messages), guard against double execution to prevent duplicate API calls and token waste.

**Problem:**
```tsx
'use client';
import { useChat } from '@ai-sdk/react';
import { useEffect } from 'react';

export default function Chat() {
  const { messages, sendMessage, resumeStream } = useChat({
    api: '/api/chat',
    resume: true,
  });

  useEffect(() => {
    // ❌ Triggers twice in strict mode → two concurrent streams
    sendMessage({ content: 'Hello' });
    // or
    resumeStream();
  }, []);
}
```

**Solution:**
```tsx
// ✅ Use ref to track execution
import { useRef } from 'react';

const hasSentRef = useRef(false);

useEffect(() => {
  if (hasSentRef.current) return;
  hasSentRef.current = true;

  sendMessage({ content: 'Hello' });
}, []);

// For resumeStream specifically:
const hasResumedRef = useRef(false);

useEffect(() => {
  if (!autoResume || hasResumedRef.current || status === 'streaming') return;
  hasResumedRef.current = true;
  resumeStream();
}, [autoResume, resumeStream, status]);
```

**Why It Happens:** React Strict Mode double-invokes effects to surface side effects. The SDK doesn't guard against concurrent requests, so both invocations create separate streams that fight for state updates.

**Impact:** Duplicate messages, doubled token usage, race conditions causing TypeError: "Cannot read properties of undefined (reading 'state')".

**Source:** [GitHub Issue #7891](https://github.com/vercel/ai/issues/7891), [Issue #6166](https://github.com/vercel/ai/issues/6166)

---

## When to Use This Skill

### Use ai-sdk-ui When:
- Building React chat interfaces
- Implementing AI completions in UI
- Streaming AI responses to frontend
- Building Next.js AI applications
- Handling chat message state
- Displaying tool calls in UI
- Managing file attachments with AI
- Migrating from v4 to v5 (UI hooks)
- Encountering useChat/useCompletion errors

### Don't Use When:
- Need backend AI functionality → Use **ai-sdk-core** instead
- Building non-React frontends (Svelte, Vue) → Check official docs
- Need Generative UI / RSC → See https://ai-sdk.dev/docs/ai-sdk-rsc
- Building native apps → Different SDK required

### Related Skills:
- **ai-sdk-core** - Backend text generation, structured output, tools, agents
- Compose both for full-stack AI applications

---

## Package Versions

**Stable (v6 - Recommended):**
```json
{
  "dependencies": {
    "ai": "^6.0.8",
    "@ai-sdk/react": "^3.0.6",
    "@ai-sdk/openai": "^3.0.2",
    "react": "^18.3.0",
    "zod": "^3.24.2"
  }
}
```

**Legacy (v5):**
```json
{
  "dependencies": {
    "ai": "^5.0.99",
    "@ai-sdk/react": "^1.0.0",
    "@ai-sdk/openai": "^2.0.68"
  }
}
```

**Version Notes:**
- AI SDK v6.0.6 (stable, Jan 2026) - recommended for new projects
- AI SDK v5.x (legacy) - still supported but not receiving new features
- React 18.3+ / React 19 supported
- Next.js 14+/15+ recommended
- Zod 3.24.2+ for schema validation

---

## Links to Official Documentation

**Core UI Hooks:**
- AI SDK UI Overview: https://ai-sdk.dev/docs/ai-sdk-ui/overview
- useChat: https://ai-sdk.dev/docs/ai-sdk-ui/chatbot
- useCompletion: https://ai-sdk.dev/docs/ai-sdk-ui/completion
- useObject: https://ai-sdk.dev/docs/ai-sdk-ui/object-generation

**Advanced Topics (Link Only):**
- Generative UI (RSC): https://ai-sdk.dev/docs/ai-sdk-rsc/overview
- Stream Protocols: https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocols
- Message Metadata: https://ai-sdk.dev/docs/ai-sdk-ui/message-metadata

**Next.js Integration:**
- Next.js App Router: https://ai-sdk.dev/docs/getting-started/nextjs-app-router
- Next.js Pages Router: https://ai-sdk.dev/docs/getting-started/nextjs-pages-router

**Migration & Troubleshooting:**
- v4→v5 Migration: https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0
- Troubleshooting: https://ai-sdk.dev/docs/troubleshooting
- Common Issues: https://ai-sdk.dev/docs/troubleshooting/common-issues

**Vercel Deployment:**
- Vercel Functions: https://vercel.com/docs/functions
- Streaming on Vercel: https://vercel.com/docs/functions/streaming

---

## Templates

This skill includes the following templates in `templates/`:

1. **use-chat-basic.tsx** - Basic chat with manual input (v5 pattern)
2. **use-chat-tools.tsx** - Chat with tool calling UI rendering
3. **use-chat-attachments.tsx** - File attachments support
4. **use-completion-basic.tsx** - Basic text completion
5. **use-object-streaming.tsx** - Streaming structured data
6. **nextjs-chat-app-router.tsx** - Next.js App Router complete example
7. **nextjs-chat-pages-router.tsx** - Next.js Pages Router complete example
8. **nextjs-api-route.ts** - API route for both App and Pages Router
9. **message-persistence.tsx** - Save/load chat history
10. **custom-message-renderer.tsx** - Custom message components with markdown
11. **package.json** - Dependencies template

## Reference Documents

See `references/` for:

- **use-chat-migration.md** - Complete v4→v5 migration guide
- **streaming-patterns.md** - UI streaming best practices
- **top-ui-errors.md** - 18 common UI errors with solutions
- **nextjs-integration.md** - Next.js setup patterns
- **links-to-official-docs.md** - Organized links to official docs

---

**Production Tested**: WordPress Auditor (https://wordpress-auditor.webfonts.workers.dev)
**Last verified**: 2026-01-20 | **Skill version**: 3.1.0 | **Changes**: Updated to AI SDK v6.0.42 (+19 patches). Added React Strict Mode section. Expanded Issue #7 (stale body) with 3 workarounds. Added 6 new issues: TypeError with resume+onFinish (#13), concurrent sendMessage state corruption (#14), tool approval callback edge case (#15), ZodError on early stop (#16), convertToModelMessages tool approval bug (#17), undefined id infinite loop (#18). Error count: 12→18.
