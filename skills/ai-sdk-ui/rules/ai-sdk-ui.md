---
paths: "**/*.ts", "**/*.tsx", "**/chat*.ts", "**/ai*.ts"
---

# AI SDK UI v5 Corrections

Claude's training may reference AI SDK v4 UI patterns. This project uses **AI SDK v5+**.

## Hook Import Changes

```typescript
/* ❌ v4 imports */
import { useChat, useCompletion } from 'ai/react'
import { useActions, useUIState } from 'ai/rsc'

/* ✅ v5 imports */
import { useChat, useCompletion } from '@ai-sdk/react'
import { useActions, useUIState } from '@ai-sdk/rsc'
```

## useChat Options

```typescript
/* ❌ v4 options */
const { messages, input, handleSubmit } = useChat({
  api: '/api/chat',
  initialMessages: [],
  body: { model: 'gpt-4' },
})

/* ✅ v5 options */
const { messages, input, handleSubmit } = useChat({
  api: '/api/chat',
  initialMessages: [],
  body: { model: 'gpt-5' },
  maxSteps: 5, // v5: multi-step by default
})
```

## Message Types

```typescript
/* ❌ v4 message type */
import type { Message } from 'ai'
const msgs: Message[] = []

/* ✅ v5 message type */
import type { UIMessage } from '@ai-sdk/react'
const msgs: UIMessage[] = []
```

## Streaming Text

```typescript
/* ❌ v4 streaming */
import { StreamingTextResponse } from 'ai'
return new StreamingTextResponse(stream)

/* ✅ v5 streaming */
import { pipeTextStreamToResponse } from 'ai'
return pipeTextStreamToResponse(result.toTextStream(), response)

// Or use result.toDataStreamResponse() for Next.js
return result.toDataStreamResponse()
```

## Tool Results in UI

```typescript
/* ❌ v4 tool results */
{messages.map((m) => (
  m.toolInvocations?.map((t) => (
    <ToolResult key={t.toolCallId} result={t.result} />
  ))
))}

/* ✅ v5 tool results (check state) */
{messages.map((m) => (
  m.toolInvocations?.map((t) => (
    t.state === 'result' && (
      <ToolResult key={t.toolCallId} result={t.result} />
    )
  ))
))}
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `from 'ai/react'` | `from '@ai-sdk/react'` |
| `from 'ai/rsc'` | `from '@ai-sdk/rsc'` |
| `Message` type | `UIMessage` type |
| `StreamingTextResponse` | `toDataStreamResponse()` or `pipeTextStreamToResponse()` |
| `useChat` without maxSteps | Add `maxSteps` for multi-step |
| Direct tool result access | Check `t.state === 'result'` first |
