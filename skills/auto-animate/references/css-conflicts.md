# AutoAnimate CSS Conflicts

This document covers CSS layout issues that can break AutoAnimate animations and how to fix them.

---

## Issue #1: Flexbox with `flex-grow: 1`

### Problem

Elements with `flex-grow: 1` snap to width instead of animating smoothly.

**Why it happens**: `flex-grow` waits for surrounding content to calculate final width. AutoAnimate can't animate to an unknown target width.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenList() {
  const [parent] = useAutoAnimate();

  return (
    <div className="flex">
      <ul ref={parent} className="flex-1"> {/* ❌ flex-1 breaks animation */}
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

**Result**: Items flash/snap instead of animating smoothly.

### Solution: Use Explicit Width

```tsx
export function FixedList() {
  const [parent] = useAutoAnimate();

  return (
    <div className="flex">
      <ul ref={parent} className="w-96"> {/* ✅ Explicit width */}
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

**Or use percentage:**

```tsx
<ul ref={parent} className="w-1/2"> {/* ✅ 50% width */}
```

**Or use min-width:**

```tsx
<ul ref={parent} className="flex-1 min-w-0"> {/* ✅ Fallback width */}
```

### Alternative: Apply AutoAnimate to Flex Children

```tsx
export function FlexChildrenList() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent} className="flex flex-col gap-2"> {/* ✅ Flex on parent */}
      {items.map(item => (
        <li key={item.id} className="w-full"> {/* ✅ Explicit width on children */}
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

---

## Issue #2: Table Rows with `display: table-row`

### Problem

Table structure breaks when animating rows. Items disappear or overlap.

**Why it happens**: `display: table-row` conflicts with CSS transforms used by AutoAnimate. During animation, rows temporarily lose table display properties.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenTable() {
  const [parent] = useAutoAnimate();

  return (
    <table>
      <tbody ref={parent}> {/* ❌ Animating <tr> directly breaks layout */}
        {items.map(item => (
          <tr key={item.id}>
            <td>{item.name}</td>
            <td>{item.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Result**: Rows flash, overlap, or disappear during animation.

### Solution #1: Apply to `<tbody>` (Recommended)

```tsx
export function FixedTable() {
  const [parent] = useAutoAnimate();

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody ref={parent}> {/* ✅ Animate tbody, not individual rows */}
        {items.map(item => (
          <tr key={item.id}>
            <td>{item.name}</td>
            <td>{item.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Note**: This animates the entire tbody, not individual rows. For most use cases, this is acceptable.

### Solution #2: Use Div-Based Table Layout

```tsx
export function DivTable() {
  const [parent] = useAutoAnimate();

  return (
    <div className="table w-full">
      <div className="table-header-group">
        <div className="table-row">
          <div className="table-cell font-bold">Name</div>
          <div className="table-cell font-bold">Value</div>
        </div>
      </div>
      <div ref={parent} className="table-row-group"> {/* ✅ Works perfectly */}
        {items.map(item => (
          <div key={item.id} className="table-row">
            <div className="table-cell">{item.name}</div>
            <div className="table-cell">{item.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Tailwind classes:**
- `table` → `display: table`
- `table-row` → `display: table-row`
- `table-cell` → `display: table-cell`
- `table-header-group` → `display: table-header-group`
- `table-row-group` → `display: table-row-group`

### Solution #3: Use CSS Grid (Modern)

```tsx
export function GridTable() {
  const [parent] = useAutoAnimate();

  return (
    <div className="grid grid-cols-2 gap-2">
      {/* Header */}
      <div className="font-bold">Name</div>
      <div className="font-bold">Value</div>

      {/* Body (animated) */}
      <div ref={parent} className="col-span-2 grid grid-cols-2 gap-2">
        {items.map(item => (
          <React.Fragment key={item.id}>
            <div>{item.name}</div>
            <div>{item.value}</div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

---

## Issue #3: Position Changes

### Problem

Layout breaks after adding AutoAnimate because parent element automatically gets `position: relative`.

**Why it happens**: AutoAnimate adds `position: relative` to the parent to enable absolute positioning during animations.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenLayout() {
  const [parent] = useAutoAnimate();

  return (
    <div className="flex items-center"> {/* Parent uses flexbox */}
      <button>Back</button>
      <ul ref={parent}> {/* ❌ Gets position: relative, breaks flex alignment */}
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

**Result**: List no longer aligns vertically with button.

### Solution #1: Account for Position Change

```tsx
export function FixedLayout() {
  const [parent] = useAutoAnimate();

  return (
    <div className="flex items-start"> {/* ✅ Change alignment */}
      <button>Back</button>
      <ul ref={parent} className="relative"> {/* ✅ Explicit position */}
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

### Solution #2: Wrap in Extra Div

```tsx
export function WrappedLayout() {
  const [parent] = useAutoAnimate();

  return (
    <div className="flex items-center">
      <button>Back</button>
      <div> {/* ✅ Wrapper absorbs position: relative */}
        <ul ref={parent}>
          {items.map(item => <li key={item.id}>{item.text}</li>)}
        </ul>
      </div>
    </div>
  );
}
```

### Solution #3: Use CSS to Override

```tsx
export function CSSOverride() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent} style={{ position: 'static' }}> {/* ✅ Force static */}
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  );
}
```

**Warning**: This may break animations in some cases. Test thoroughly.

---

## Issue #4: Absolutely Positioned Elements

### Problem

Absolutely positioned children don't animate correctly.

**Why it happens**: AutoAnimate assumes children are in normal document flow. Absolute positioning removes elements from flow.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenAbsolute() {
  const [parent] = useAutoAnimate();

  return (
    <div ref={parent} className="relative">
      {items.map(item => (
        <div key={item.id} className="absolute top-0 left-0"> {/* ❌ Doesn't animate */}
          {item.text}
        </div>
      ))}
    </div>
  );
}
```

**Result**: Items overlap, don't animate.

### Solution: Use Relative or Static Positioning

```tsx
export function FixedAbsolute() {
  const [parent] = useAutoAnimate();

  return (
    <div ref={parent} className="space-y-2"> {/* ✅ Normal flow */}
      {items.map(item => (
        <div key={item.id} className="relative"> {/* ✅ Relative for internal positioning */}
          {item.text}
        </div>
      ))}
    </div>
  );
}
```

**If you need absolute positioning:**

```tsx
export function StackedAbsolute() {
  const [parent] = useAutoAnimate();

  return (
    <div ref={parent} className="relative h-96"> {/* ✅ Fixed height */}
      {items.map((item, index) => (
        <div
          key={item.id}
          className="absolute left-0"
          style={{ top: `${index * 80}px` }} {/* ✅ Calculate position */}
        >
          {item.text}
        </div>
      ))}
    </div>
  );
}
```

---

## Issue #5: Fixed Height Containers

### Problem

Animations get cut off if parent has fixed height and `overflow: hidden`.

**Why it happens**: Items animating out need space to move. Fixed height + hidden overflow clips them.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenFixedHeight() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent} className="h-64 overflow-hidden"> {/* ❌ Clips animations */}
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  );
}
```

**Result**: Items disappear instantly instead of animating out.

### Solution #1: Use `overflow: visible`

```tsx
export function FixedVisible() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent} className="h-64 overflow-visible"> {/* ✅ Allow overflow */}
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  );
}
```

### Solution #2: Use `min-height` Instead

```tsx
export function MinHeight() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent} className="min-h-64 overflow-hidden"> {/* ✅ Grows as needed */}
      {items.map(item => <li key={item.id}>{item.text}</li>)}
    </ul>
  );
}
```

### Solution #3: Scrollable Container

```tsx
export function Scrollable() {
  const [parent] = useAutoAnimate();

  return (
    <div className="h-64 overflow-auto"> {/* ✅ Scroll if too many items */}
      <ul ref={parent}>
        {items.map(item => <li key={item.id}>{item.text}</li>)}
      </ul>
    </div>
  );
}
```

---

## Issue #6: CSS Transitions on Children

### Problem

If children have their own CSS transitions, they conflict with AutoAnimate.

**Why it happens**: Both CSS transitions and AutoAnimate try to animate the same properties.

### Example (Broken)

```tsx
import { useAutoAnimate } from "@formkit/auto-animate/react";

export function BrokenTransition() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {items.map(item => (
        <li
          key={item.id}
          className="transition-all duration-500" {/* ❌ Conflicts with AutoAnimate */}
        >
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

**Result**: Janky animations, double transitions.

### Solution: Remove CSS Transitions from Children

```tsx
export function FixedTransition() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {items.map(item => (
        <li key={item.id}> {/* ✅ No transition on children */}
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

**Or apply transitions only to specific properties:**

```tsx
export function SelectiveTransition() {
  const [parent] = useAutoAnimate();

  return (
    <ul ref={parent}>
      {items.map(item => (
        <li
          key={item.id}
          className="transition-colors duration-200" {/* ✅ Only color transitions */}
        >
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

---

## Summary: CSS Conflict Checklist

Before adding AutoAnimate, check for:

- [ ] `flex-grow: 1` on parent → Use explicit width instead
- [ ] `display: table-row` on children → Apply ref to `<tbody>` or use div-based layout
- [ ] Existing `position: absolute/fixed` → Use relative/static positioning
- [ ] Fixed height + `overflow: hidden` → Use `overflow: visible` or `min-height`
- [ ] CSS transitions on children → Remove or scope to specific properties
- [ ] Complex flexbox/grid layouts → Test thoroughly, may need wrapper div

**General Rule**: AutoAnimate works best with simple, flow-based layouts. Complex layouts may need refactoring.

---

## Debugging CSS Conflicts

### Step 1: Isolate the Problem

Remove AutoAnimate temporarily:

```tsx
// const [parent] = useAutoAnimate(); // ← Comment out
const parent = null; // ← Add this

return (
  <ul ref={parent}> {/* Layout should work without animation */}
    {items.map(item => <li key={item.id}>{item.text}</li>)}
  </ul>
);
```

If layout works without AutoAnimate → CSS conflict. If not → different issue.

### Step 2: Check Computed Styles

In browser DevTools:
1. Inspect parent element
2. Check "Computed" tab
3. Look for unexpected `position`, `display`, `overflow` values

### Step 3: Test with Minimal CSS

Remove all Tailwind classes temporarily:

```tsx
const [parent] = useAutoAnimate();

return (
  <ul ref={parent}> {/* No classes */}
    {items.map(item => <li key={item.id}>{item.text}</li>)}
  </ul>
);
```

If animations work → One of your CSS classes caused the conflict.

Add classes back one at a time to identify the culprit.

---

## Getting Help

If you encounter a CSS conflict not covered here:

1. Create minimal reproduction at https://codesandbox.io
2. Open issue at https://github.com/formkit/auto-animate/issues
3. Include:
   - CSS classes/styles applied
   - Expected behavior
   - Actual behavior
   - Browser version

The AutoAnimate team is responsive and helpful!
