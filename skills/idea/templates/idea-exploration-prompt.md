# Idea Exploration Template

Use this template when researching a new idea captured in IDEAS.md.

---

## Prompt

```
I have an idea I'd like you to explore in depth:

**Idea:** {IDEA_DESCRIPTION}

Please research and analyze this idea comprehensively:

1. **Core Concept Analysis**
   - Break down the core problem/opportunity
   - Key assumptions and hypothesis
   - What makes this interesting/unique?

2. **Market Research**
   - Who would use this?
   - What's the market size/opportunity?
   - Existing solutions and competitors
   - Market gaps this could fill

3. **Technical Implementation**
   - Possible technical approaches
   - Key technical challenges
   - Required resources/skills
   - MVP scope and complexity

4. **Use Cases**
   - Primary use cases (3-5)
   - User personas
   - User journey/flow
   - Value proposition for each persona

5. **Go-to-Market Strategy**
   - Target customer segment
   - Distribution channels
   - Pricing models
   - Launch strategy

6. **Risks & Challenges**
   - Technical risks
   - Market risks
   - Competitive risks
   - Execution risks

7. **Next Steps**
   - Should we pursue this?
   - If yes: What's the minimal first step?
   - What would validate/invalidate this idea?
   - Timeline for a quick prototype

Please be thorough but practical. Focus on actionable insights.

**When you're done:**
1. Save your research to: ~/clawd/ideas/{IDEA_SLUG}/research.md
2. Run this command to notify that research is complete:
   ```bash
   ~/clawd/scripts/notify-research-complete.sh "{IDEA_SLUG}" "{SESSION_ID}"
   ```
```

---

## Variables to Replace

- `{IDEA_DESCRIPTION}`: The actual idea text
- `{IDEA_SLUG}`: URL-friendly version (e.g., "ai-powered-calendar" from "AI-Powered Calendar Assistant")
