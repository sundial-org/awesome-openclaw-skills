---
name: skill-evaluator
description: Evaluate Clawdbot skills for quality, reliability, and publish-readiness using a multi-framework rubric (ISO 25010, OpenSSF, Shneiderman, agent-specific heuristics). Use when asked to review, audit, evaluate, score, or assess a skill before publishing, or when checking skill quality. Runs automated structural checks and guides manual assessment across 25 criteria.
---

# Skill Evaluator

Evaluate skills across 25 criteria using a hybrid automated + manual approach.

## Quick Start

### 1. Run automated checks

```bash
python3 scripts/eval-skill.py /path/to/skill
python3 scripts/eval-skill.py /path/to/skill --json    # machine-readable
python3 scripts/eval-skill.py /path/to/skill --verbose  # show all details
```

Checks: file structure, frontmatter, description quality, script syntax, dependency audit, credential scan, env var documentation.

### 2. Manual assessment

Use the rubric at [references/rubric.md](references/rubric.md) to score 25 criteria across 8 categories (0–4 each, 100 total). Each criterion has concrete descriptions per score level.

### 3. Write the evaluation

Copy [assets/EVAL-TEMPLATE.md](assets/EVAL-TEMPLATE.md) to the skill directory as `EVAL.md`. Fill in automated results + manual scores.

## Evaluation Process

1. **Run `eval-skill.py`** — get the automated structural score
2. **Read the skill's SKILL.md** — understand what it does
3. **Read/skim the scripts** — assess code quality, error handling, testability
4. **Score each manual criterion** using [references/rubric.md](references/rubric.md) — concrete criteria per level
5. **Prioritize findings** as P0 (blocks publishing) / P1 (should fix) / P2 (nice to have)
6. **Write EVAL.md** in the skill directory with scores + findings

## Categories (8 categories, 25 criteria)

| # | Category | Source Framework | Criteria |
|---|----------|-----------------|----------|
| 1 | Functional Suitability | ISO 25010 | Completeness, Correctness, Appropriateness |
| 2 | Reliability | ISO 25010 | Fault Tolerance, Error Reporting, Recoverability |
| 3 | Performance / Context | ISO 25010 + Agent | Token Cost, Execution Efficiency |
| 4 | Usability — AI Agent | Shneiderman, Gerhardt-Powals | Learnability, Consistency, Feedback, Error Prevention |
| 5 | Usability — Human | Tognazzini, Norman | Discoverability, Forgiveness |
| 6 | Security | ISO 25010 + OpenSSF | Credentials, Input Validation, Data Safety |
| 7 | Maintainability | ISO 25010 | Modularity, Modifiability, Testability |
| 8 | Agent-Specific | Novel | Trigger Precision, Progressive Disclosure, Composability, Idempotency, Escape Hatches |

## Interpreting Scores

| Range | Verdict | Action |
|-------|---------|--------|
| 90–100 | Excellent | Publish confidently |
| 80–89 | Good | Publishable, note known issues |
| 70–79 | Acceptable | Fix P0s before publishing |
| 60–69 | Needs Work | Fix P0+P1 before publishing |
| <60 | Not Ready | Significant rework needed |

## Deeper Security Scanning

This evaluator covers security basics (credentials, input validation, data safety) but for thorough security audits of skills under development, consider [SkillLens](https://www.npmjs.com/package/skilllens) (`npx skilllens scan <path>`). It checks for exfiltration, code execution, persistence, privilege bypass, and prompt injection — complementary to the quality focus here.

## Dependencies

- Python 3.6+ (for eval-skill.py)
- PyYAML (`pip install pyyaml`) — for frontmatter parsing in automated checks
