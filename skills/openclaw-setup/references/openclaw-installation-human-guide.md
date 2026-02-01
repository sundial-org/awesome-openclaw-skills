# OpenClaw Setup Guide: Your Personal AI Assistant

*A comprehensive guide to setting up your own 24/7 AI assistant*

---

## What is OpenClaw?

OpenClaw is your own personal AI assistant that runs 24/7 on your infrastructure. Unlike ChatGPT or other AI services that reset every conversation, OpenClaw maintains persistent memory, learns your preferences, integrates with your tools, and proactively helps you manage your life.

Think of it as having a highly capable personal assistant who:
- Never forgets important details
- Can access and control your apps and services
- Sends you proactive reminders and briefings
- Handles repetitive tasks automatically
- Gets smarter about your preferences over time
- Works across all your messaging platforms

**Key differentiator:** While other AI assistants are reactive (you ask, they respond), OpenClaw is proactive. It thinks ahead, remembers context across months of conversation, and can take actions on your behalf.

---

## What You Need

### Essential Requirements
- **AWS Account** (free tier eligible for 12 months)
- **Anthropic API Key** (Claude access, pay-per-use, ~$20/month typical usage)
- **Groq API Key** (voice transcription, free tier: 144 hours/month)
- **Telegram Account** (primary interface, free)
- **Domain Name** (optional but recommended for SSL, ~$10/year)

### Technical Requirements
- **AWS Instance**: **m7i-flex.large** (2 vCPUs, 8GB RAM, free tier eligible)
- **Storage**: 30GB gp3 EBS volume minimum
- **Operating System**: Ubuntu 22.04 LTS (recommended)

---

## Power Features

### Memory Architecture
- Persistent conversation history across sessions
- Automatic categorization of important information
- Searchable knowledge base of past interactions
- Daily notes system with automatic summary generation
- State management for ongoing projects and tasks

### Compaction Hooks
- Automatic memory consolidation before context limits
- Seamless context restoration after cleanup
- Preserved personality and tone consistency

### Heartbeat System
- Scheduled daily/weekly proactive check-ins
- Goal progress monitoring
- Automated follow-up reminders
- Smart scheduling with calendar awareness

### Cron Jobs & Automation
- Morning briefings, evening debriefs
- Custom reminders (medication, birthdays, bills, deadlines)
- Fully configurable schedules

### Google Workspace Integration
- Calendar management (create, modify, conflict resolution)
- Gmail integration (summarize, triage, suggest responses)
- Drive integration (search, organize, share)

### Browser Automation
- Web task automation (forms, data extraction, monitoring)
- Research assistance (information gathering, fact-checking)

### Sub-Agents
- Background task workers for long-running projects
- Specialized agents (email, calendar, research, creative)

### Voice Transcription
- Groq Whisper integration (free tier: 144 hours/month)
- Real-time voice message transcription
- Action item extraction from recordings

---

## Security Hardening

### SSL Certificate Setup
- Let's Encrypt automatic certificate generation
- 90-day renewal automation
- HTTPS enforcement with HSTS headers

### Port Lockdown
- Close unnecessary ports
- Restrict SSH access by IP
- fail2ban for brute force protection

### Domain Setup
- A record pointing to Elastic IP
- CNAME records for subdomains
- TXT records for verification

---

## The Result: What Your Setup Looks Like When Done

**Morning (7:00 AM):**
OpenClaw sends a personalized briefing: agenda, reminders, weather, priority tasks, calendar conflicts.

**Throughout the Day:**
Intelligent message filtering, automatic calendar optimization, proactive task reminders, research assistance.

**Evening (8:00 PM):**
Day summary with accomplishments, tomorrow's preparation, smart suggestions.

**Memory That Actually Works:**
Remembers restaurant recommendations from weeks ago, tracks your preferences over months, creates calendar events from casual conversations.

---

## Ready to Set Up?

This skill walks you through every step. Give it to any AI agent (Claude Code, OpenClaw, or any tool that can follow markdown instructions) and it will set up your personal AI assistant from scratch.

**What you get:**
- Complete OpenClaw installation on your own AWS infrastructure
- Telegram bot as your primary interface
- Persistent memory that survives across sessions
- Voice transcription (send voice notes, get text back)
- Google Workspace integration (calendar, email, drive)
- Security hardening (firewall, SSL, fail2ban)
- Personalized personality, tone, and check-in schedule
- Auto-restart on crashes (systemd service)

**Your data stays on your server. Your AI works for you. Nobody else has access.**

Community and support: [discord.com/invite/clawd](https://discord.com/invite/clawd) | [docs.clawd.bot](https://docs.clawd.bot)
