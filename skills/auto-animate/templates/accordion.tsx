// AutoAnimate - Accordion Example
// Smooth expand/collapse animations

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState } from "react";

interface AccordionItem {
  id: string;
  title: string;
  content: string;
}

const items: AccordionItem[] = [
  {
    id: "1",
    title: "What is AutoAnimate?",
    content:
      "AutoAnimate is a zero-config, drop-in animation utility that automatically adds smooth transitions to elements.",
  },
  {
    id: "2",
    title: "How do I use it?",
    content:
      "Just import useAutoAnimate, get a ref, and attach it to a parent element. That's it!",
  },
  {
    id: "3",
    title: "Is it accessible?",
    content:
      "Yes! AutoAnimate automatically respects prefers-reduced-motion settings.",
  },
];

export function AccordionExample() {
  const [openId, setOpenId] = useState<string | null>(null);

  const toggle = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-2">
      {items.map((item) => (
        <AccordionItem
          key={item.id}
          item={item}
          isOpen={openId === item.id}
          onToggle={() => toggle(item.id)}
        />
      ))}
    </div>
  );
}

function AccordionItem({
  item,
  isOpen,
  onToggle,
}: {
  item: AccordionItem;
  isOpen: boolean;
  onToggle: () => void;
}) {
  // Animate the content div
  const [parent] = useAutoAnimate();

  return (
    <div className="border rounded overflow-hidden">
      {/* Header (always visible) */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 text-left"
      >
        <span className="font-semibold">{item.title}</span>
        <svg
          className={`w-5 h-5 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Content (conditionally rendered, animated by parent ref) */}
      <div ref={parent}>
        {isOpen && (
          <div className="p-4 bg-white border-t">
            <p className="text-gray-700">{item.content}</p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Key Pattern:
 * - Parent ref wraps the conditionally rendered content
 * - Parent div is always in DOM (not conditional)
 * - Only the child content is conditional
 *
 * ❌ Wrong: <div ref={parent}>{isOpen && <div>...</div>}</div> is outside component
 * ✅ Correct: <div ref={parent}>{isOpen && <div>...</div>}</div> inside component
 */
