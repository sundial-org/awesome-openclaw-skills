# AutoAnimate SSR Patterns

This document covers how to use AutoAnimate in server-side rendering (SSR) environments without errors.

---

## Why SSR is a Problem

AutoAnimate uses DOM APIs (`window`, `document`, `MutationObserver`) that **don't exist on the server**:

```javascript
// Inside @formkit/auto-animate
if (typeof window !== "undefined") {
  // Uses window, document, etc.
}
```

**Common SSR errors:**

```
❌ ReferenceError: window is not defined
❌ ReferenceError: document is not defined
❌ Can't import the named export 'useEffect' from non EcmaScript module
❌ Cannot find module '@formkit/auto-animate/react'
```

**Solution**: Only import and run AutoAnimate on the **client side**.

---

## Pattern #1: Dynamic Import (Recommended)

### Cloudflare Workers + Static Assets

**Best for**: Cloudflare Workers with Vite

```tsx
// src/components/TodoList.tsx
import { useState, useEffect } from "react";
import type { AutoAnimateOptions } from "@formkit/auto-animate";

export function useAutoAnimateSafe<T extends HTMLElement>(
  options?: Partial<AutoAnimateOptions>
) {
  const [parent, setParent] = useState<T | null>(null);

  useEffect(() => {
    // Only import on client side
    if (typeof window !== "undefined" && parent) {
      import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
        autoAnimate(parent, options);
      });
    }
  }, [parent, options]);

  return [parent, setParent] as const;
}

// Use it:
export function TodoList() {
  const [parent, setParent] = useAutoAnimateSafe<HTMLUListElement>();

  return (
    <ul ref={setParent}> {/* Callback ref pattern */}
      {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
    </ul>
  );
}
```

**Vite Config** (required):

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import cloudflare from "@cloudflare/vite-plugin";

export default defineConfig({
  plugins: [react(), cloudflare()],
  ssr: {
    external: ["@formkit/auto-animate"], // ← Exclude from SSR bundle
  },
});
```

**Why this works:**
- Hook runs only after hydration (client-side)
- Dynamic import prevents server-side execution
- Callback ref ensures parent exists before animation setup

---

## Pattern #2: Client-Only Component Wrapper

### Next.js App Router

**Best for**: Next.js 13+ (App Router)

```tsx
// src/components/AnimatedList.client.tsx
"use client"; // ← Mark as client component

import { useAutoAnimate } from "@formkit/auto-animate/react";

export function AnimatedList({ children }: { children: React.ReactNode }) {
  const [parent] = useAutoAnimate();

  return <div ref={parent}>{children}</div>;
}
```

```tsx
// src/app/page.tsx (Server Component)
import { AnimatedList } from "@/components/AnimatedList.client";

export default function Page() {
  return (
    <AnimatedList>
      {todos.map(todo => (
        <div key={todo.id}>{todo.text}</div>
      ))}
    </AnimatedList>
  );
}
```

**Why this works:**
- `"use client"` directive tells Next.js to bundle for client only
- Server component passes data, client component handles animation
- No SSR errors because AutoAnimate never runs on server

---

## Pattern #3: Conditional Rendering

### Next.js Pages Router

**Best for**: Next.js 12 (Pages Router)

```tsx
// src/components/TodoList.tsx
import { useState, useEffect } from "react";

export function TodoList({ todos }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    // Server render: No animation
    return (
      <ul>
        {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
      </ul>
    );
  }

  // Client render: With animation
  return <AnimatedTodoList todos={todos} />;
}

function AnimatedTodoList({ todos }) {
  const { useAutoAnimate } = require("@formkit/auto-animate/react");
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
    </ul>
  );
}
```

**Why this works:**
- Server renders basic HTML (no animation)
- Client hydrates, detects `isClient`, re-renders with animation
- `require()` only runs on client (inside `if (isClient)`)

**Drawback**: Slight flash as component re-renders on hydration.

---

## Pattern #4: Next.js Dynamic Import

### Next.js (Any Router)

**Best for**: Lazy-loading animated components

```tsx
// src/components/AnimatedList.tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function AnimatedList({ children }) {
  const [parent] = useAutoAnimate();
  return <div ref={parent}>{children}</div>;
}
```

```tsx
// src/app/page.tsx
import dynamic from "next/dynamic";

const AnimatedList = dynamic(
  () => import("@/components/AnimatedList").then(mod => ({ default: mod.AnimatedList })),
  { ssr: false } // ← Disable SSR for this component
);

export default function Page() {
  return (
    <AnimatedList>
      {todos.map(todo => <div key={todo.id}>{todo.text}</div>)}
    </AnimatedList>
  );
}
```

**Why this works:**
- `{ ssr: false }` tells Next.js to skip SSR for this component
- Component only loads on client
- Clean, declarative API

---

## Pattern #5: Remix

### Remix

**Best for**: Remix SSR

```tsx
// app/components/AnimatedList.tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useEffect, useState } from "react";

export function AnimatedList({ children }: { children: React.ReactNode }) {
  const [parent, setParent] = useState<HTMLDivElement | null>(null);

  useEffect(() => {
    if (parent && typeof window !== "undefined") {
      import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
        autoAnimate(parent);
      });
    }
  }, [parent]);

  return <div ref={setParent}>{children}</div>;
}
```

```tsx
// app/routes/todos.tsx
import { AnimatedList } from "~/components/AnimatedList";

export default function TodosRoute() {
  return (
    <AnimatedList>
      {todos.map(todo => <div key={todo.id}>{todo.text}</div>)}
    </AnimatedList>
  );
}
```

**Why this works:**
- Dynamic import in `useEffect` (client-only)
- Callback ref pattern ensures parent exists
- No special Remix config needed

---

## Pattern #6: Astro

### Astro

**Best for**: Astro SSG/SSR

```astro
---
// src/components/TodoList.astro
const { todos } = Astro.props;
---

<ul id="todo-list">
  {todos.map(todo => (
    <li key={todo.id}>{todo.text}</li>
  ))}
</ul>

<script>
  // Client-side script (runs in browser)
  import { autoAnimate } from "@formkit/auto-animate";

  const list = document.getElementById("todo-list");
  if (list) {
    autoAnimate(list);
  }
</script>
```

**Why this works:**
- `<script>` tag runs only on client (Astro feature)
- Vanilla AutoAnimate (no React hook)
- No SSR config needed

---

## Pattern #7: SvelteKit

### SvelteKit

**Best for**: SvelteKit SSR

```svelte
<!-- src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { autoAnimate } from '@formkit/auto-animate';

  export let todos;
  let listElement;

  onMount(() => {
    if (listElement) {
      autoAnimate(listElement);
    }
  });
</script>

<ul bind:this={listElement}>
  {#each todos as todo (todo.id)}
    <li>{todo.text}</li>
  {/each}
</ul>
```

**Why this works:**
- `onMount` only runs on client (Svelte lifecycle)
- `bind:this` attaches ref to element
- No special SvelteKit config needed

---

## Pattern #8: Nuxt 3

### Nuxt 3

**Best for**: Nuxt 3 SSR

```vue
<!-- components/AnimatedList.vue -->
<template>
  <ul ref="listRef">
    <li v-for="todo in todos" :key="todo.id">
      {{ todo.text }}
    </li>
  </ul>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps(['todos']);
const listRef = ref(null);

onMounted(async () => {
  if (process.client && listRef.value) {
    const { default: autoAnimate } = await import('@formkit/auto-animate');
    autoAnimate(listRef.value);
  }
});
</script>
```

**Why this works:**
- `onMounted` only runs on client (Vue lifecycle)
- `process.client` check ensures client-side execution
- Dynamic import prevents server bundling

**Nuxt Config** (optional):

```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  build: {
    transpile: ['@formkit/auto-animate'], // ← May be needed
  },
});
```

---

## Pattern #9: Gatsby

### Gatsby

**Best for**: Gatsby SSG

```tsx
// src/components/TodoList.tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useEffect, useState } from "react";

export function TodoList({ todos }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Skip during SSR
  if (!mounted) {
    return (
      <ul>
        {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
      </ul>
    );
  }

  return <AnimatedList todos={todos} />;
}

function AnimatedList({ todos }) {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
    </ul>
  );
}
```

**Why this works:**
- Conditional rendering based on `mounted` state
- Server renders basic HTML
- Client re-renders with animation after hydration

---

## Common SSR Errors & Fixes

### Error: "window is not defined"

**Fix**: Use dynamic import or conditional rendering

```tsx
// ❌ Wrong (runs on server)
import { useAutoAnimate } from "@formkit/auto-animate/react";

// ✅ Correct (client-only)
useEffect(() => {
  import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
    autoAnimate(parent);
  });
}, [parent]);
```

### Error: "Cannot find module '@formkit/auto-animate/react'"

**Fix**: Add to `external` in Vite/Webpack config

```typescript
// vite.config.ts
export default defineConfig({
  ssr: {
    external: ["@formkit/auto-animate"],
  },
});
```

### Error: "useEffect is not defined"

**Fix**: Use dynamic import inside `useEffect`

```tsx
// ❌ Wrong
const { useAutoAnimate } = require("@formkit/auto-animate/react");

// ✅ Correct
useEffect(() => {
  import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
    autoAnimate(parent);
  });
}, [parent]);
```

### Error: "document is not defined"

**Fix**: Check for `window` before importing

```tsx
useEffect(() => {
  if (typeof window !== "undefined" && parent) {
    import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
      autoAnimate(parent);
    });
  }
}, [parent]);
```

---

## Testing SSR Safety

### Manual Test

1. Disable JavaScript in browser (Chrome DevTools → Settings → Debugger → Disable JavaScript)
2. Reload page
3. Check if content renders (without animations)
4. Re-enable JavaScript
5. Check if animations work

**Expected behavior:**
- Content visible without JavaScript (SSR worked)
- Animations work with JavaScript (hydration worked)

### Automated Test (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test('SSR renders without JavaScript', async ({ page }) => {
  // Disable JavaScript
  await page.context().setJavaScriptEnabled(false);

  // Visit page
  await page.goto('/todos');

  // Check content is visible
  await expect(page.locator('ul li')).toHaveCount(3);
});

test('Animations work with JavaScript', async ({ page }) => {
  // JavaScript enabled (default)
  await page.goto('/todos');

  // Add new item
  await page.fill('input', 'New todo');
  await page.click('button[type="submit"]');

  // Check animation ran (item exists)
  await expect(page.locator('ul li')).toHaveCount(4);
});
```

---

## Summary: SSR Pattern Checklist

Choose the right pattern for your framework:

- **Cloudflare Workers** → Pattern #1 (Dynamic Import)
- **Next.js App Router** → Pattern #2 (Client Component)
- **Next.js Pages Router** → Pattern #3 (Conditional Rendering) or #4 (Dynamic Import)
- **Remix** → Pattern #5 (useEffect + Dynamic Import)
- **Astro** → Pattern #6 (Client Script)
- **SvelteKit** → Pattern #7 (onMount)
- **Nuxt 3** → Pattern #8 (onMounted + process.client)
- **Gatsby** → Pattern #9 (Conditional Rendering)

**Key principles:**
- ✅ Only import AutoAnimate on client side
- ✅ Use `useEffect`, `onMount`, or `<script>` tag for client-only code
- ✅ Check `typeof window !== "undefined"` before using DOM APIs
- ✅ Add to `external` in build config if needed
- ✅ Test with JavaScript disabled to verify SSR works

---

## Getting Help

If you encounter SSR errors not covered here:

1. Check the framework's SSR docs (Next.js, Remix, etc.)
2. Open issue at https://github.com/formkit/auto-animate/issues
3. Include:
   - Framework + version
   - Error message
   - Minimal reproduction

The AutoAnimate community is helpful and responsive!
