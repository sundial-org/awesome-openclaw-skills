#!/bin/bash
# AutoAnimate Setup Script
# Automates installation and initial setup for React + Vite + Cloudflare Workers projects

set -e

echo "🎬 AutoAnimate Setup"
echo "===================="
echo ""

# Check if we're in a React project
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found"
  echo "   Run this script from your project root"
  exit 1
fi

# Check if React is installed
if ! grep -q '"react"' package.json; then
  echo "❌ Error: React not found in package.json"
  echo "   This script is for React projects"
  exit 1
fi

echo "✅ React project detected"
echo ""

# Install AutoAnimate
echo "📦 Installing @formkit/auto-animate..."
if command -v pnpm &> /dev/null; then
  pnpm add @formkit/auto-animate
elif command -v yarn &> /dev/null; then
  yarn add @formkit/auto-animate
else
  npm install @formkit/auto-animate
fi

echo "✅ Package installed"
echo ""

# Check if using Cloudflare Workers
USING_CLOUDFLARE=false
if grep -q '@cloudflare/vite-plugin' package.json; then
  USING_CLOUDFLARE=true
  echo "🔍 Detected: Cloudflare Workers project"
  echo ""
fi

# Create SSR-safe hook if using Cloudflare or Next.js
if [ "$USING_CLOUDFLARE" = true ] || grep -q 'next' package.json; then
  echo "📝 Creating SSR-safe hook..."

  # Create src/hooks directory if it doesn't exist
  mkdir -p src/hooks

  # Create useAutoAnimateSafe.ts
  cat > src/hooks/useAutoAnimateSafe.ts << 'EOF'
// AutoAnimate SSR-Safe Hook
// Use this instead of useAutoAnimate for Cloudflare Workers or Next.js

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
EOF

  echo "✅ Created: src/hooks/useAutoAnimateSafe.ts"
  echo ""

  # Update vite.config.ts if using Cloudflare
  if [ "$USING_CLOUDFLARE" = true ] && [ -f "vite.config.ts" ]; then
    echo "📝 Updating vite.config.ts..."

    # Check if ssr.external already exists
    if grep -q "ssr:" vite.config.ts; then
      echo "⚠️  SSR config already exists in vite.config.ts"
      echo "   Add '@formkit/auto-animate' to ssr.external manually"
    else
      # Backup original
      cp vite.config.ts vite.config.ts.backup

      # Add ssr.external (simplified approach)
      echo ""
      echo "⚠️  Manual step required:"
      echo "   Add this to your vite.config.ts:"
      echo ""
      echo "   ssr: {"
      echo "     external: ['@formkit/auto-animate'],"
      echo "   },"
      echo ""
    fi
  fi
fi

# Create example component
echo "📝 Creating example component..."
mkdir -p src/components

cat > src/components/AnimatedListExample.tsx << 'EOF'
// AutoAnimate Example Component
// Copy this to your project and customize as needed

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState } from "react";

interface Item {
  id: number;
  text: string;
}

export function AnimatedListExample() {
  const [parent] = useAutoAnimate();
  const [items, setItems] = useState<Item[]>([
    { id: 1, text: "Item 1" },
    { id: 2, text: "Item 2" },
    { id: 3, text: "Item 3" },
  ]);
  const [newText, setNewText] = useState("");

  const addItem = () => {
    if (!newText.trim()) return;
    setItems([...items, { id: Date.now(), text: newText }]);
    setNewText("");
  };

  const removeItem = (id: number) => {
    setItems(items.filter((item) => item.id !== id));
  };

  const shuffleItems = () => {
    setItems([...items].sort(() => Math.random() - 0.5));
  };

  return (
    <div className="max-w-md mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">AutoAnimate Example</h2>

      <div className="flex gap-2">
        <input
          type="text"
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addItem()}
          placeholder="Add item..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <button
          onClick={addItem}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Add
        </button>
      </div>

      <button
        onClick={shuffleItems}
        className="px-4 py-2 bg-gray-600 text-white rounded"
      >
        Shuffle
      </button>

      {/* Animated list - notice how simple this is! */}
      <ul ref={parent} className="space-y-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between p-4 bg-white border rounded shadow-sm"
          >
            <span>{item.text}</span>
            <button
              onClick={() => removeItem(item.id)}
              className="px-3 py-1 bg-red-500 text-white rounded text-sm"
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
 * Usage:
 *
 * import { AnimatedListExample } from "@/components/AnimatedListExample";
 *
 * function App() {
 *   return <AnimatedListExample />;
 * }
 */
EOF

echo "✅ Created: src/components/AnimatedListExample.tsx"
echo ""

# If using SSR, create SSR-safe example
if [ "$USING_CLOUDFLARE" = true ] || grep -q 'next' package.json; then
  cat > src/components/AnimatedListSSRSafe.tsx << 'EOF'
// AutoAnimate SSR-Safe Example
// Use this version for Cloudflare Workers or Next.js

import { useAutoAnimateSafe } from "../hooks/useAutoAnimateSafe";
import { useState } from "react";

interface Item {
  id: number;
  text: string;
}

export function AnimatedListSSRSafe() {
  // Use SSR-safe hook
  const [parent, setParent] = useAutoAnimateSafe<HTMLUListElement>();

  const [items, setItems] = useState<Item[]>([
    { id: 1, text: "Item 1" },
    { id: 2, text: "Item 2" },
    { id: 3, text: "Item 3" },
  ]);
  const [newText, setNewText] = useState("");

  const addItem = () => {
    if (!newText.trim()) return;
    setItems([...items, { id: Date.now(), text: newText }]);
    setNewText("");
  };

  const removeItem = (id: number) => {
    setItems(items.filter((item) => item.id !== id));
  };

  return (
    <div className="max-w-md mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">AutoAnimate (SSR-Safe)</h2>

      <div className="flex gap-2">
        <input
          type="text"
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addItem()}
          placeholder="Add item..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <button
          onClick={addItem}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Add
        </button>
      </div>

      {/* Use callback ref pattern for SSR safety */}
      <ul ref={setParent} className="space-y-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between p-4 bg-white border rounded shadow-sm"
          >
            <span>{item.text}</span>
            <button
              onClick={() => removeItem(item.id)}
              className="px-3 py-1 bg-red-500 text-white rounded text-sm"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
EOF

  echo "✅ Created: src/components/AnimatedListSSRSafe.tsx"
  echo ""
fi

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Import the example component:"
if [ "$USING_CLOUDFLARE" = true ] || grep -q 'next' package.json; then
  echo "   import { AnimatedListSSRSafe } from '@/components/AnimatedListSSRSafe';"
else
  echo "   import { AnimatedListExample } from '@/components/AnimatedListExample';"
fi
echo ""
echo "2. Add it to your app:"
if [ "$USING_CLOUDFLARE" = true ] || grep -q 'next' package.json; then
  echo "   <AnimatedListSSRSafe />"
else
  echo "   <AnimatedListExample />"
fi
echo ""

if [ "$USING_CLOUDFLARE" = true ]; then
  echo "3. Update vite.config.ts (if not already done):"
  echo "   ssr: {"
  echo "     external: ['@formkit/auto-animate'],"
  echo "   },"
  echo ""
fi

echo "4. Check templates/ folder for more examples:"
echo "   - Accordion components"
echo "   - Toast notifications"
echo "   - Form validation"
echo "   - Filter/sort lists"
echo ""
echo "📚 Documentation: https://auto-animate.formkit.com"
echo ""
