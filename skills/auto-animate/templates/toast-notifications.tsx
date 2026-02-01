// AutoAnimate - Toast Notifications
// Fade in/out for temporary messages

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState, useEffect } from "react";

interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

export function ToastExample() {
  const [parent] = useAutoAnimate();
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: Toast["type"]) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  };

  return (
    <div className="p-6">
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => addToast("Success!", "success")}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Success Toast
        </button>
        <button
          onClick={() => addToast("Error occurred", "error")}
          className="px-4 py-2 bg-red-600 text-white rounded"
        >
          Error Toast
        </button>
        <button
          onClick={() => addToast("Info message", "info")}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Info Toast
        </button>
      </div>

      {/* Toast container */}
      <div
        ref={parent}
        className="fixed top-4 right-4 space-y-2 w-80"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`p-4 rounded shadow-lg ${
              toast.type === "success"
                ? "bg-green-500"
                : toast.type === "error"
                ? "bg-red-500"
                : "bg-blue-500"
            } text-white`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}
