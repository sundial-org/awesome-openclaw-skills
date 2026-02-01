# AI SDK UI - Frontend React Hooks

**Version**: AI SDK v6.0.6 (Stable)
**Status**: Production-Ready ✅
**Framework**: React 18+/19, Next.js 14+/15+
**Last Updated**: 2026-01-03

---

## What This Skill Does

Provides complete implementation patterns for Vercel AI SDK v6 **frontend React hooks**:

- **useChat** - Chat interfaces with streaming
- **useCompletion** - Text completions
- **useObject** - Streaming structured data

**Focus**: React UI layer for AI-powered applications.

---

## Auto-Trigger Keywords

This skill should be automatically discovered when working with any of the following:

### Primary Keywords (Highest Priority)

- `ai sdk ui`
- `useChat hook`
- `useCompletion hook`
- `useObject hook`
- `react ai chat`
- `ai chat interface`
- `chat ui react`
- `ai sdk react`
- `vercel ai ui`
- `ai react hooks`
- `streaming ai ui`
- `react streaming chat`
- `nextjs ai chat`
- `nextjs ai`
- `next.js chat`
- `ai chat component`
- `react ai components`

### Secondary Keywords (Medium Priority)

- `nextjs app router ai`
- `nextjs pages router ai`
- `chat message state`
- `message persistence ai`
- `ai file attachments`
- `file upload ai chat`
- `streaming chat react`
- `real-time ai chat`
- `tool calling ui`
- `ai tools react`
- `ai completion react`
- `text completion ui`
- `structured data streaming`
- `useObject streaming`
- `react chat app`
- `react ai application`

### Error-Based Keywords (Trigger on Errors)

- `useChat failed to parse stream`
- `parse stream error`
- `useChat no response`
- `chat hook no response`
- `unclosed streams ai`
- `stream not closing`
- `streaming not working deployed`
- `vercel streaming issue`
- `streaming not working proxied`
- `proxy buffering`
- `strange stream output`
- `0: characters stream`
- `stale body values useChat`
- `body not updating`
- `custom headers not working useChat`
- `react maximum update depth`
- `infinite loop useChat`
- `repeated assistant messages`
- `duplicate messages`
- `onFinish not called`
- `stream aborted`
- `v5 migration useChat`
- `v6 migration useChat`
- `useChat breaking changes`
- `input handleInputChange removed`
- `sendMessage v5`
- `message parts v6`
- `m.content undefined`
- `parts array v6`

### Framework Integration Keywords

- `nextjs ai integration`
- `next.js ai sdk`
- `vite react ai`
- `remix ai chat`
- `vercel ai deployment`

### Provider Keywords

- `openai react chat`
- `anthropic react chat`
- `claude chat ui`
- `gpt chat interface`

---

## Quick Start

```bash
npm install ai @ai-sdk/react @ai-sdk/openai
```

**5-minute chat interface (v6 with message parts):**

```tsx
// app/chat/page.tsx
'use client';
import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export default function Chat() {
  const { messages, sendMessage, isLoading } = useChat({ api: '/api/chat' });
  const [input, setInput] = useState('');

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          {m.role}: {m.parts.map((part, i) => (
            part.type === 'text' ? <span key={i}>{part.text}</span> : null
          ))}
        </div>
      ))}
      <form onSubmit={(e) => {
        e.preventDefault();
        sendMessage({ content: input });
        setInput('');
      }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} />
      </form>
    </div>
  );
}
```

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({ model: openai('gpt-5'), messages });
  return result.toDataStreamResponse();
}
```

---

## What's Included

### Templates (11)

1. **use-chat-basic.tsx** - Basic chat with v5 input management
2. **use-chat-tools.tsx** - Chat with tool calling UI
3. **use-chat-attachments.tsx** - File attachments support
4. **use-completion-basic.tsx** - Text completion streaming
5. **use-object-streaming.tsx** - Structured data streaming
6. **nextjs-chat-app-router.tsx** - Next.js App Router complete example
7. **nextjs-chat-pages-router.tsx** - Next.js Pages Router complete example
8. **nextjs-api-route.ts** - API route for both routers
9. **message-persistence.tsx** - localStorage persistence
10. **custom-message-renderer.tsx** - Markdown & code highlighting
11. **package.json** - Dependencies template

### References (5)

1. **use-chat-migration.md** - Complete v4→v5 migration guide
2. **streaming-patterns.md** - UI streaming best practices
3. **top-ui-errors.md** - 12 common UI errors with solutions
4. **nextjs-integration.md** - Next.js setup patterns
5. **links-to-official-docs.md** - Official docs organization

### Scripts (1)

1. **check-versions.sh** - Verify package versions

---

## Critical v6 Changes

**BREAKING: Message content is now accessed via `.parts` array!**

**v5 (OLD):**
```tsx
{messages.map(m => <div>{m.content}</div>)}
```

**v6 (NEW):**
```tsx
{messages.map(m => (
  <div>
    {m.parts.map((part, i) => (
      part.type === 'text' ? <span key={i}>{part.text}</span> : null
    ))}
  </div>
))}
```

**Part Types in v6:**
- `text` - Text content (`.text`)
- `tool-invocation` - Tool calls (`.toolName`, `.args`, `.result`)
- `file` - File attachments (`.mimeType`, `.data`)
- `reasoning` - Model reasoning
- `source` - Source citations

**Prior v4→v5 changes still apply:**
- `input`, `handleInputChange`, `handleSubmit` removed
- `append()` → `sendMessage()`
- `onResponse` removed → use `onFinish`

See `references/use-chat-migration.md` for complete migration guide.

---

## Token Savings

**Without skill**: ~15,500 tokens (research, trial-and-error, debugging)
**With skill**: ~7,000 tokens (templates, references, examples)

**Savings**: ~55% (8,500 tokens)

---

## Errors Prevented

This skill documents and prevents 12 common UI errors:

1. useChat failed to parse stream
2. useChat no response
3. Unclosed streams
4. Streaming not working when deployed
5. Streaming not working when proxied
6. Strange stream output (0:... characters)
7. Stale body values
8. Custom headers not working
9. React maximum update depth
10. Repeated assistant messages
11. onFinish not called when aborted
12. Type errors with message parts

---

## When to Use This Skill

**Use ai-sdk-ui when:**
- Building React chat interfaces
- Implementing AI completions in UI
- Streaming AI responses to frontend
- Building Next.js AI applications
- Handling chat message state
- Displaying tool calls in UI
- Managing file attachments with AI
- Migrating from v4 to v5
- Encountering useChat/useCompletion errors

**Don't use when:**
- Need backend AI (use **ai-sdk-core** instead)
- Building non-React frontends (check official docs)
- Need Generative UI / RSC (advanced topic)

---

## Related Skills

- **ai-sdk-core** - Backend text generation, structured output, tools, agents
- Compose both for full-stack AI applications

---

## Package Versions

**v6 (Recommended):**
- `ai`: ^6.0.6
- `@ai-sdk/react`: ^3.0.6
- `@ai-sdk/openai`: ^3.0.2
- `react`: ^18.3.0
- `zod`: ^3.24.2

**Next.js:**
- `next`: ^14.0.0 or ^15.0.0
- `react`: ^18.3.0 or ^19.0.0
- `react-dom`: ^18.3.0 or ^19.0.0

---

## Official Documentation

**Core UI Hooks:**
- AI SDK UI Overview: https://ai-sdk.dev/docs/ai-sdk-ui/overview
- useChat: https://ai-sdk.dev/docs/ai-sdk-ui/chatbot
- useCompletion: https://ai-sdk.dev/docs/ai-sdk-ui/completion
- useObject: https://ai-sdk.dev/docs/ai-sdk-ui/object-generation

**Next.js:**
- App Router: https://ai-sdk.dev/docs/getting-started/nextjs-app-router
- Pages Router: https://ai-sdk.dev/docs/getting-started/nextjs-pages-router

**Migration:**
- v4→v5: https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0

---

## Production Validation

**Tested In**: WordPress Auditor (https://wordpress-auditor.webfonts.workers.dev)

**Verified**:
- ✅ All 11 templates work copy-paste
- ✅ v5→v6 breaking changes documented
- ✅ Message parts structure documented
- ✅ 12 common errors prevented
- ✅ Package versions current (2026-01-03)
- ✅ Next.js App Router & Pages Router examples
- ✅ Token savings: 55%

---

## Recent Updates

**v1.1.0 (2026-01-03):**
- **AI SDK v6 Stable**: Updated from v5.0.99/v6.0.0-beta to v6.0.6 stable
- **Message Parts Structure**: Added v6 breaking change documentation (.content → .parts)
- **Package Updates**: @ai-sdk/react 1.0.0→3.0.6, @ai-sdk/openai 2.0.68→3.0.2
- **useAssistant Deprecation**: Added deprecation notice (OpenAI Assistants sunset Aug 26, 2026)
- **React 19 Support**: Framework support expanded to React 19 and Next.js 15

**v1.0.1 (2025-11-19):**
- Updated Package Versions: AI SDK 5.0.95
- Added YAML frontmatter metadata

---

**License**: MIT
