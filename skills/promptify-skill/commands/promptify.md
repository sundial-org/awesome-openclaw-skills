---
name: promptify
description: "+ask +deep +web <- modifiers | optimize your prompts"
---

# Prompt Optimizer

Transform prompts into clear, effective ones. Model-agnostic.

## Modifiers (parse from ARGUMENTS)

- **+ask** → Ask 1-3 clarifying questions first (use AskUserQuestion)
- **+deep** → Explore codebase with Glob/Grep/Read for patterns
- **+web** → Web search for current best practices (2024-2026)

## Core Contract (every prompt needs all four)

| Element | Must Answer | If Missing |
|---------|-------------|------------|
| **Role** | Who is the model? | Add persona with expertise |
| **Task** | What exactly to do? | Make action specific |
| **Constraints** | What rules apply? | Infer from context |
| **Output** | What does done look like? | Specify format/structure |

## Process

1. **If image**: Analyze UI/diagram/example, incorporate into prompt
2. **If +deep**: Find relevant files, patterns, conventions (CLAUDE.md, README)
3. **If +web**: Search best practices, API docs, recent patterns
4. **If +ask**: Ask 1-3 questions (audience? constraints? success criteria?)
5. **Detect type**: coding/writing/analysis/creative/data
6. **Convert output→process**: "Write X" → "Analyze → Plan → Implement → Validate"
7. **Strip fluff**: Remove "please", "I want you to", filler words, apologies
8. **Apply contract**: Verify all 4 elements present
9. **Add structure**: XML tags for complex prompts (`<context>`, `<task>`, `<format>`)

## Type-Specific Focus

- **Coding**: Precise specs, edge cases, language/framework
- **Writing**: Tone, audience, length
- **Analysis**: Criteria, depth, structure
- **Creative**: Constraints, quantity, novelty
- **Data**: Input/output format, edge cases

## Techniques (apply as needed)

- Replace vague words with criteria
- Add "Do NOT..." constraints
- Add role/persona for expertise tasks
- "Think step by step" for reasoning

## Output

1. Optimized prompt in code block
2. `echo 'PROMPT' | pbcopy`
3. 2-3 sentence explanation
