// AutoAnimate - TypeScript Setup with Configuration
// @formkit/auto-animate v0.9.0

import { useAutoAnimate } from "@formkit/auto-animate/react";
import type { AutoAnimateOptions, AnimationController } from "@formkit/auto-animate";
import { useState } from "react";

/**
 * Example: TypeScript Setup with Custom Configuration
 *
 * This shows:
 * - Proper TypeScript types
 * - Custom animation duration/easing
 * - Access to animation controller
 * - Type-safe configuration
 */

interface Task {
  id: string;
  title: string;
  completed: boolean;
}

export function TypeScriptExample() {
  // Custom configuration with types
  const animationConfig: Partial<AutoAnimateOptions> = {
    duration: 250, // milliseconds
    easing: "ease-in-out",
    // disrespectUserMotionPreference: false, // Keep false for accessibility
  };

  // Get ref and controller with proper types
  const [parent, controller] = useAutoAnimate<HTMLUListElement>(animationConfig);

  const [tasks, setTasks] = useState<Task[]>([
    { id: "1", title: "Learn AutoAnimate", completed: false },
    { id: "2", title: "Build awesome UI", completed: false },
  ]);

  const [newTaskTitle, setNewTaskTitle] = useState("");

  const addTask = () => {
    if (!newTaskTitle.trim()) return;

    const newTask: Task = {
      id: Date.now().toString(),
      title: newTaskTitle,
      completed: false,
    };

    setTasks([...tasks, newTask]);
    setNewTaskTitle("");
  };

  const toggleTask = (id: string) => {
    setTasks(
      tasks.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const deleteTask = (id: string) => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  // Optional: Manually enable/disable animations
  const toggleAnimations = () => {
    if (controller) {
      controller.isEnabled() ? controller.disable() : controller.enable();
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">Tasks</h2>

      {/* Add task form */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addTask()}
          placeholder="New task..."
          className="flex-1 px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={addTask}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add
        </button>
      </div>

      {/* Task list with ref */}
      <ul ref={parent} className="space-y-2">
        {tasks.map((task) => (
          <li
            key={task.id}
            className={`flex items-center gap-3 p-4 border rounded ${
              task.completed ? "bg-gray-50" : "bg-white"
            }`}
          >
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => toggleTask(task.id)}
              className="w-5 h-5"
            />
            <span
              className={`flex-1 ${
                task.completed ? "line-through text-gray-500" : ""
              }`}
            >
              {task.title}
            </span>
            <button
              onClick={() => deleteTask(task.id)}
              className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
            >
              Delete
            </button>
          </li>
        ))}

        {tasks.length === 0 && (
          <li className="p-4 text-center text-gray-500">
            No tasks yet. Add one above!
          </li>
        )}
      </ul>

      {/* Optional: Animation toggle */}
      <button
        onClick={toggleAnimations}
        className="text-sm text-gray-600 underline"
      >
        Toggle Animations
      </button>
    </div>
  );
}

/**
 * TypeScript Tips:
 *
 * 1. Import types from @formkit/auto-animate
 * import type { AutoAnimateOptions, AnimationController } from "@formkit/auto-animate";
 *
 * 2. Type the ref explicitly
 * const [parent, controller] = useAutoAnimate<HTMLUListElement>();
 *
 * 3. Use Partial<AutoAnimateOptions> for config
 * const config: Partial<AutoAnimateOptions> = { duration: 250 };
 *
 * 4. Controller methods (optional)
 * controller.enable() - Enable animations
 * controller.disable() - Disable animations
 * controller.isEnabled() - Check if enabled
 */

/**
 * Configuration Options:
 *
 * duration: number (default: 250ms)
 * easing: string (default: "ease-in-out")
 * disrespectUserMotionPreference: boolean (default: false) - Keep false!
 *
 * Note: AutoAnimate automatically respects prefers-reduced-motion
 * unless disrespectUserMotionPreference is true (NOT recommended)
 */
