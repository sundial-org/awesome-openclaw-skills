# Personas - Frequently Asked Questions

## General

### Q: What are personas?
**A:** Personas are specialized AI personalities with unique expertise, communication styles, and approaches. Each persona is optimized for specific tasks - like having 31 different experts available on demand.

### Q: How do I activate a persona?
**A:** Just say: `"Use Dev"`, `"Switch to Chef Marco"`, or `"Activate Dr. Med"`. Case-insensitive and flexible phrasing works.

### Q: Can I switch personas mid-conversation?
**A:** Yes! Switch anytime: `"Switch to Wordsmith"` and I'll immediately adopt that personality while keeping conversation context.

### Q: How do I go back to normal?
**A:** Say: `"Exit persona mode"`, `"Back to normal"`, or `"Stop persona"`.

### Q: Which persona should I use?
**A:** Depends on your task:
- **Coding** → Dev, Chameleon Agent
- **Writing** → Wordsmith, Luna
- **Learning** → Scholar, Herr Müller
- **Quick answers** → Flash
- **Creative brainstorming** → Luna, Mythos
- **Business** → Startup Sam, Career Coach
- **Not sure?** → Cami (adaptive default)

---

## Technical

### Q: Do you load all 31 personas at once?
**A:** No! Only the active persona is loaded from `data/` when you request it. This saves context tokens and keeps responses fast.

### Q: What's in the `data/` folder?
**A:** 31 `.md` files, each containing one persona's personality prompt, expertise areas, communication style, and philosophy.

### Q: Can I edit existing personas?
**A:** Yes! Edit any file in `data/` to customize behavior. Changes apply immediately on next activation.

### Q: File size limits?
**A:** Each persona file is ~2-5KB. Keep prompts focused and under 10KB for optimal performance.

### Q: Does persona mode remember context?
**A:** Yes! The active persona remembers your conversation. Switching personas preserves your discussion topic but changes the expert voice.

---

## Creating Custom Personas

### Q: How do I create a custom persona?
**A:** Say: `"Create a new persona called [name]"` and I'll guide you through:
1. Name & Emoji
2. Expertise areas
3. Personality traits
4. Communication style
5. Philosophy

The result is saved to `data/your-name.md` and ready to use.

### Q: What makes a good custom persona?
**A:**
- **Specific expertise** - "Debugger" not "General programmer"
- **Clear personality** - How do they communicate? Formal? Casual? Technical?
- **Defined philosophy** - What principles guide them?
- **Use cases** - When should someone use this persona?

### Q: Template for manual creation?
**A:** Create `data/your-persona.md`:

```markdown
# [Name] [Emoji]

[Brief intro describing this persona - 2-3 sentences]

## EXPERTISE:
- [Specific skill/domain 1]
- [Specific skill/domain 2]
- [Specific skill/domain 3]
- [Specific skill/domain 4]

## PERSONALITY:
- [Trait 1: e.g., "Patient and encouraging"]
- [Trait 2: e.g., "Dry humor"]
- [Trait 3: e.g., "Detail-oriented"]
- [Trait 4: e.g., "Pragmatic over theoretical"]

## PHILOSOPHY:
- [Core belief 1]
- [Core belief 2]
- [Core belief 3]
- [Core belief 4]

## HOW I HELP:
- [Approach 1]
- [Approach 2]
- [Approach 3]

## COMMUNICATION STYLE:
- [Tone description]
- [Format preferences: bullet points, narratives, etc.]
- [Language level: technical jargon OK? ELI5?]
- [Length: concise or detailed?]

## SPECIAL FEATURES (optional):
- [Unique capability or approach]
- [Signature phrases or methods]

## IMPORTANT BOUNDARIES (optional):
- [What this persona won't/can't do]
- [When to recommend switching to another persona]
```

Then add to `skill.json`:
```json
"custom": ["your-persona"]
```

### Q: Can I share custom personas?
**A:** Yes! Share the `.md` file or publish a modified version of this skill to ClawdHub with your custom additions.

### Q: Examples of good custom personas?
**A:**
- 🎲 **Game Master** - D&D campaigns, storytelling, improvisation
- 🐛 **Debugger** - Bug hunting, root cause analysis, systematic testing
- 🎯 **Focus Coach** - Pomodoro, time-blocking, anti-procrastination
- 🤔 **Skeptic** - Devil's advocate, challenge assumptions, critical thinking
- 📸 **Photo Critic** - Composition, lighting, editing feedback
- 🎬 **Script Doctor** - Screenplay feedback, dialogue polish
- 🧪 **Lab Partner** - Science experiments, hypothesis design
- 🎸 **Music Theory Tutor** - Scales, chords, composition

---

## Behavior & Expectations

### Q: Will personas always stay in character?
**A:** Yes, until you switch or exit. The persona's communication style, expertise focus, and approach remain consistent.

### Q: Can personas access external tools (web search, code execution)?
**A:** Yes! Personas can use all Moltbot tools. Dev might run code, Globetrotter might search travel sites, etc.

### Q: Do personas have different knowledge bases?
**A:** No - same underlying knowledge. The difference is **how** they communicate and **what** they prioritize. Dev thinks like a programmer, Chef Marco thinks like a chef.

### Q: Are medical/legal/financial personas giving professional advice?
**A:** **NO.** These are educational personas only:
- **Dr. Med** - Explains medical concepts, NOT diagnosis/treatment
- **Legal Guide** - Legal orientation, NOT legal advice/representation  
- **Finny** - Financial education, NOT investment recommendations

Always consult licensed professionals for serious matters.

### Q: Can personas refuse requests?
**A:** Yes. Personas maintain boundaries:
- Dr. Med won't diagnose or prescribe
- Legal Guide won't give case-specific legal advice
- All personas refuse harmful/unethical requests

### Q: What if a persona doesn't know something?
**A:** They'll say so! Good personas admit knowledge gaps and suggest alternatives (web search, another persona, external expert).

---

## Performance

### Q: Does using personas slow down responses?
**A:** Minimal impact. Loading a persona file adds ~1-2 seconds one-time when switching. After that, no difference.

### Q: Can I use personas with smaller/faster models?
**A:** Yes! Personas work with any model (Haiku, Sonnet, Opus). Complex personas (Chameleon Agent, Dr. Med) benefit from larger models.

### Q: How many personas can I switch between in one session?
**A:** Unlimited. Switch as often as needed - each switch loads the new persona prompt.

### Q: Does persona mode use more tokens?
**A:** Slightly. Each persona prompt is ~500-2000 tokens, added to context when active. But since you only load ONE at a time, it's efficient.

---

## Customization

### Q: Can I modify default personas?
**A:** Yes! Edit files in `data/`. Example: Make Dev more concise, Chef Marco less passionate, etc.

### Q: Can I delete personas I don't use?
**A:** Yes. Delete unwanted `.md` files from `data/` and remove from `skill.json`. Won't break anything.

### Q: Can I rename personas?
**A:** Yes. Rename the `.md` file in `data/` and update `skill.json`. Example: `dev.md` → `senior-dev.md`.

### Q: Can personas speak different languages?
**A:** Yes! Most default personas are German/English mix (from Chameleon AI). You can create English-only or any-language personas.

### Q: Can I create persona variations?
**A:** Absolutely! Example:
- `dev.md` - General programming
- `dev-frontend.md` - React/UI specialist
- `dev-backend.md` - Node.js/databases specialist
- `dev-devops.md` - Docker/CI/CD specialist

---

## Troubleshooting

### Q: Persona isn't activating?
**A:** Check:
1. File exists: `ls ~/clawd/skills/personas/data/[name].md`
2. Correct name: Must match filename (without `.md`)
3. Try exact phrasing: `"Use dev"` or `"Switch to dev"`

### Q: Persona behavior is wrong?
**A:** Possible issues:
- **Outdated file** - Re-read the persona: `"Reload dev persona"`
- **Context pollution** - Exit and re-enter: `"Exit persona"` then `"Use dev"`
- **File corrupted** - Check file integrity, restore from backup

### Q: Created custom persona but can't activate it?
**A:** Ensure:
1. File saved to `data/your-name.md`
2. Follows template structure (headers matter!)
3. No special characters in filename (use hyphens: `game-master.md`)

### Q: Persona responses too long/short?
**A:** Edit the `COMMUNICATION STYLE` section in the persona's `.md` file. Add guidance like:
- "Keep responses under 3 paragraphs"
- "Use bullet points for clarity"
- "Provide detailed explanations with examples"

### Q: Two personas have overlapping expertise - which to use?
**A:** Examples:
- **Dev vs Chameleon Agent** - Dev for coding focus, Chameleon Agent for complex multi-domain problems
- **Wordsmith vs Luna** - Wordsmith for editing/structure, Luna for creative brainstorming
- **Scholar vs Herr Müller** - Scholar for study techniques, Herr Müller for simple explanations

When in doubt, ask: `"Should I use Dev or Chameleon Agent for this?"`

---

## Advanced

### Q: Can I chain personas in one request?
**A:** No direct chaining, but you can:
```
"Use Luna to brainstorm, then switch to Wordsmith to refine"
```
I'll switch personas mid-task.

### Q: Can personas collaborate?
**A:** Sort of! Use **The Panel** persona - it simulates 4 experts discussing your question from different angles.

Or manually: Get Dev's take, then switch to CyberGuard for security perspective, then Startup Sam for business angle.

### Q: Can I export/import personas?
**A:** Yes!
- **Export**: Copy `.md` files from `data/`
- **Import**: Drop `.md` files into `data/`, update `skill.json`
- Share via GitHub, ClawdHub, or direct file transfer

### Q: Can I use personas in sub-agents?
**A:** Yes! Spawn a sub-agent with a persona request:
```
"Spawn a sub-agent using Dev persona to refactor this codebase"
```

### Q: Versioning personas?
**A:** Use git in your skills directory:
```bash
cd ~/clawd/skills/personas
git init
git add .
git commit -m "Initial personas"
```
Then track changes, revert if needed.

### Q: Can I monetize custom personas?
**A:** If you create valuable custom personas, you can:
1. Publish modified skill to ClawdHub
2. Share on GitHub (MIT license)
3. Offer as part of consulting/services

Original 31 personas are MIT licensed (Chameleon AI).

---

## Best Practices

### Q: When should I NOT use a persona?
**A:** For simple, quick tasks where Cami (default adaptive) is sufficient. Don't over-optimize - personas shine for:
- Specialized expertise needed
- Specific communication style wanted
- Complex, domain-specific tasks

### Q: Can I use multiple personas in parallel sessions?
**A:** Yes! Start multiple Moltbot sessions, each with different personas. Example:
- Session 1: Dev persona (coding)
- Session 2: Wordsmith persona (blog writing)
- Session 3: Chef Marco persona (meal planning)

### Q: Should I create many custom personas or modify existing ones?
**A:** Modify existing ones if:
- Close to what you want (80%+ match)
- Small tweaks needed

Create new if:
- Unique niche expertise
- Completely different communication style
- Specific use case not covered

### Q: How often should I switch personas?
**A:** When the task changes domains. Example conversation:
```
[Cami] General chat
[Dev] "Let's code this feature" → Switch to Dev
[CyberGuard] "How do I secure this?" → Switch to CyberGuard
[Wordsmith] "Now document it" → Switch to Wordsmith
[Cami] "Thanks!" → Exit persona
```

---

## Philosophy

### Q: Why use personas vs. just asking differently?
**A:** Personas provide:
- **Consistency** - Same expert voice throughout task
- **Optimization** - Communication style tuned for domain
- **Context** - Persona "remembers" they're a chef/dev/coach
- **Efficiency** - No need to re-specify expertise each message

### Q: Aren't personas just prompt engineering?
**A:** Yes! But systematized, reusable, and shareable. Instead of crafting custom prompts every time, load pre-optimized personas instantly.

### Q: Original Chameleon AI vs Moltbot personas - differences?
**A:** 
- **Chameleon AI**: Web UI, visual elements (colors, themes), chat-focused
- **Moltbot**: CLI/Telegram, tool integration, task automation
- **This skill**: Adapted personalities for Moltbot use cases, removed UI-specific elements, added creator functionality

---

**Still have questions?** Ask in persona mode: `"Use Professor Stein"` then `"Explain personas to me"` 🎓
