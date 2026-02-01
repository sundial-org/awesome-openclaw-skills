# AutoAnimate vs Motion: Decision Guide

## Quick Decision Matrix

| Need | AutoAnimate | Motion |
|------|-------------|--------|
| List add/remove/sort | ✅ Perfect | ⚠️ Overkill |
| Accordion expand/collapse | ✅ Perfect | ⚠️ Overkill |
| Toast notifications | ✅ Perfect | ⚠️ Overkill |
| Form validation errors | ✅ Perfect | ⚠️ Overkill |
| Hero animations | ❌ Too simple | ✅ Perfect |
| Drag and drop | ❌ Not supported | ✅ Perfect |
| Scroll animations | ❌ Not supported | ✅ Perfect |
| Gesture controls | ❌ Not supported | ✅ Perfect |
| Spring physics | ❌ Not supported | ✅ Perfect |
| SVG path morphing | ❌ Not supported | ✅ Perfect |

---

## Bundle Size Comparison

```
AutoAnimate: 3.28 KB gzipped
Motion:      22 KB gzipped (6.7x larger)
```

**Impact**: For a typical SPA, AutoAnimate saves ~19 KB (about 1 second of load time on 3G).

---

## API Complexity Comparison

### AutoAnimate: Zero Config

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function MyList() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  );
}
```

**Total lines**: 3 (import, hook, ref)

### Motion: Configuration Required

```tsx
import { motion, AnimatePresence } from "motion/react";

export function MyList() {
  return (
    <AnimatePresence>
      <motion.ul>
        {items.map(item => (
          <motion.li
            key={item.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2 }}
          >
            {item.text}
          </motion.li>
        ))}
      </motion.ul>
    </AnimatePresence>
  );
}
```

**Total lines**: 12 (import, wrapper, motion components, animation props)

**Maintenance**: Motion requires updating animation props if design changes. AutoAnimate "just works".

---

## Use Case Breakdown

### AutoAnimate Wins: 90% of UI Animations

**When to use:**
1. **Lists** - Todo lists, shopping carts, search results
2. **Accordions** - FAQ sections, collapsible panels
3. **Toasts** - Notifications, alerts, success messages
4. **Form validation** - Error messages appearing/disappearing
5. **Tabs** - Content switching with smooth transitions
6. **Modals** - Simple fade in/out
7. **Filters** - Results updating after filter changes
8. **Sort** - Reordering items visually
9. **Pagination** - Items entering/leaving

**Why AutoAnimate:**
- Zero configuration needed
- Works on ANY existing component (no refactor)
- Respects `prefers-reduced-motion` automatically
- 3.28 KB bundle size
- Framework-agnostic

**Example: E-commerce Cart**

```tsx
// AutoAnimate: Add animation to existing cart component
const [parent] = useAutoAnimate();

return (
  <ul ref={parent}> {/* Add one ref, done! */}
    {cartItems.map(item => (
      <CartItem key={item.id} item={item} />
    ))}
  </ul>
);
```

### Motion Wins: 10% of Hero/Marketing Animations

**When to use:**
1. **Landing pages** - Hero sections with parallax, reveals
2. **Onboarding flows** - Multi-step wizards with choreographed animations
3. **Product showcases** - SVG animations, path morphing
4. **Drag & drop** - Sortable lists, Kanban boards, file uploads
5. **Scroll animations** - Reveal on scroll, scroll-linked animations
6. **Gesture controls** - Swipe to delete, pinch to zoom
7. **Spring physics** - Natural, bouncy animations
8. **Complex orchestration** - Sequenced animations with delays
9. **Layout animations** - Shared element transitions

**Why Motion:**
- Full control over animation curves
- Gesture recognition built-in
- Spring physics for natural feel
- Scroll-linked animations
- Animation variants (hover, tap, focus states)
- Layout animations (FLIP technique)

**Example: Landing Page Hero**

```tsx
// Motion: Complex choreographed animation
<motion.section
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ staggerChildren: 0.2 }}
>
  <motion.h1
    initial={{ y: -50, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
  >
    Welcome
  </motion.h1>

  <motion.p
    initial={{ y: 50, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
  >
    Description
  </motion.p>

  <motion.button
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
  >
    Get Started
  </motion.button>
</motion.section>
```

---

## Can You Use Both?

**Yes!** They solve different problems:

```tsx
// AutoAnimate for list animations
import { useAutoAnimate } from "@formkit/auto-animate/react";

// Motion for hero section
import { motion } from "motion/react";

export function App() {
  const [listParent] = useAutoAnimate();

  return (
    <div>
      {/* Motion for hero */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <h1>Welcome</h1>
      </motion.section>

      {/* AutoAnimate for list */}
      <ul ref={listParent}>
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

**Bundle size**: 3.28 KB + 22 KB = 25.28 KB total

---

## Migration Scenarios

### AutoAnimate → Motion

**When to migrate:**
- Need gesture controls (drag, swipe)
- Need scroll-based animations
- Need spring physics
- Need complex choreography
- Need layout animations

**How to migrate:**
1. Replace `useAutoAnimate()` with `motion` components
2. Add animation props explicitly
3. Wrap with `<AnimatePresence>` for exit animations
4. Configure transition timings

**Cost**: ~2-3 hours for complex components

### Motion → AutoAnimate

**When to migrate:**
- Bundle size is critical
- Animations are simple (list transitions)
- Want zero-config solution
- Want better accessibility defaults

**How to migrate:**
1. Remove `motion.*` components → regular HTML elements
2. Remove animation props
3. Add `useAutoAnimate()` ref to parent
4. Done!

**Savings**: ~19 KB bundle size, ~50% less code

---

## Real-World Recommendations

### Startup MVP / Side Project
**Use AutoAnimate everywhere** → Add Motion only if needed for hero sections

**Why:**
- Faster development (zero config)
- Smaller bundle (better SEO, mobile performance)
- Good enough animations for most users

### E-commerce Site
**Use AutoAnimate for:**
- Product lists
- Shopping cart
- Filters/sort

**Use Motion for:**
- Product image galleries (if interactive)
- Landing page hero

### SaaS Dashboard
**Use AutoAnimate for:**
- Data tables
- Sidebar navigation
- Notifications
- Form validation

**Use Motion for:**
- Onboarding flow
- Empty states
- Marketing pages

### Content Site / Blog
**Use AutoAnimate for:**
- Article lists
- Comments
- Related posts

**Use Motion for:**
- Hero sections
- Image galleries (if interactive)

---

## Performance Comparison

### AutoAnimate

**Strengths:**
- ✅ 3.28 KB gzipped
- ✅ No runtime overhead (pure CSS transitions)
- ✅ Works with server-side rendering (with dynamic import)
- ✅ Zero JavaScript for animations (CSS-based)

**Limitations:**
- ❌ No control over easing curves (uses CSS defaults)
- ❌ No gesture support
- ❌ No spring physics

### Motion

**Strengths:**
- ✅ Full animation control
- ✅ Gesture recognition
- ✅ Spring physics
- ✅ Layout animations (FLIP)
- ✅ Scroll-linked animations

**Limitations:**
- ❌ 22 KB gzipped (6.7x larger)
- ❌ JavaScript-based animations (more overhead)
- ❌ More complex API (higher maintenance)

---

## Accessibility Comparison

### AutoAnimate

**Built-in:**
- ✅ Respects `prefers-reduced-motion` automatically (no config needed)
- ✅ Animations disabled if user has motion sensitivity

**Manual:**
- ❌ Can override with `disrespectUserMotionPreference: true` (don't do this!)

### Motion

**Built-in:**
- ✅ Respects `prefers-reduced-motion` via `useReducedMotion()` hook

**Manual:**
- ❌ Need to manually check and disable animations:
  ```tsx
  const shouldReduceMotion = useReducedMotion();
  const variants = shouldReduceMotion ? disabledVariants : enabledVariants;
  ```

**Winner**: AutoAnimate (zero-config accessibility)

---

## Decision Flowchart

```
Start: Need animation?
  ↓
  Is it a simple list/accordion/toast/form?
    ↓ YES → AutoAnimate
    ↓ NO
  ↓
  Do you need gestures (drag/swipe)?
    ↓ YES → Motion
    ↓ NO
  ↓
  Do you need scroll animations?
    ↓ YES → Motion
    ↓ NO
  ↓
  Do you need spring physics?
    ↓ YES → Motion
    ↓ NO
  ↓
  Is it a hero/landing section?
    ↓ YES → Motion
    ↓ NO
  ↓
  Default → AutoAnimate (80/20 rule)
```

---

## Summary: The 80/20 Rule

**AutoAnimate**: Handles 80% of UI animations with 20% of the effort
**Motion**: Handles 20% of hero/interactive animations with 80% of the features

**Best Practice**: Start with AutoAnimate everywhere. Only add Motion when you hit a specific limitation (gestures, scroll, springs, etc.).

---

## Common Questions

### Q: Can I use AutoAnimate for drag & drop?
**A**: No. Use Motion (`drag` prop) or React DnD.

### Q: Can I use Motion for simple lists?
**A**: You can, but it's overkill. AutoAnimate is simpler and smaller.

### Q: What if I need custom easing curves?
**A**: Use Motion. AutoAnimate only supports CSS easing (ease-in-out, etc.).

### Q: What if I need animations to run on scroll?
**A**: Use Motion (`useScroll` hook) or Intersection Observer + AutoAnimate.

### Q: Can I animate SVG paths with AutoAnimate?
**A**: No. Use Motion (`motion.path` with `pathLength` animation).

### Q: What if I need animations to run on mount only?
**A**: Both work. AutoAnimate is simpler (just add ref). Motion gives more control.

---

## Conclusion

**Default to AutoAnimate** for 90% of UI animations:
- Lists, accordions, toasts, forms, tabs, modals

**Upgrade to Motion** for the 10% that need:
- Gestures, scroll animations, spring physics, hero sections, layout animations

**Both together**: Perfectly fine! Use each for their strengths.

**Remember**: The best animation is the one that ships. AutoAnimate ships faster.
