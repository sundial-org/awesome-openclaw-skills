// AutoAnimate - SSR-Safe Pattern for Cloudflare Workers
// Prevents "useEffect not defined" errors in server environments

import { useState, useEffect } from "react";
import type { AutoAnimateOptions } from "@formkit/auto-animate";

/**
 * SSR-Safe AutoAnimate Hook
 *
 * Problem: AutoAnimate uses DOM APIs that don't exist on the server
 * Solution: Only import and use AutoAnimate on the client side
 *
 * This pattern works for:
 * - Cloudflare Workers + Static Assets
 * - Next.js (App Router & Pages Router)
 * - Remix
 * - Any SSR/SSG environment
 */

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

/**
 * Alternative: useAutoAnimate from react package (client-only import)
 */
export function ClientOnlyAutoAnimate({ children }: { children: React.ReactNode }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    // Server render: return children without animation
    return <>{children}</>;
  }

  // Client render: use AutoAnimate
  return <AnimatedList>{children}</AnimatedList>;
}

function AnimatedList({ children }: { children: React.ReactNode }) {
  // This import only runs on client
  const { useAutoAnimate } = require("@formkit/auto-animate/react");
  const [parent] = useAutoAnimate();

  return <div ref={parent}>{children}</div>;
}

/**
 * Example Usage: Todo List with SSR-Safe Hook
 */
interface Todo {
  id: number;
  text: string;
}

export function SSRSafeTodoList() {
  // Use the SSR-safe hook
  const [parent, setParent] = useAutoAnimateSafe<HTMLUListElement>();

  const [todos, setTodos] = useState<Todo[]>([
    { id: 1, text: "Server-rendered todo" },
  ]);

  const [newTodo, setNewTodo] = useState("");

  const addTodo = () => {
    if (!newTodo.trim()) return;
    setTodos([...todos, { id: Date.now(), text: newTodo }]);
    setNewTodo("");
  };

  const removeTodo = (id: number) => {
    setTodos(todos.filter((t) => t.id !== id));
  };

  return (
    <div className="max-w-md mx-auto p-6 space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addTodo()}
          placeholder="New todo..."
          className="flex-1 px-3 py-2 border rounded"
        />
        <button
          onClick={addTodo}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Add
        </button>
      </div>

      {/* Set ref using callback pattern for SSR safety */}
      <ul ref={setParent} className="space-y-2">
        {todos.map((todo) => (
          <li
            key={todo.id}
            className="flex items-center justify-between p-4 bg-white border rounded"
          >
            <span>{todo.text}</span>
            <button
              onClick={() => removeTodo(todo.id)}
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
 * Cloudflare Workers Configuration
 *
 * In vite.config.ts:
 * import { defineConfig } from "vite";
 * import react from "@vitejs/plugin-react";
 * import cloudflare from "@cloudflare/vite-plugin";
 *
 * export default defineConfig({
 *   plugins: [react(), cloudflare()],
 *   build: {
 *     outDir: "dist",
 *   },
 *   ssr: {
 *     // Exclude AutoAnimate from SSR bundle
 *     noExternal: [],
 *     external: ["@formkit/auto-animate"],
 *   },
 * });
 *
 * This ensures AutoAnimate only runs in the browser (Static Assets),
 * not in the Worker runtime.
 */

/**
 * Common SSR Errors Prevented:
 *
 * ❌ "ReferenceError: window is not defined"
 * ❌ "Cannot find module '@formkit/auto-animate/react'"
 * ❌ "useEffect is not defined"
 * ❌ "document is not defined"
 *
 * ✅ All prevented by client-only import + conditional rendering
 */
