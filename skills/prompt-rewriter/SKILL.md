---
name: prompt-rewriter
description: Advanced prompt rewriting and optimization service. Analyzes prompts for clarity, specificity, structure, completeness, and usability. Identifies weaknesses, suggests improvements, and generates multiple rewrite options. Use when users need to improve an existing prompt's effectiveness, understand why a prompt isn't working well, generate variations of a prompt for A/B testing, or learn prompt engineering best practices through examples.
---

# Prompt Rewriter

## Overview

Help users transform vague, ineffective prompts into powerful, well-structured instructions that produce consistent, high-quality results from AI models. Analyzes prompts across multiple quality dimensions and provides actionable suggestions.

## Quick Start

**User says**: "Help me rewrite this prompt: 'Write a blog post about AI'"

**You should**:
1. Analyze the original prompt's weaknesses (too vague, no audience specified, no format defined)
2. Identify improvement areas (add topic specificity, target audience, tone, length, structure)
3. Provide 2-3 rewrite options with different approaches
4. Explain the changes and why they matter

---

## Core Capabilities

### 1. Prompt Quality Analysis

Evaluate prompts across five key dimensions:

**Clarity** (0-2)
- Is the request unambiguous?
- Are terms defined?
- Can Claude understand without clarification?

**Specificity** (0-2)
- Are constraints clear?
- Is output format specified?
- Are boundaries defined?

**Structure** (0-2)
- Is information organized logically?
- Are steps clear if applicable?
- Is there a framework?

**Completeness** (0-2)
- Is sufficient context provided?
- Are requirements comprehensive?
- Is missing information flagged?

**Usability** (0-2)
- Is it reusable?
- Can it be adapted easily?
- Is the language natural?

**Scoring**:
- 8-10: Excellent prompt, minor tweaks needed
- 6-7: Good prompt, moderate improvements possible
- 4-5: Functional but has significant weaknesses
- 0-3: Poor prompt, needs major rework

### 2. Rewrite Generation

Generate 2-3 rewrite variations using different approaches:

**Variation 1: Conservative Fix**
- Keep original intent
- Add specificity and structure
- Minimal stylistic changes
- Best when user wants to preserve voice

**Variation 2: Technique Enhancement**
- Apply prompt engineering patterns (CoT, few-shot, etc.)
- Add advanced techniques
- Focus on effectiveness
- Best when user wants optimal results

**Variation 3: Simplification**
- Strip complexity while keeping core request
- Make more conversational
- Focus on ease of use
- Best for beginners or quick tasks

### 3. Improvement Explanation

For each rewrite, explain:
- What changed (specific modifications)
- Why it matters (impact on AI output)
- When to use (appropriate scenarios)

### 4. Pattern Application

Apply proven prompt engineering techniques:

**Chain of Thought (CoT)**
- "Let's think step by step"
- "First, analyze... Then, evaluate..."
- Best for: complex reasoning, math, logic

**Few-Shot Learning**
- Provide 2-3 examples before request
- Pattern: Example 1 → Example 2 → Example 3 → Your task
- Best for: format specification, style matching

**Role-Based Prompts**
- "Act as a senior engineer..."
- "You are a marketing expert..."
- Best for: specialized knowledge, tone control

**Output Structure**
- Use templates and headers
- Define sections explicitly
- Best for: reports, documentation, structured content

**Constraint Definition**
- "Limit response to 500 words"
- "Exclude jargon for non-technical audience"
- Best for: length control, accessibility

### 5. A/B Testing Guidance

Help users test prompts effectively:
- Generate variations systematically
- Suggest test methodology
- Recommend evaluation criteria

---

## Workflow

### Step 1: Receive and Analyze

1. Extract the prompt to rewrite
2. Identify user's intent (what do they want to achieve?)
3. Check for constraints (tone, format, length, audience)
4. Evaluate against 5 quality dimensions
5. Calculate score and identify primary weaknesses

### Step 2: Generate Rewrites

1. **Variation 1 (Conservative)**: Add structure, clarify terms, define output
2. **Variation 2 (Technique-Enhanced)**: Apply relevant patterns (CoT, few-shot, etc.)
3. **Variation 3 (Simplified)**: Make conversational, reduce complexity

### Step 3: Present Options

For each rewrite:
- Show the improved prompt
- Explain the changes
- Highlight which techniques were used
- Recommend which to use based on context

### Step 4: Educational Component

Briefly explain:
- Which prompt engineering techniques were applied
- Why they work in this context
- How the user can apply them in future prompts

---

## Common Patterns and Fixes

### Pattern: Too Vague

**Weak**: "Write about climate change"
**Fix**: Add specificity - audience, purpose, format, depth

**Strong**: "Write a 1000-word blog post for a general audience explaining climate change's causes, effects, and potential solutions. Use an optimistic but realistic tone. Include: (1) introduction with hook, (2) 3 main sections with data, (3) conclusion with actionable advice."

### Pattern: No Structure

**Weak**: "Analyze this data"
**Fix**: Add framework or step-by-step instructions

**Strong**: "Analyze the sales data provided. Structure your response as:
1. **Executive Summary** (3 bullet points of key findings)
2. **Detailed Analysis** (break down by region and product)
3. **Trend Identification** (what patterns emerge?)
4. **Recommendations** (3 actionable steps based on data)"

### Pattern: Missing Context

**Weak**: "Improve this email"
**Fix**: Add context about audience, goal, constraints

**Strong**: "Improve this email for a C-level executive audience. Goal: Get approval for a $50k project. Keep it under 200 words. Tone: Professional but persuasive. Current email: [paste]"

### Pattern: Unclear Output Format

**Weak**: "Create marketing content"
**Fix**: Specify format, style, deliverables

**Strong**: "Create marketing content for our new product launch. Deliver:
1. **Social media post** (LinkedIn, 150 words, professional tone)
2. **Email blurb** (75 words, excitement-focused)
3. **Website headline** (catchy, under 10 words)
4. **3 key benefits** (each under 15 words)"

---

## Examples

### Example 1: Content Creation

**Input Prompt**: "Write an article about remote work"

**Analysis**:
- Clarity: 1/2 (clear topic but vague on specifics)
- Specificity: 0/2 (no format, audience, length)
- Structure: 0/2 (no framework)
- Completeness: 0/2 (missing key details)
- Usability: 1/2 (somewhat reusable)
- **Score: 2/10** - Major weaknesses across dimensions

**Rewrite Option 1 (Conservative)**:
```
Write a 1500-word article about remote work for business professionals. Cover:
1. Benefits of remote work (productivity, cost savings, flexibility)
2. Challenges (isolation, communication, work-life balance)
3. Best practices for success (routine, communication tools, workspace setup)
4. Future trends (hybrid models, technology evolution)

Tone: Informative and balanced
Format: Use headings and bullet points
```

**Rewrite Option 2 (Technique-Enhanced)**:
```
Act as an experienced remote work consultant. Write a comprehensive article about remote work for business leaders considering transitioning their teams.

Structure your response using the following framework:

**Introduction (150 words)**
- Hook with a surprising statistic
- Briefly state the article's purpose
- Outline what will be covered

**Section 1: The Business Case (400 words)**
Let's think about this step by step:
- Analyze cost benefits (real estate, equipment, turnover)
- Evaluate productivity studies (with data sources)
- Consider talent access (hiring from anywhere)

**Section 2: Implementation Challenges (350 words)**
- Communication breakdowns (provide examples)
- Culture maintenance (specific strategies)
- Performance management (tools and metrics)

**Section 3: Success Framework (400 words)**
Provide a concrete 90-day rollout plan:
- Month 1: Foundation and tools
- Month 2: Training and feedback
- Month 3: Optimization and refinement

**Conclusion (200 words)**
- Summarize key takeaways
- Provide 3 actionable next steps
- End with an inspiring vision

Tone: Professional yet engaging
Examples: Include 2-3 real company case studies
```

**Rewrite Option 3 (Simplified)**:
```
Write an article about remote work. Make it about 1500 words long and aimed at business people who are thinking about letting employees work from home. Talk about:
- Why it's good (saves money, people like it)
- What's hard (staying in touch, managing performance)
- How to do it right (tools, schedules, clear expectations)

Use a helpful, informative tone with clear headings.
```

**Recommendation**: Use Option 2 if the user wants maximum impact. Use Option 1 for clarity and professionalism. Use Option 3 for quick, casual needs.

---

### Example 2: Code Review

**Input Prompt**: "Review this code"

**Analysis**:
- Clarity: 0/2 (completely unclear what to look for)
- Specificity: 0/2 (no criteria, no scope)
- Structure: 0/2 (no framework)
- Completeness: 0/2 (missing all context)
- Usability: 0/2 (not reusable)
- **Score: 0/10** - Needs complete rework

**Rewrite Option 1 (Conservative)**:
```
Review the code provided below. Focus on:
1. Bugs or errors
2. Performance issues
3. Code style and readability
4. Potential security vulnerabilities

Provide specific line references and suggestions for each issue found.
```

**Rewrite Option 2 (Technique-Enhanced)**:
```
Act as a senior software engineer conducting a thorough code review. Analyze the provided code following this systematic approach:

**Step 1: Functional Analysis**
Let's check if the code works correctly:
- Verify logic correctness (walk through execution)
- Check edge cases (null inputs, empty arrays, boundary conditions)
- Validate error handling (try-catch blocks, meaningful error messages)

**Step 2: Performance Evaluation**
Analyze computational complexity:
- Time complexity: Big-O notation
- Space complexity: Memory usage
- Identify any O(n²) or worse bottlenecks
- Suggest optimization opportunities

**Step 3: Security Review**
Look for common vulnerabilities:
- SQL injection risks
- XSS vulnerabilities
- Improper input validation
- Sensitive data exposure

**Step 4: Code Quality**
Assess adherence to best practices:
- Naming conventions (descriptive, consistent)
- Comments (helpful, not redundant)
- DRY principle (Don't Repeat Yourself)
- Single Responsibility Principle

**Step 5: Recommendations**
Provide:
- Priority-ranked list of issues (Critical > High > Medium > Low)
- Specific code examples for fixes
- Refactoring suggestions for improvement

Code to review:
```

**Rewrite Option 3 (Simplified)**:
```
Look at this code and tell me what's wrong or could be better. Check for bugs, slow parts, security issues, and things that are hard to understand. Give me specific suggestions with examples.

Code:
```

**Recommendation**: Option 2 is best for professional code reviews. Option 1 works for quick checks. Use Option 3 for informal feedback or beginners.

---

### Example 3: Email Writing

**Input Prompt**: "Write an email asking for a meeting"

**Analysis**:
- Clarity: 1/2 (clear intent but vague context)
- Specificity: 0/2 (no purpose, no agenda, no recipient type)
- Structure: 0/2 (no format)
- Completeness: 0/2 (missing all details)
- Usability: 1/2 (somewhat reusable)
- **Score: 2/10** - Needs major improvement

**Rewrite Option 1 (Conservative)**:
```
Write an email requesting a meeting with [recipient name]. Purpose: Discuss [topic].

Include:
- Brief introduction (context)
- Meeting purpose (why we need to meet)
- Proposed agenda (3-4 bullet points)
- Suggested time options (provide 2-3 alternatives)
- Call to action (confirmation request)

Tone: Professional and respectful
Length: Under 200 words
```

**Rewrite Option 2 (Technique-Enhanced)**:
```
Act as an executive assistant drafting a meeting request email to [recipient type, e.g., senior executive/client].

Context: We need to discuss [specific topic] to [desired outcome].

Apply these principles:

**Subject Line Best Practice**
Make it specific and actionable: "Meeting Request: [Topic] - [Urgency/Timeframe]"
Example: "Meeting Request: Q1 Strategy Alignment - This Week"

**Opening Strategy**
First, establish relevance in 1 sentence:
- Reference prior conversation
- Mention shared goal or project
- Acknowledge their value/time

**Value Proposition Frame**
Instead of "I want to meet," use "We'll achieve X by meeting together":
- "In 30 minutes, we can finalize the project timeline"
- "This discussion will unblock the next phase of development"

**Agenda Structure**
Use the SCQA framework:
1. **Situation** (current state)
2. **Complication** (what's blocking us)
3. **Question** (decision needed)
4. **Answer** (your recommendation)

**Time Options Psychology**
Offer specific times with psychological anchors:
- Tuesday 2pm (after lunch, high energy)
- Thursday 10am (start of week, fresh)
- Friday 3pm (end of week, closure mindset)

**Closing**
Make it easy to say yes:
- "If these don't work, suggest your best time"
- "I'll adjust to accommodate your schedule"

Tone: Respectful of their time, clear on value
Length: 150-180 words
```

**Rewrite Option 3 (Simplified)**:
```
Write a short email asking for a meeting with [name]. We need to talk about [topic]. Suggest a few times that would work, mention what we'll cover, and ask them to confirm. Keep it friendly and brief.
```

**Recommendation**: Option 2 is ideal for important business communications. Option 1 works for routine internal emails. Option 3 is fine for casual requests.

---

## Advanced Techniques

### Multiple Rewrites for A/B Testing

When users need to test prompts systematically:

1. **Control**: The original prompt
2. **Variation A**: Change one variable (e.g., add examples)
3. **Variation B**: Change a different variable (e.g., add role)
4. **Variation C**: Combine A + B

Suggest testing methodology:
- Run each prompt 3-5 times with same input
- Evaluate outputs on criteria (quality, consistency, usefulness)
- Track which variation performs best

### Iterative Improvement

Guide users through multiple rounds:

**Round 1**: Initial rewrite (address major weaknesses)
**Round 2**: Refine based on feedback (what worked, what didn't)
**Round 3**: Polish (fine-tune for specific use case)

Each round should:
- Show what changed
- Explain the reasoning
- Ask for specific feedback

### Context Injection

When prompts lack context, guide users to add it:

**Ask these questions**:
1. Who is the audience?
2. What is the goal/purpose?
3. What constraints exist (length, tone, format)?
4. What background is assumed?
5. What should the output look like?

**Then incorporate answers into the rewrite.**

---

## When to Use This Skill

Trigger when users say:
- "Rewrite this prompt"
- "Make this prompt better"
- "Improve my prompt"
- "Why isn't this prompt working?"
- "Help me write a better prompt for..."
- "Generate variations of this prompt"
- "A/B test this prompt"

---

## Resources

### scripts/
No scripts required for this skill - all analysis and rewriting is done by Claude directly.

### references/
No references required - prompt engineering techniques are documented inline.

### assets/
No assets required - this skill generates text output only.
