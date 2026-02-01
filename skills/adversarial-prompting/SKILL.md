---
name: adversarial-prompting
description: Applies rigorous adversarial analysis to generate, critique, fix, and consolidate solutions for any problem (technical or non-technical). Use when facing complex problems requiring thorough analysis, multiple solution approaches, and validation of proposed fixes before implementation.
---

# Adversarial Prompting

This skill applies a structured adversarial methodology to problem-solving by generating multiple solutions, rigorously critiquing each for weaknesses, developing fixes, validating those fixes, and consolidating into ranked recommendations. The approach forces deep analysis of failure modes, edge cases, and unintended consequences before committing to a solution.

## When to Use This Skill

Use this skill when:
- Facing complex technical problems requiring thorough analysis (architecture decisions, debugging, performance optimization)
- Solving strategic or business problems with multiple viable approaches
- Needing to identify weaknesses in proposed solutions before implementation
- Requiring validated fixes that address root causes, not symptoms
- Working on high-stakes decisions where failure modes must be understood
- Seeking comprehensive analysis with detailed reasoning visible throughout

Do not use this skill for:
- Simple, straightforward problems with obvious solutions
- Time-sensitive decisions requiring immediate action without analysis
- Problems where exploration and iteration are more valuable than upfront analysis

## How to Use This Skill

### Primary Workflow

When invoked, apply the following 7-phase process to the user's problem:

#### Phase 1: Solution Generation
Generate 3-7 distinct solution approaches. For each solution:
- Explain the reasoning behind the approach
- Describe the core strategy
- Outline the key steps or components

#### Phase 2: Adversarial Critique
For each solution, rigorously identify critical weaknesses. Show thinking while examining:
- Edge cases and failure modes
- Security vulnerabilities or risks
- Performance bottlenecks
- Scalability limitations
- Hidden assumptions that could break
- Resource constraints (time, money, people)
- Unintended consequences
- Catastrophic failure scenarios

Be creative and thorough in identifying what could go wrong.

#### Phase 3: Fix Development
For each identified weakness:
- Propose a specific fix or mitigation strategy
- Explain why this fix addresses the root cause
- Describe how the fix integrates with the original solution

#### Phase 4: Validation Check
Review each fix to verify it actually solves the weakness:
- Confirm the fix addresses the root cause
- Check for new problems introduced by the fix
- Flag any remaining concerns or trade-offs

#### Phase 5: Consolidation
Synthesize all solutions and validated fixes into comprehensive approaches:
- Integrate complementary elements from different solutions
- Eliminate redundancies
- Show how solutions can be combined for stronger approaches
- Present the final set of viable options

#### Phase 6: Summary of Options
Present all viable options in priority order, ranked by:
- **Feasibility**: Can this actually be implemented with available resources?
- **Impact**: How well does this solve the problem?
- **Risk Level**: What could still go wrong?
- **Resource Requirements**: Cost in time, money, and effort

For each option, provide a one-paragraph summary highlighting key trade-offs.

#### Phase 7: Final Recommendation
State the top recommendation (single option or combination):
- Clear rationale for why this is the best path
- Concrete next steps for implementation
- Key success metrics to track
- Early warning signs to monitor for problems

### Output Format

Present the complete analysis in three sections:

1. **Detailed Walkthrough**: Show all phases (1-5) with full reasoning visible
2. **Summary of Options**: Ranked list of viable approaches (Phase 6)
3. **Final Recommendation**: Top choice with implementation guidance (Phase 7)

After presenting the analysis, automatically export the complete output to a markdown file using `scripts/export_analysis.py`.

## Implementation Notes

- Show reasoning throughout the process for transparency
- Be thorough in adversarial critique—surface uncomfortable truths
- Validate fixes rigorously to avoid creating new problems
- Consolidation should create stronger solutions, not just list options
- Final recommendation should be actionable with clear next steps
- Export results to markdown for future reference and sharing
