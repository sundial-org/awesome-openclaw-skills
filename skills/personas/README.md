# 🎭 Personas

### A Moltbot Skill

> Transform into 31 specialized AI personalities on demand - from Dev (coding) to Chef Marco (cooking) to Dr. Med (medical)

**Switch mid-conversation** between expert personalities, each with unique expertise and communication style. Includes guided creator for custom personas.

---

## 🚀 Quick Start

**Activate a persona:**
```
"Use Dev persona"
"Switch to Chef Marco"
"Activate Dr. Med"
```

**List available personas:**
```
"List all personas"
"Show persona categories"
```

**Create your own:**
```
"Create a new persona called Game Master"
"I want a persona for debugging"
```

**Exit persona mode:**
```
"Exit persona mode"
"Back to normal"
```

---

## 📋 Available Personas (31)

### 🦎 Core (5)
Essential personas for everyday use.

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Cami** 🦎 | Adaptive, emotion-aware assistant | General help, beginner-friendly |
| **Chameleon Agent** 🦎 | Premium AI for complex tasks | Deep analysis, multi-step projects |
| **Professor Stein** 🎓 | Academic expert | Detailed explanations, nuanced topics |
| **Dev** 💻 | Senior programmer | Coding, debugging, architecture |
| **Flash** ⚡ | Ultra-efficient responder | Quick answers, bullet points |

### 🎨 Creative (2)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Luna** 🎨 | Creative brainstormer | Idea generation, divergent thinking |
| **Mythos** 🗺️ | Worldbuilder | Fiction writing, RPG campaigns |

### 🎧 Curator (1)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Vibe** 🎧 | Taste curator | Music, shows, books recommendations |

### 📚 Learning (3)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Herr Müller** 👨‍🏫 | ELI5 teacher | Simple explanations, patience |
| **Scholar** 📚 | Study partner | Exam prep, Socratic learning |
| **Lingua** 🗣️ | Language tutor | Language practice, corrections |

### 🌟 Lifestyle (9)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Chef Marco** 👨‍🍳 | Italian cooking expert | Recipes, techniques, food culture |
| **Fit** 💪 | Fitness coach | Workouts, form checks, motivation |
| **Zen** 🧘 | Mindfulness guide | Meditation, stress relief, calm |
| **Globetrotter** ✈️ | Travel expert | Trip planning, destinations, hacks |
| **Wellbeing** 🌱 | Holistic health | Sleep, habits, self-care |
| **DIY Maker** 🔨 | Handyman | Repairs, crafts, how-to guides |
| **Family** 👨‍👩‍👧 | Parenting advisor | Kids, activities, family life |
| **Lisa Knight** 🌿 | Sustainability activist | Eco-living, climate action |
| **The Panel** 🎙️ | Four expert perspectives | Multi-angle discussion |

### 💼 Professional (10)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Social Pro** 📱 | Social media strategist | Content, growth, platform tips |
| **CyberGuard** 🔒 | Cybersecurity expert | Privacy, passwords, scam detection |
| **DataViz** 📊 | Data scientist | Analytics, charts, statistics |
| **Career Coach** 💼 | Job search advisor | Resumes, interviews, negotiation |
| **Legal Guide** ⚖️ | Legal orientation | Contracts, rights, basic law |
| **Startup Sam** 🚀 | Entrepreneur | Business ideas, fundraising, growth |
| **Dr. Med** 🩺 | Experienced doctor | Medical concepts (not advice!) |
| **Wordsmith** 📝 | Writing partner | Editing, content, storytelling |
| **Canvas** 🎨 | UI/UX designer | Design feedback, layouts, color |
| **Finny** 💰 | Financial guide | Budgeting, saving, money basics |

### 🧠 Philosophy (1)

| Persona | Purpose | Best For |
|---------|---------|----------|
| **Coach Thompson** 🏆 | Performance coach | Goals, mindset, personal growth |

---

## 🛠️ Creating Custom Personas

**Why create custom personas?**
- Niche expertise not covered by the 31 defaults
- Personalized communication style
- Specific use cases (e.g., "Code Reviewer", "Dungeon Master", "Motivator")

**How to create:**

1. **Initiate creation:**
   ```
   "Create a new persona called [name]"
   "I want a [specialty] expert persona"
   ```

2. **I'll guide you through:**
   - Name & Emoji
   - Core expertise areas
   - Personality traits
   - Communication style
   - Philosophy/principles

3. **Save & activate:**
   - Custom persona saved to `data/your-persona.md`
   - Instantly available: `"Use [your-persona]"`

**Template structure:**
```markdown
# [Name] [Emoji]

[Brief intro]

## EXPERTISE:
- [Area 1]
- [Area 2]

## PERSONALITY:
- [Trait 1]
- [Trait 2]

## PHILOSOPHY:
- [Belief 1]
- [Belief 2]

## HOW I HELP:
- [Method 1]
- [Method 2]

## COMMUNICATION STYLE:
- [Description]
```

**Example custom personas:**
- 🎲 **Game Master** - D&D dungeon master
- 🐛 **Debugger** - Bug hunting specialist
- 💪 **Motivator** - Personal hype person
- 🤔 **Skeptic** - Devil's advocate
- 🎯 **Focus Coach** - Anti-procrastination expert

---

## 💡 How It Works

**Token-efficient loading:**
- **Index** in `skill.json` shows available personas (lightweight)
- **Only the active persona** is loaded from `data/` when needed
- No massive context dump - just the one you're using

**Switching personas:**
- Change mid-conversation anytime
- Previous persona context is replaced
- Smooth transitions between expertise areas

**Memory:**
- Active persona remembers your conversation context
- Adapts to your preferences and style
- Maintains character until you switch

---

## 📖 Use Cases

### Coding Project
```
"Use Dev" → get senior dev help
"Switch to CyberGuard" → security review
"Use Chameleon Agent" → complex architecture decisions
```

### Content Creation
```
"Use Wordsmith" → write blog post
"Switch to Social Pro" → optimize for Instagram
"Use Canvas" → design featured image
```

### Learning
```
"Use Scholar" → study for exam
"Switch to Herr Müller" → simplify complex topic
"Use Professor Stein" → deep dive
```

### Business Planning
```
"Use Startup Sam" → validate idea
"Switch to Finny" → budget projections
"Use Career Coach" → pitch practice
```

---

## ⚠️ Important Disclaimers

**Medical (Dr. Med):**
- Educational only, NOT medical advice
- Always consult real doctors for health issues
- Emergency: call 112 immediately

**Legal (Legal Guide):**
- NOT legal advice or representation
- Complex cases: consult a lawyer
- Know your local laws may differ

**Financial (Finny):**
- NOT licensed financial advice
- No specific investment recommendations
- Consult professionals for major decisions

**General:**
- All personas are AI - not human experts
- Use judgment and verify important information
- Critical decisions need human professionals

---

## 🔧 Technical Details

**Skill structure:**
```
personas/
├── README.md         # This file
├── FAQ.md            # Common questions
├── SKILL.md          # Usage instructions (loaded by Moltbot)
├── skill.json        # Metadata & persona index
├── INTERNAL.md       # Developer documentation
└── data/             # Persona definitions
    ├── cami.md
    ├── dev.md
    ├── chef-marco.md
    └── ... (28 more + custom)
```

**File formats:**
- `.md` files = Markdown personality prompts
- `skill.json` = JSON metadata
- Case-insensitive persona names

**Adding personas manually:**
1. Create `data/your-persona.md` following the template
2. Add entry to `skill.json` personas object
3. Use immediately: `"Use your-persona"`

---

## 🤝 Contributing

**Improving existing personas:**
- Edit files in `data/`
- Keep structure consistent
- Test before committing

**Adding new default personas:**
- Follow template in FAQ.md
- Add to appropriate category in `skill.json`
- Update this README

**Publishing to ClawdHub:**
- `clawdhub publish` from skill directory
- Semantic versioning for updates
- Include changelog

---

## 📜 License

Based on Chameleon AI Chat personas - adapted for Moltbot.

- Original: Chameleon AI (MIT License)
- Adaptation: Moltbot (MIT License)
- Author: Robby / Chameleon AI Community

---

## 🔗 Links

- [Chameleon AI Chat](https://github.com/robbyczgw-cla/Chameleon-AI-Chat) - Original project
- [ClawdHub](https://clawdhub.com) - Skill marketplace
- [Moltbot Docs](https://moltbot.com/docs) - Framework documentation

---

**Built with 🦎 by the Chameleon community**
