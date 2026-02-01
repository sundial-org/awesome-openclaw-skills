# Document Design Reference

Practical guide for creating well-formatted documents for Nudocs.

---

## Structure Planning

### ASCII Outline Technique

Before writing, sketch your document structure:

```
# Title
  ## Section A
    - Point 1
    - Point 2
  ## Section B
    ### Subsection
    - Details
  ## Conclusion
```

This reveals hierarchy problems before you write content.

### Document Type Quick Patterns

| Type | Structure |
|------|-----------|
| Blog | Hook → Problem → Solution → CTA |
| Report | Summary → Findings → Analysis → Recommendations |
| How-to | Intro → Prerequisites → Steps → Conclusion |
| Analysis | Context → Data → Insights → Implications |

---

## Typography Hierarchy

### Heading Levels

| Level | Use For |
|-------|---------|
| H1 | Document title only (one per doc) |
| H2 | Major sections |
| H3 | Subsections within H2 |
| H4 | Minor divisions (use sparingly) |

**Rule**: Never skip levels. H2 → H4 is wrong; use H2 → H3.

### Text Emphasis

| Style | Purpose | Example |
|-------|---------|---------|
| **Bold** | Key terms, important points | **Required** field |
| *Italic* | Titles, new concepts, subtle emphasis | The *cascade* effect |
| `Code` | Technical terms, commands, values | Set `timeout` to `30` |

**Avoid**: Bold italic, ALL CAPS, excessive emphasis.

### Paragraph Guidelines

- **Ideal length**: 2-4 sentences
- **Max length**: 6 sentences (break up long paragraphs)
- **One idea per paragraph**
- Lead with the main point, then support

---

## Spacing Rules

### Between Elements

| Element Pair | Spacing |
|--------------|---------|
| Paragraph → Paragraph | Single blank line |
| Paragraph → Heading | Single blank line |
| Heading → Content | No blank line |
| List → Paragraph | Single blank line |
| Code block → Text | Single blank line |

### Example (Correct)

```markdown
Introduction paragraph here.

## Section Title
Content starts immediately after heading.

Another paragraph with space before it.
```

### Example (Wrong)

```markdown
Introduction paragraph here.
## Section Title

Content with wrong spacing.
```

---

## List Best Practices

### When to Use Each Type

| Type | Use When |
|------|----------|
| Bullets | Items have no sequence/priority |
| Numbers | Order matters, steps, rankings |
| Checklists | Task tracking, requirements |

### Nesting Rules

- **Max depth**: 2 levels (main + one sub)
- **Deeper nesting**: Restructure as separate sections
- **Consistency**: Same punctuation style within a list

### Formatting Consistency

**Do this**:
- Start each item with capital letter
- Use same grammatical structure (all verbs, all nouns)
- End with periods if items are sentences

**Not this**:
- some items lowercase
- Others Are Capitalized
- punctuation varies;

---

## Visual Elements

### Block Quotes

Use for:
- Callouts and important notes
- Definitions
- Quotes from sources

```markdown
> **Note**: This highlights critical information that readers shouldn't miss.
```

> **Tip**: Keep callouts brief—one to three sentences max.

### Horizontal Rules

Use to separate:
- Major document sections
- Unrelated content blocks
- Header/footer from body

```markdown
Content above.

---

Content below (distinctly different topic).
```

**Avoid**: Multiple consecutive rules, rules within sections.

### Tables

**Good for**:
- Comparisons
- Reference data
- Structured information

**Structure tips**:
- Keep columns under 5 when possible
- Left-align text, right-align numbers
- Use header row always

```markdown
| Feature | Free | Pro |
|---------|------|-----|
| Storage | 5GB | 50GB |
| Support | Email | Priority |
```

### Code Blocks

**Inline code**: Single commands, values, short references
```markdown
Run `npm install` to begin.
```

**Fenced blocks**: Multi-line code, examples, configs
```markdown
```javascript
function example() {
  return true;
}
```
```

Always specify the language for syntax highlighting.

---

## Document Templates

### Blog Post

```markdown
# [Compelling Title]

[Hook: One sentence that grabs attention]

[Problem: 1-2 paragraphs on the issue/question]

## [Solution/Main Point]

[Core content: 3-5 paragraphs with examples]

## Key Takeaways

- Point 1
- Point 2
- Point 3

## What's Next

[Call to action: What should reader do now?]
```

### Report

```markdown
# [Report Title]

## Executive Summary

[2-3 paragraph overview of findings and recommendations]

## Findings

### [Finding 1]
[Details and evidence]

### [Finding 2]
[Details and evidence]

## Analysis

[Interpretation of findings, patterns, implications]

## Recommendations

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

## Appendix

[Supporting data, methodology, references]
```

### How-To Guide

```markdown
# How to [Accomplish Task]

[Brief intro: What this guide covers and who it's for]

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### Step 1: [Action]
[Instructions]

### Step 2: [Action]
[Instructions]

### Step 3: [Action]
[Instructions]

## Troubleshooting

**Problem**: [Common issue]
**Solution**: [Fix]

## Summary

[Recap what was accomplished, next steps]
```

### Analysis Document

```markdown
# [Analysis Title]

## Context

[Background: Why this analysis, what prompted it]

## Data

[Sources, methodology, key metrics]

| Metric | Value | Change |
|--------|-------|--------|
| [X] | [Y] | [Z] |

## Insights

### [Insight 1]
[Explanation and evidence]

### [Insight 2]
[Explanation and evidence]

## Implications

[What this means, recommended actions]

## Limitations

[Caveats, data gaps, assumptions]
```

---

## Quick Reference Checklist

Before uploading to Nudocs:

- [ ] Single H1 title at top
- [ ] Logical heading hierarchy (no skipped levels)
- [ ] Consistent list formatting
- [ ] Paragraphs under 6 sentences
- [ ] Single blank lines between elements
- [ ] Code blocks have language specified
- [ ] Tables have header rows
- [ ] No excessive emphasis (bold/italic)
- [ ] Callouts used sparingly
