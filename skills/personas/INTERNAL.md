# Personas Skill - Internal Documentation

**For developers, maintainers, and advanced users.**

This document explains the technical architecture, implementation details, and maintenance procedures for the Personas skill.

---

## Architecture Overview

### Design Philosophy

**Problem:** Users need specialized AI responses for different domains (coding, writing, health, etc.) without:
- Loading 31 personalities into context simultaneously (token waste)
- Manually crafting expert prompts every conversation
- Maintaining separate chat sessions for each expert type

**Solution:** On-demand persona loading system:
1. Lightweight index (`skill.json`) lists available personas
2. User activates persona by name
3. Single `.md` file loaded into context
4. Persona remains active until switched/exited
5. Create custom personas dynamically

### File Structure

```
personas/
├── README.md          # User-facing documentation (extensive guide)
├── FAQ.md             # Common questions and troubleshooting
├── SKILL.md           # Moltbot skill instructions (loaded on invocation)
├── skill.json         # Metadata, index, and feature list
├── INTERNAL.md        # This file (developer documentation)
└── data/              # Persona definitions (31 default + custom)
    ├── cami.md
    ├── chameleon-agent.md
    ├── dev.md
    ├── chef-marco.md
    ├── dr-med.md
    ├── ... (26 more defaults)
    └── [user-custom].md
```

### Data Flow

```
User request: "Use Dev persona"
       ↓
Moltbot parses intent → persona activation
       ↓
Read ~/clawd/skills/personas/data/dev.md
       ↓
Load persona prompt into context
       ↓
AI adopts Dev personality, expertise, style
       ↓
User continues conversation in Dev mode
       ↓
User request: "Switch to Chef Marco"
       ↓
Read ~/clawd/skills/personas/data/chef-marco.md
       ↓
Replace Dev context with Chef Marco context
       ↓
AI now responds as Chef Marco
```

---

## Technical Implementation

### Persona File Format

Each persona `.md` file follows this structure:

```markdown
# [Name] [Emoji]

[Brief intro: 2-3 sentences describing who this persona is]

## EXPERTISE:
- [Domain 1]
- [Domain 2]
- [Domain 3]
- [Domain 4]

## PERSONALITY:
- [Trait 1]
- [Trait 2]
- [Trait 3]

## PHILOSOPHY:
- [Principle 1]
- [Principle 2]
- [Principle 3]

## HOW I HELP:
- [Method 1]
- [Method 2]
- [Method 3]

## COMMUNICATION STYLE:
- [Style description]
- [Format preferences]
- [Tone guidelines]

## [OPTIONAL SECTIONS]:
- SPECIAL FEATURES
- IMPORTANT BOUNDARIES
- WHEN TO USE
- EXAMPLES
```

**Why this structure?**
- **Consistent parsing** - Moltbot can extract sections reliably
- **LLM-friendly** - Clear headers guide model behavior
- **Human-readable** - Easy to edit and understand
- **Extensible** - Add custom sections as needed

### skill.json Schema

```json
{
  "name": "Personas",
  "emoji": "🎭",
  "description": "Transform into 31 specialized AI personalities...",
  "category": "ai-experience",
  "author": "Chameleon AI / Moltbot",
  "version": "1.0.0",
  "tags": ["personalities", "modes", "expertise", ...],
  "features": [
    "31 pre-built expert personas",
    "Create custom personas on demand",
    ...
  ],
  "personas": {
    "core": ["cami", "chameleon-agent", ...],
    "creative": ["luna", "mythos"],
    "curator": ["vibe"],
    "learning": ["herr-mueller", "scholar", "lingua"],
    "lifestyle": ["chef-marco", "fit", ...],
    "professional": ["social-pro", "cyberguard", ...],
    "philosophy": ["coach-thompson"],
    "custom": []  // User-created personas added here
  }
}
```

**Fields:**
- `personas` - Categorized index of all available personas
- `features` - Used for ClawdHub listing
- `tags` - Search/discovery on ClawdHub
- `version` - Semantic versioning for updates

### Activation Logic

**User triggers:**
- `"Use [persona]"`
- `"Switch to [persona]"`
- `"Activate [persona]"`
- `"I want [persona] mode"`

**Moltbot behavior:**
1. Parse persona name from user input
2. Normalize: lowercase, replace spaces with hyphens
3. Check if file exists: `data/{persona}.md`
4. If exists: read file, inject into context
5. If not exists: suggest similar names or list available

**Exit triggers:**
- `"Exit persona mode"`
- `"Back to normal"`
- `"Stop persona"`
- `"Deactivate"`

**Switching:**
- Direct switch: `"Switch to X"` replaces current persona
- No need to exit first - seamless transition

---

## Persona Creation Workflow

### Guided Creation (Conversational)

When user says: `"Create a new persona called Game Master"`

**Step 1: Confirmation**
```
"Great! Let's create a Game Master persona. 🎲
I'll guide you through 5 sections. Ready? (yes/no)"
```

**Step 2: Name & Emoji**
```
"First, confirm the name and choose an emoji.
Name: Game Master
Suggested emoji: 🎲
Want to use this emoji or pick another?"
```

**Step 3: Expertise**
```
"What are the core expertise areas?
Examples for Game Master:
- D&D 5e rules mastery
- Improvised storytelling
- Character voice acting
- Combat balancing
- World-building

List 3-5 expertise areas:"
```

**Step 4: Personality**
```
"How should this persona communicate?
Examples for Game Master:
- Dramatic and immersive
- Patient with new players
- Encourages creative solutions
- Builds tension through description

List 3-5 personality traits:"
```

**Step 5: Philosophy**
```
"What principles guide this persona?
Examples for Game Master:
- Rule of cool over strict rules
- 'Yes, and...' improv mindset
- Player agency matters most
- Story emerges from play

List 3-5 core beliefs:"
```

**Step 6: Communication Style**
```
"Describe the communication style:
- Tone: [Dramatic? Casual? Formal?]
- Length: [Concise? Detailed? Varies?]
- Format: [Narrative? Bullet points? Dialogue?]

Your input:"
```

**Step 7: Save**
```
"Perfect! Here's your Game Master persona:

# Game Master 🎲

[Generated prompt based on inputs]

## EXPERTISE:
- D&D 5e rules mastery
- Improvised storytelling
...

Save this persona? (yes/no)"
```

**Step 8: Activation**
```
"✅ Saved to data/game-master.md

Want to activate it now? (yes/no)"
```

### Manual Creation (File-Based)

**For developers or advanced users who prefer editing files directly:**

1. **Create file:**
   ```bash
   touch ~/clawd/skills/personas/data/your-persona.md
   ```

2. **Follow template** (see "Persona File Format" above)

3. **Update index:**
   ```json
   // In skill.json, add to appropriate category or "custom"
   "custom": ["your-persona"]
   ```

4. **Test:**
   ```
   "Use your-persona"
   ```

5. **Iterate:**
   - Edit file based on behavior
   - No restart needed - changes apply on next activation

---

## Maintenance Procedures

### Adding New Default Personas

**When to add:**
- Common use case not covered by existing 31
- Community requests or contributions
- Emerging domains (e.g., "AI Prompt Engineer", "Web3 Advisor")

**Process:**
1. Create `data/new-persona.md` following template
2. Test thoroughly in various scenarios
3. Add to appropriate category in `skill.json`
4. Update README.md persona table
5. Add FAQ entry if needed
6. Bump `version` in `skill.json` (minor version: x.Y.z)
7. Publish update to ClawdHub

### Updating Existing Personas

**Minor updates** (typos, clarity, small improvements):
1. Edit `data/{persona}.md`
2. Test changes: `"Use {persona}"`
3. Commit changes
4. Bump `version` patch (x.y.Z)

**Major updates** (personality changes, new sections):
1. Consider backward compatibility
2. Test extensively
3. Update FAQ if behavior changes
4. Bump `version` minor (x.Y.z)
5. Document changes in CHANGELOG

### Removing Personas

**When to remove:**
- Outdated/obsolete (e.g., specific to old tech)
- Redundant with better alternatives
- Legal/ethical issues

**Process:**
1. Remove `data/{persona}.md`
2. Remove from `skill.json` personas index
3. Update README.md
4. Add deprecation notice in FAQ
5. Bump `version` major (X.y.z) if breaking change

### Quality Assurance

**Testing checklist for new/updated personas:**
- [ ] File follows template structure
- [ ] Headers are consistent (## EXPERTISE, ## PERSONALITY, etc.)
- [ ] No personal information or copyrighted content
- [ ] Ethical boundaries clearly defined (especially medical/legal/financial)
- [ ] Communication style distinct from similar personas
- [ ] Emoji renders correctly
- [ ] Filename matches persona name (lowercase, hyphenated)
- [ ] Added to skill.json index
- [ ] Test activation: `"Use [persona]"`
- [ ] Test typical use cases (3-5 example conversations)
- [ ] Test edge cases (refusals, unknowns, off-topic)
- [ ] Test switching to/from other personas
- [ ] README updated if default persona

---

## Performance Optimization

### Token Usage

**Current implementation:**
- Index (`skill.json`): ~1KB = ~250 tokens
- Average persona file: ~3KB = ~750 tokens
- Overhead per activation: ~750 tokens (one-time)

**Optimization strategies:**
- ✅ **Lazy loading** - Only load requested persona
- ✅ **No embedding** - Don't include all 31 in context
- ⚠️ **Compression** - Could minify prompts, but reduces readability
- ⚠️ **Caching** - Moltbot could cache frequently-used personas

**Recommendation:** Current approach is optimal. Don't over-optimize.

### Response Time

**Activation latency:**
- Read file: ~10-50ms (local SSD)
- Parse markdown: ~5-10ms
- Inject into context: ~20-50ms
- **Total: ~35-110ms** (negligible)

**No optimization needed** - human-imperceptible delay.

### Storage

**Disk usage:**
- 31 default personas: ~95KB
- Average custom persona: ~3KB
- skill.json + docs: ~30KB
- **Total default: ~125KB**

At 100 custom personas: ~425KB total (still tiny).

**No storage concerns.**

---

## Security & Safety

### Prompt Injection Risks

**Threat:** Malicious persona file could inject harmful instructions.

**Mitigations:**
- Personas are local files (user controls data/)
- No remote persona loading
- File permissions: user-writable only
- Moltbot sandboxing prevents system-level harm

**Low risk** - user shoots own foot if editing files maliciously.

### Sensitive Information

**Personas should NOT:**
- Contain API keys, passwords, or secrets
- Reference specific user data (names, addresses, etc.)
- Include copyrighted content verbatim

**Review process:**
- Check files before publishing to ClawdHub
- Sanitize any contributed personas
- FAQ explicitly warns against secrets in personas

### Ethical Boundaries

**Medical/Legal/Financial personas:**
- Clearly state "NOT professional advice"
- Include disclaimers in persona files
- FAQ reinforces limitations
- Personas should refuse to diagnose, prescribe, or advise on serious matters

**Example (Dr. Med):**
```markdown
## IMPORTANT BOUNDARIES:
- I am NOT medical advice
- No diagnoses or treatment recommendations
- Emergency: call 112 immediately
- Always consult real doctors for health decisions
```

**Testing:** Verify boundary enforcement for sensitive domains.

---

## Extension Ideas

### Future Enhancements

**v1.1:**
- [ ] Persona stats tracking (activation count, avg session time)
- [ ] Persona recommendations based on user query
- [ ] Quick-switch shortcuts (e.g., `@dev` in message)

**v1.2:**
- [ ] Persona blending (combine two personas: "Dev + Security")
- [ ] Context-aware auto-switching (code block → suggest Dev)
- [ ] Persona marketplace integration (browse/install community personas)

**v2.0:**
- [ ] Multi-persona conversations (simulate expert panel)
- [ ] Persona memory (persona-specific context across sessions)
- [ ] Voice-specific personas (adjust TTS for each persona)

### Community Contributions

**Accepting:**
- New default personas (via PR)
- Improved existing personas
- Translations (German, Spanish, French versions)
- Domain-specific packs (e.g., "Medical Personas Pack")

**Process:**
1. Fork skill or submit `.md` file
2. Review for quality, ethics, uniqueness
3. Test in Moltbot
4. Merge if approved
5. Credit contributor in README

**ClawdHub publication:**
- Original skill: `personas` (official, 31 defaults)
- Forks: `personas-extended`, `personas-medical`, etc.
- Users can install multiple persona skills (data/ folders merge)

---

## Debugging

### Common Issues

**Issue: Persona not activating**

**Symptoms:**
```
User: "Use Dev"
Bot: "I don't recognize that persona."
```

**Diagnosis:**
1. Check file exists: `ls ~/clawd/skills/personas/data/dev.md`
2. Check filename matches (case-sensitive filesystem): `dev.md` not `Dev.md`
3. Check skill.json includes it
4. Try exact case: `"Use dev"` (lowercase)

**Fix:**
- Rename file if case mismatch
- Add to skill.json if missing
- Verify no typos in filename

---

**Issue: Persona behaves incorrectly**

**Symptoms:**
```
User: "Use Dev"
Bot: *doesn't act like a programmer*
```

**Diagnosis:**
1. Read file: `cat ~/clawd/skills/personas/data/dev.md`
2. Check structure (headers present?)
3. Check file isn't corrupted (encoding, special chars)
4. Test with fresh activation: exit and re-enter

**Fix:**
- Validate markdown structure
- Ensure UTF-8 encoding
- Restore from backup if corrupted
- Clear Moltbot cache (if applicable)

---

**Issue: Custom persona creation fails**

**Symptoms:**
```
User: "Create persona X"
Bot: *doesn't guide through creation*
```

**Diagnosis:**
- SKILL.md includes creator instructions? (check loaded content)
- User phrasing unclear? (try exact: "Create a new persona called X")

**Fix:**
- Verify SKILL.md includes creation workflow
- Provide explicit template to user
- Manual creation fallback: edit file directly

---

### Logging & Monitoring

**Useful logs:**
- File read operations (persona activation)
- Parse errors (malformed markdown)
- User activation patterns (popular personas)

**Metrics to track:**
- Most-used personas (optimize/improve popular ones)
- Failed activations (UX issues)
- Custom persona creation rate (feature adoption)

**Implementation:**
- Moltbot may log tool calls (file reads)
- skill.json could include usage stats (if Moltbot supports)

---

## Migration & Compatibility

### Upgrading from v1.0.0

**Breaking changes:** None expected. Backward-compatible updates.

**Process:**
1. Pull latest skill updates
2. Merge custom personas (preserve data/)
3. Update skill.json (merge personas index)
4. Test existing custom personas

### Downgrading

**If v1.x has issues:**
1. Backup `data/` (preserve custom personas)
2. Checkout previous version
3. Restore `data/`
4. Note: May lose new features

### Exporting Personas

**To another Moltbot instance:**
```bash
# Copy entire skill
cp -r ~/clawd/skills/personas /path/to/other/instance/skills/

# Or just custom personas
cp ~/clawd/skills/personas/data/my-custom-*.md /path/to/other/data/
```

**To share with others:**
- GitHub repo of `.md` files
- ClawdHub publication
- Direct file sharing (Dropbox, email, etc.)

---

## Development Workflow

### Local Testing

```bash
# 1. Edit persona
vim ~/clawd/skills/personas/data/dev.md

# 2. Test in Moltbot
moltbot
> "Use Dev"
> "Write a Python function to parse JSON"

# 3. Iterate
# Edit file based on behavior
# Re-activate: "Exit persona" then "Use Dev"

# 4. Commit when satisfied
cd ~/clawd/skills/personas
git add data/dev.md
git commit -m "Improve Dev persona: Add Python focus"
```

### Publishing to ClawdHub

```bash
cd ~/clawd/skills/personas

# 1. Bump version in skill.json
vim skill.json  # e.g., 1.0.0 → 1.1.0

# 2. Update CHANGELOG (if exists)
echo "## v1.1.0 - $(date +%Y-%m-%d)\n- Added Game Master persona\n- Improved Dev persona Python expertise" >> CHANGELOG.md

# 3. Publish
clawdhub publish

# 4. Tag release
git tag v1.1.0
git push origin v1.1.0
```

### Contributing Upstream

**To Chameleon AI Chat (original personas):**
- Improvements feed back to web app
- Coordinate with Chameleon maintainers
- Keep adapted version in sync

**To Moltbot (this skill):**
- Fork/PR to skill repository
- Follow code review process
- Maintain quality standards

---

## Credits & License

**Original Personas:**
- Source: [Chameleon AI Chat](https://github.com/robbyczgw-cla/Chameleon-AI-Chat)
- Authors: Chameleon AI Community
- License: MIT

**Moltbot Adaptation:**
- Adapter: Robby (robbyczgw-cla)
- Modifications: Removed UI-specific elements, added creator workflow, optimized for CLI/tool use
- License: MIT

**31 Default Personas:**
- Adapted from Chameleon AI definitions (TypeScript → Markdown)
- Personality prompts largely preserved
- Communication styles adjusted for Moltbot context

**Skill Framework:**
- Platform: Moltbot
- Skill structure follows Moltbot conventions
- Compatible with ClawdHub publication

---

## Appendix

### Complete Persona List (Internal Reference)

**Core (5):**
1. cami - Adaptive chameleon (emotion-aware)
2. chameleon-agent - Complex task specialist
3. professor-stein - Academic expert
4. dev - Senior programmer
5. flash - Ultra-efficient responder

**Creative (2):**
6. luna - Creative brainstormer
7. mythos - Worldbuilder

**Curator (1):**
8. vibe - Taste curator

**Learning (3):**
9. herr-mueller - ELI5 teacher
10. scholar - Study partner
11. lingua - Language tutor

**Lifestyle (9):**
12. chef-marco - Italian cooking expert
13. fit - Fitness coach
14. zen - Mindfulness guide
15. globetrotter - Travel expert
16. wellbeing - Holistic health
17. diy-maker - Handyman
18. family - Parenting advisor
19. lisa-knight - Sustainability activist
20. the-panel - Multi-expert discussion

**Professional (10):**
21. social-pro - Social media strategist
22. cyberguard - Cybersecurity expert
23. dataviz - Data scientist
24. career-coach - Job search advisor
25. legal-guide - Legal orientation
26. startup-sam - Entrepreneur
27. dr-med - Medical educator
28. wordsmith - Writing partner
29. canvas - UI/UX designer
30. finny - Financial guide

**Philosophy (1):**
31. coach-thompson - Performance coach

**Custom:**
- (User-created personas listed in skill.json["personas"]["custom"])

### File Size Reference

```bash
# Check persona file sizes
cd ~/clawd/skills/personas/data
du -h *.md | sort -h

# Typical output:
# 2.4K cami.md
# 2.8K dev.md
# 3.1K chef-marco.md
# 4.2K dr-med.md (longer due to ethical boundaries)
# 5.1K chameleon-agent.md (comprehensive multi-domain)
```

**Recommended size:** 2-5KB per persona (500-1250 tokens).

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-20
**Maintainer:** Robby (robbyczgw-cla)
