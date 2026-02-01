// AutoAnimate - Basic React Example
// @formkit/auto-animate v0.9.0

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState } from "react";

/**
 * Example: Simple List Animation with AutoAnimate
 *
 * Key Features:
 * - Zero config - just add the ref
 * - Automatically animates add/remove/move
 * - Respects prefers-reduced-motion
 * - Works with any list structure
 */

interface Item {
  id: number;
  text: string;
}

export function BasicListExample() {
  // 1. Get the ref from useAutoAnimate hook
  const [parent] = useAutoAnimate();

  // 2. Set up state
  const [items, setItems] = useState<Item[]>([
    { id: 1, text: "Item 1" },
    { id: 2, text: "Item 2" },
    { id: 3, text: "Item 3" },
  ]);

  // 3. Functions to modify the list
  const addItem = () => {
    const newId = Math.max(...items.map(item => item.id), 0) + 1;
    setItems([...items, { id: newId, text: `Item ${newId}` }]);
  };

  const removeItem = (id: number) => {
    setItems(items.filter(item => item.id !== id));
  };

  const shuffleItems = () => {
    setItems([...items].sort(() => Math.random() - 0.5));
  };

  return (
    <div className="space-y-4 p-6">
      {/* Controls */}
      <div className="flex gap-2">
        <button
          onClick={addItem}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add Item
        </button>
        <button
          onClick={shuffleItems}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Shuffle
        </button>
      </div>

      {/* 4. Attach ref to parent element - that's it! */}
      <ul ref={parent} className="space-y-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between p-4 bg-white border rounded shadow-sm"
          >
            <span>{item.text}</span>
            <button
              onClick={() => removeItem(item.id)}
              className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * CRITICAL:
 * - ✅ Always use unique, stable keys for list items
 * - ✅ Attach ref to immediate parent of animated children
 * - ✅ Parent element must always be in DOM (not conditionally rendered)
 * - ✅ AutoAnimate respects prefers-reduced-motion automatically
 */

/**
 * Common Mistakes:
 *
 * ❌ Wrong: Conditional parent
 * {showList && <ul ref={parent}>...</ul>}
 *
 * ✅ Correct: Always-rendered parent, conditional children
 * <ul ref={parent}>{showList && items.map(...)}</ul>
 *
 * ❌ Wrong: Missing or non-unique keys
 * {items.map((item, index) => <li key={index}>...)}
 *
 * ✅ Correct: Unique, stable keys
 * {items.map(item => <li key={item.id}>...)}
 */
