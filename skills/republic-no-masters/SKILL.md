---
name: republic-no-masters
description: Explain, summarize, analyze, or adapt the "Republic with No Masters" / Democratic Formalism governance framework when asked to produce content, guidance, critiques, FAQs, or implementation ideas based on the manifesto in principles.md.
---

# Republic with No Masters

Use this skill to produce faithful, clear outputs grounded in the manifesto.

## Source of truth

- Always read `principles.md` before answering.
- Treat `principles.md` as authoritative; do not invent new claims or terminology.
- If asked for extensions or speculative ideas, label them explicitly as proposals or interpretations.

## Core workflow

1. Identify the request type: summary, explanation, application, critique, or derivative writing.
2. Load `principles.md` and extract only the relevant sections.
3. Map the request to the manifesto's defined terms (e.g., Values/Execution/Oversight, Agency Firewall, Quad-Lock, Hard-Coded Floor, Receipt).
4. Draft the response in the requested format and tone while preserving the framework's intent.
5. If the user wants changes to the manifesto, propose edits as diffs or bullet changes and ask for confirmation before rewriting.

## Output patterns

- **Short summary (1-2 paragraphs)**: Focus on the separation of Values and Execution, independent agents, and oversight; mention the Receipt as the atomic unit.
- **Longer overview**: Walk through the Agency Firewall, Quad-Lock, Meritocracy/Entropy, Debugging Protocol, and Hard-Coded Floor.
- **FAQ or Q&A**: Tie each answer to a named section in `principles.md`; avoid adding new doctrine.
- **Policy or system design**: Provide concrete examples (e.g., how a Receipt would look) while staying consistent with the constraints in the manifesto.
- **Public-facing writing**: Keep the tone crisp, declarative, and manifesto-like; avoid jargon not present in `principles.md`.

## Guardrails

- Do not claim real-world adoption, legal enforceability, or operational readiness unless the user provides evidence.
- Do not present speculative extensions as existing policy.
- Keep the language precise; preserve capitalization of named constructs (e.g., Hard-Coded Floor, Quad-Lock).

