---
name: a11y-checker
description: "Scan HTML and JSX files for WCAG accessibility violations and generate concrete code fixes. Detects missing alt text, low color contrast, missing form labels, keyboard navigation issues, and ARIA misuse. Use when auditing web components for accessibility, preparing for compliance reviews, or adding accessibility gates to CI/CD pipelines."
---

# A11y Checker

Scan HTML and JSX files for WCAG accessibility violations and generate concrete code fixes.

## Workflow

1. Run scan on target files or directory.
2. Review detected violations and generated fixes.
3. Apply fixes and re-scan to verify resolution.
4. Optionally integrate into CI/CD as a gate.

## Usage

```bash
# Scan a single component
npx ai-a11y ./src/components/Button.tsx

# Scan all components in a directory
npx ai-a11y ./src/components/

# Scan with verbose output for detailed violation info
npx ai-a11y ./src --verbose
```

## Example Output

```
src/components/Header.tsx
  Line 12: <img> missing alt attribute
    Fix: <img src="logo.png" alt="Company logo" />
  Line 28: <button> has no accessible name
    Fix: <button aria-label="Close dialog">×</button>

2 issues found, 2 fixes generated
```

## CI/CD Integration

```bash
# Add as a pre-commit or CI gate (exits non-zero on violations)
npx ai-a11y ./src --verbose
# Exit code 0 = no issues, non-zero = violations found
```

## Requirements

- Node.js 18+
- `OPENAI_API_KEY` environment variable set

## References

- [GitHub repository](https://github.com/lxgicstudios/ai-a11y)
