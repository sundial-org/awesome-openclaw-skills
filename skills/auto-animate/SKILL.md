---
name: auto-animate
description: |
  Zero-config animations for React, Vue, Solid, Svelte, Preact with @formkit/auto-animate (3.28kb). Prevents 15 documented errors including React 19 StrictMode bugs, SSR imports, conditional parents, viewport issues, drag & drop conflicts, and CSS transform bugs.

  Use when: animating lists/accordions/toasts, troubleshooting SSR animation errors, React 19 StrictMode issues, or need accessible drop-in transitions with auto prefers-reduced-motion.
user-invocable: true
---

# AutoAnimate - Error Prevention Guide

**Package**: @formkit/auto-animate@0.9.0 (current)
**Frameworks**: React, Vue, Solid, Svelte, Preact
**Last Updated**: 2026-01-21

---

## SSR-Safe Pattern (Critical for Cloudflare Workers/Next.js)

```tsx
// Use client-only import to prevent SSR errors
import { useState, useEffect } from "react";

export function useAutoAnimateSafe<T extends HTMLElement>() {
  const [parent, setParent] = useState<T | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && parent) {
      import("@formkit/auto-animate").then(({ default: autoAnimate }) => {
        autoAnimate(parent);
      });
    }
  }, [parent]);

  return [parent, setParent] as const;
}
```

**Why this matters**: Prevents Issue #1 (SSR/Next.js import errors). AutoAnimate uses DOM APIs not available on server.

---

## Known Issues Prevention (15 Documented Errors)

This skill prevents **15** documented issues:

### Issue #1: SSR/Next.js Import Errors
**Error**: "Can't import the named export 'useEffect' from non EcmaScript module"
**Source**: https://github.com/formkit/auto-animate/issues/55
**Why It Happens**: AutoAnimate uses DOM APIs not available on server
**Prevention**: Use dynamic imports (see `templates/vite-ssr-safe.tsx`)

### Issue #2: Conditional Parent Rendering
**Error**: Animations don't work when parent is conditional
**Source**: https://github.com/formkit/auto-animate/issues/8
**Why It Happens**: Ref can't attach to non-existent element
**Prevention**:

**React Pattern**:
```tsx
// ❌ Wrong
{showList && <ul ref={parent}>...</ul>}

// ✅ Correct
<ul ref={parent}>{showList && items.map(...)}</ul>
```

**Vue.js Pattern**:
```vue
<!-- ❌ Wrong - parent conditional -->
<ul v-if="showList" ref="parent">
  <li v-for="item in items" :key="item.id">{{ item.text }}</li>
</ul>

<!-- ✅ Correct - children conditional -->
<ul ref="parent">
  <li v-if="showList" v-for="item in items" :key="item.id">
    {{ item.text }}
  </li>
</ul>
```

**Source**: React [Issue #8](https://github.com/formkit/auto-animate/issues/8), Vue [Issue #193](https://github.com/formkit/auto-animate/issues/193)

### Issue #3: Missing Unique Keys
**Error**: Items don't animate correctly or flash
**Source**: Official docs
**Why It Happens**: React can't track which items changed
**Prevention**: Always use unique, stable keys (`key={item.id}`)

### Issue #4: Flexbox Width and Shaking Issues
**Error**: Elements snap to width instead of animating smoothly, or container shakes on remove
**Source**: Official docs, [Issue #212](https://github.com/formkit/auto-animate/issues/212)
**Why It Happens**: `flex-grow: 1` waits for surrounding content, causing timing issues
**Prevention**: Use explicit width instead of flex-grow for animated elements

```tsx
// ❌ Wrong - causes shaking
<ul ref={parent} style={{ display: 'flex' }}>
  {items.map(item => (
    <li key={item.id} style={{ flex: '1 1 auto' }}>{item.text}</li>
  ))}
</ul>

// ✅ Correct - fixed sizes
<ul ref={parent} style={{ display: 'flex', gap: '1rem' }}>
  {items.map(item => (
    <li
      key={item.id}
      style={{ minWidth: '200px', maxWidth: '200px' }}
    >
      {item.text}
    </li>
  ))}
</ul>
```

**Maintainer Note**: justin-schroeder confirmed fixed sizes are required for flex containers

### Issue #5: Table Row Display Issues
**Error**: Table structure breaks when removing rows
**Source**: https://github.com/formkit/auto-animate/issues/7
**Why It Happens**: Display: table-row conflicts with animations
**Prevention**: Apply to `<tbody>` instead of individual rows, or use div-based layouts

### Issue #6: Jest Testing Errors
**Error**: "Cannot find module '@formkit/auto-animate/react'"
**Source**: https://github.com/formkit/auto-animate/issues/29
**Why It Happens**: Jest doesn't resolve ESM exports correctly
**Prevention**: Configure `moduleNameMapper` in jest.config.js

### Issue #7: esbuild Compatibility
**Error**: "Path '.' not exported by package"
**Source**: https://github.com/formkit/auto-animate/issues/36
**Why It Happens**: ESM/CommonJS condition mismatch
**Prevention**: Configure esbuild to handle ESM modules properly

### Issue #8: CSS Position Side Effects
**Error**: Layout breaks after adding AutoAnimate
**Source**: Official docs
**Why It Happens**: Parent automatically gets `position: relative`
**Prevention**: Account for position change in CSS or set explicitly

### Issue #9: Vue/Nuxt Registration Errors
**Error**: "Failed to resolve directive: auto-animate"
**Source**: https://github.com/formkit/auto-animate/issues/43
**Why It Happens**: Plugin not registered correctly
**Prevention**: Proper plugin setup in Vue/Nuxt config (see references/)

**Nuxt 3 Note**: Requires v0.8.2+ (April 2024). Earlier versions have ESM import issues fixed by Daniel Roe. See [Issue #199](https://github.com/formkit/auto-animate/issues/199)

### Issue #10: Angular ESM Issues
**Error**: Build fails with "ESM-only package"
**Source**: https://github.com/formkit/auto-animate/issues/72
**Why It Happens**: CommonJS build environment
**Prevention**: Configure ng-packagr for Angular Package Format

### Issue #11: React 19 StrictMode Double-Call Bug
**Error**: Child animations don't work in React 19 StrictMode
**Source**: https://github.com/formkit/auto-animate/issues/232
**Why It Happens**: StrictMode calls useEffect twice, triggering autoAnimate initialization twice
**Prevention**: Use ref to track initialization

```tsx
// ❌ Wrong - breaks in StrictMode
const [parent] = useAutoAnimate();

// ✅ Correct - prevents double initialization
const [parent] = useAutoAnimate();
const initialized = useRef(false);

useEffect(() => {
  if (initialized.current) return;
  initialized.current = true;
}, []);
```

**Note**: React 19 enables StrictMode by default in development. This affects all React 19+ projects.

### Issue #12: Broken Animation Outside Viewport
**Error**: Animations broken when list is outside viewport
**Source**: https://github.com/formkit/auto-animate/issues/222
**Why It Happens**: Chrome may not run Animation API for off-screen elements
**Prevention**: Ensure parent is visible before applying autoAnimate

```tsx
const isInViewport = (element) => {
  const rect = element.getBoundingClientRect();
  return rect.top >= 0 && rect.bottom <= window.innerHeight;
};

useEffect(() => {
  if (parent.current && isInViewport(parent.current)) {
    autoAnimate(parent.current);
  }
}, [parent]);
```

### Issue #13: Deleted Elements Overlay Existing Content
**Error**: Removed items overlay other items during fade out
**Source**: https://github.com/formkit/auto-animate/issues/231
**Why It Happens**: Exit animation maintains z-index, covering active content
**Prevention**: Add explicit z-index handling

```tsx
// CSS workaround
<style>{`
  [data-auto-animate-target] {
    z-index: -1 !important;
  }
`}</style>
```

### Issue #14: Cannot Disable During Drag & Drop
**Error**: Calling enable(false) doesn't prevent animations during drag
**Source**: https://github.com/formkit/auto-animate/issues/215
**Why It Happens**: Disable doesn't work reliably mid-drag
**Prevention**: Conditionally remove ref during drag

```tsx
const [isDragging, setIsDragging] = useState(false);
const [parent] = useAutoAnimate();

return (
  <ul ref={isDragging ? null : parent}>
    {/* items */}
  </ul>
);
```

### Issue #15: CSS Transform Parent Position Bug
**Error**: Items animate from wrong position after parent transform
**Source**: https://github.com/formkit/auto-animate/issues/227
**Why It Happens**: Items remember original position before transform
**Prevention**: Delay autoAnimate until transform completes

```tsx
useEffect(() => {
  if (showList && parent.current) {
    setTimeout(() => {
      autoAnimate(parent.current);
    }, 300); // Match CSS transition duration
  }
}, [showList]);
```

---

## Critical Rules (Error Prevention)

### Always Do

✅ **Use unique, stable keys** - `key={item.id}` not `key={index}`
✅ **Keep parent in DOM** - Parent ref element always rendered
✅ **Client-only for SSR** - Dynamic import for server environments
✅ **Respect accessibility** - Keep `disrespectUserMotionPreference: false`
✅ **Test with motion disabled** - Verify UI works without animations
✅ **Use explicit width** - Avoid flex-grow on animated elements
✅ **Apply to tbody for tables** - Not individual rows

### Never Do

❌ **Conditional parent** - `{show && <ul ref={parent}>}`
❌ **Index as key** - `key={index}` breaks animations
❌ **Ignore SSR** - Will break in Cloudflare Workers/Next.js
❌ **Force animations** - `disrespectUserMotionPreference: true` breaks accessibility
❌ **Animate tables directly** - Use tbody or div-based layout
❌ **Skip unique keys** - Required for proper animation
❌ **Complex animations** - Use Motion instead

**Note**: AutoAnimate respects `prefers-reduced-motion` automatically (never disable this).

---

## Community Tips (Community-Sourced)

> **Note**: These tips come from community discussions. Verify against your version.

### Tip: Prevent Test Freezing with Mocked Package

**Source**: [Issue #230](https://github.com/formkit/auto-animate/issues/230) | **Confidence**: MEDIUM
**Applies to**: v0.8.2+

Tests may freeze for ~10 seconds when package is mocked. Add ResizeObserver mock:

```typescript
// jest.setup.js
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// __mocks__/@formkit/auto-animate.js
const autoAnimate = jest.fn(() => () => {});
const useAutoAnimate = jest.fn(() => [null, jest.fn(), jest.fn()]);
module.exports = { default: autoAnimate, useAutoAnimate };
```

### Tip: Memory Leak Prevention

**Source**: [Issue #180](https://github.com/formkit/auto-animate/issues/180) | **Confidence**: LOW
**Applies to**: All versions

For long-lived SPAs, ensure proper cleanup:

```tsx
useEffect(() => {
  const cleanup = autoAnimate(parent.current);
  return () => cleanup && cleanup();
}, []);

// useAutoAnimate hook handles cleanup automatically
const [parent] = useAutoAnimate(); // Preferred
```

---

## Package Versions

**Latest**: @formkit/auto-animate@0.9.0 (Sept 5, 2025)

**Recent Releases**:
- v0.9.0 (Sept 5, 2025) - Current stable
- v0.8.2 (April 10, 2024) - Fixed Nuxt 3 ESM imports, ResizeObserver guard

```json
{
  "dependencies": {
    "@formkit/auto-animate": "^0.9.0"
  }
}
```

**Framework Compatibility**: React 18+, Vue 3+, Solid, Svelte, Preact

**Important**: For Nuxt 3 users, v0.8.2+ is required. Earlier versions have ESM import issues

---

## Official Documentation

- **Official Site**: https://auto-animate.formkit.com
- **GitHub**: https://github.com/formkit/auto-animate
- **npm**: https://www.npmjs.com/package/@formkit/auto-animate
- **React Docs**: https://auto-animate.formkit.com/react

---

## Templates & References

See bundled resources:
- `templates/` - Copy-paste examples (SSR-safe, accordion, toast, forms)
- `references/` - CSS conflicts, SSR patterns, library comparisons
