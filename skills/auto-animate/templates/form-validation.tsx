// AutoAnimate - Form Validation Messages
// Error messages that smoothly appear/disappear

import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState } from "react";

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
}

interface Errors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export function FormValidationExample() {
  const [emailParent] = useAutoAnimate();
  const [passwordParent] = useAutoAnimate();
  const [confirmParent] = useAutoAnimate();

  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validate = () => {
    const newErrors: Errors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleBlur = (field: keyof FormData) => {
    setTouched({ ...touched, [field]: true });
    validate();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ email: true, password: true, confirmPassword: true });
    if (validate()) {
      alert("Form submitted successfully!");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 space-y-4">
      {/* Email */}
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          onBlur={() => handleBlur("email")}
          className={`w-full px-3 py-2 border rounded ${
            touched.email && errors.email ? "border-red-500" : ""
          }`}
        />
        <div ref={emailParent}>
          {touched.email && errors.email && (
            <p className="text-red-500 text-sm mt-1">{errors.email}</p>
          )}
        </div>
      </div>

      {/* Password */}
      <div>
        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          onBlur={() => handleBlur("password")}
          className={`w-full px-3 py-2 border rounded ${
            touched.password && errors.password ? "border-red-500" : ""
          }`}
        />
        <div ref={passwordParent}>
          {touched.password && errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password}</p>
          )}
        </div>
      </div>

      {/* Confirm Password */}
      <div>
        <label className="block text-sm font-medium mb-1">Confirm Password</label>
        <input
          type="password"
          value={formData.confirmPassword}
          onChange={(e) =>
            setFormData({ ...formData, confirmPassword: e.target.value })
          }
          onBlur={() => handleBlur("confirmPassword")}
          className={`w-full px-3 py-2 border rounded ${
            touched.confirmPassword && errors.confirmPassword
              ? "border-red-500"
              : ""
          }`}
        />
        <div ref={confirmParent}>
          {touched.confirmPassword && errors.confirmPassword && (
            <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>
          )}
        </div>
      </div>

      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Submit
      </button>
    </form>
  );
}

/**
 * Pattern: Each error message has its own parent ref
 * This allows independent animations for each field
 */
