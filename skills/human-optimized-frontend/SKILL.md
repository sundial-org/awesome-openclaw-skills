---
name: human-optimized-frontend
description: >
  Generates a frontend interface that is visually pleasing and experientially sound by jointly optimizing
  aesthetics, motion graphics, and user experience (UX) using quantified evaluation.
  Use only when the user explicitly invokes this skill by name to redesign a frontend.
  Trigger keywords: use human-optimized-frontend, redesign frontend, redesign interface.
---

## Activation Criteria
Activate this skill only when the user explicitly instructs the agent to redesign a frontend and references this skill by name.

Do not activate for:
- Conceptual discussion or critique only
- Coding or implementation tasks
- Inspiration, references, or visual examples
- Partial or component-level design requests

## Execution Steps

### 1. Context Intake
- Consume all provided information about the interface.
- If context is missing, assume a neutral functional product with general-purpose usage.
- Do not assume branding, audience psychology, or business goals unless explicitly stated.

### 2. Direction Lock (Aesthetic + UX)
- Select exactly one aesthetic direction.
- Select exactly one UX interaction philosophy (e.g. clarity-first, flow-driven, exploration-led).
- All visual, motion, and interaction decisions must reinforce both.
- Do not mix stylistic or interaction paradigms.

### 3. Initial Design Generation

#### Typography
- Body text baseline: 15–18px equivalent
- Heading scale:
  - H1 = body × 2.2–2.6
  - H2 = body × 1.6–1.9
  - H3 = body × 1.3–1.5
- Line height:
  - Body: 1.45–1.6
  - Headings: 1.15–1.3
- Font rule:
  - Serif + sans-serif pairing OR single family with ≥ 4 weights
- Letter spacing:
  - Headings: -1% to -3%
  - Body: 0% to +1%
- Prohibited fonts: system defaults, Inter, Roboto, Arial.

#### Color & Theme
- Palette:
  - 1 dominant
  - 1 secondary
  - 1 accent
  - 1 neutral base
- Contrast:
  - Text ≥ 4.5:1
  - Interactive elements ≥ 3:1
- Accent usage ≤ 10% of visible area
- Only one saturated color allowed
- Gradients allowed only as background fields

#### Layout & Composition
- Single spacing base unit (8px or 10px)
- Visual weight distribution:
  - Primary: 40–55%
  - Secondary: 25–35%
  - Tertiary: ≤ 20%
- Maximum two alignment axes per view
- Symmetry allowed only with counterbalancing contrast

#### Background & Depth
- Background type:
  - Textured neutral OR
  - Low-contrast geometry OR
  - Layered planes
- Max depth layers: 3
- Foreground contrast must exceed background by ≥ 20%

#### Motion Graphics (Mandatory)
- Required motion categories:
  - Entry motion
  - Hierarchy reinforcement
  - Interaction feedback
- Timing: 180–420ms
- Easing:
  - Primary: ease-out
  - Secondary: subtle cubic or linear
- Max simultaneous moving elements per viewport: 3
- Motion must encode hierarchy, state, or spatial relation
- Prohibited: decorative loops, idle animations, novelty motion

#### UX Structure (Mandatory)
- Define a primary user goal per view.
- All visual and motion emphasis must support this goal.
- Interaction rules:
  - One primary action per screen
  - Secondary actions visually subordinate
- Navigation clarity:
  - Entry point must be obvious within 1 second
  - Next available action must be discoverable without exploration
- Cognitive load:
  - No more than 3 competing focal points per view
- Feedback:
  - All user actions must produce immediate visual or motion feedback
- Error tolerance:
  - Interfaces must be forgiving; destructive actions must be visually distinguished

### 4. Quantitative Evaluation Loop

Score each dimension from 0–10:

**Typography**
- ≥ 8: hierarchy instantly readable
- ≤ 6: scale or spacing feels inconsistent

**Color**
- ≥ 8: dominance and emphasis are unambiguous
- ≤ 6: accents compete or contrast is weak

**Layout**
- ≥ 8: eye flow resolves within 1–2 seconds
- ≤ 6: multiple regions compete equally

**Background**
- ≥ 7: depth supports hierarchy
- ≤ 5: background distracts or feels empty

**Motion**
- ≥ 8: motion improves comprehension and flow
- ≤ 6: motion distracts or delays intent

**UX**
- ≥ 8: user intent is obvious, actions feel effortless
- ≤ 6: hesitation, ambiguity, or friction introduced

**Cross-Dimensional Harmony**
- ≥ 8: visuals, motion, and UX reinforce the same hierarchy and intent
- ≤ 6: any dimension contradicts another

**Weighted Total Score**
- Typography: 20%
- Color: 20%
- Layout: 20%
- Motion: 15%
- UX: 15%
- Background: 10%
- Harmony: mandatory ≥ 8

### 5. Iteration Rules
- Adjust lowest-scoring dimension first.
- UX adjustments take priority if UX score < 8.
- Never adjust more than two dimensions per iteration.
- Maximum iterations: 5.
- If harmony score drops, revert the last change.

### 6. Final Output
Produce a single declarative frontend specification including:
- Typography system
- Color palette with roles
- Layout structure and visual weights
- Background and depth treatment
- Motion graphics definitions
- UX flow and interaction rules

No alternatives. No explanations. No theory.

## Ambiguity Handling
- Missing context defaults to neutral functional usage.
- Defaults must still satisfy aesthetic, motion, and UX thresholds.
- Never infer branding, emotional tone, or audience psychology.

## Constraints & Non-Goals
- Do not generate code, assets, or mockups.
- Do not critique existing designs unless redesign context requires it.
- Do not reference trends, competitors, or popular products.
- Do not provide multiple options.
- Do not justify decisions.

## Failure Behavior
If activation conditions are not met, output a minimal statement indicating the skill cannot be activated.

If after maximum iterations UX or harmony thresholds are not met, output a minimal statement indicating that a satisfactory frontend cannot be generated under the given constraints and terminate.
