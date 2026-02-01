#!/bin/bash
# LinkedIn Content Ideas Generator
# Usage: ./ideas.sh [topic]

TOPIC="${1:-general}"

cat << EOF
💡 LINKEDIN CONTENT IDEAS: $TOPIC
═══════════════════════════════════════

Generate content ideas based on high-performing formats.

## Research Steps (via browser):

1. Check trending topics:
   - https://www.linkedin.com/news/
   - Extract top 5 trending stories in your industry

2. Analyze competitor content:
   - Visit top creators in your niche
   - Note their most engaged posts (sort by reactions)
   - Identify patterns in hooks, formats, topics

3. Check hashtag performance:
   - Search relevant hashtags (#${TOPIC}, #leadership, #tech, etc.)
   - Note which posts get high engagement

## High-Engagement Post Formats:

📌 **The Contrarian Take**
"Unpopular opinion: [controversial but defensible stance]"
→ Drives comments and debate

📌 **The Story Arc**
"3 years ago, I [struggle]. Today, I [success]. Here's what changed:"
→ Personal stories get 3x engagement

📌 **The List Post**
"10 [lessons/tips/tools] I wish I knew [timeframe] ago:"
→ Easy to consume, high saves

📌 **The Before/After**
"Before: [old way]. After: [new way]. The difference? [insight]"
→ Clear transformation narrative

📌 **The Question Hook**
"What's the one skill that changed your career?"
→ Drives comments

📌 **The Hot Take + Data**
"[Bold claim]. Here's the data: [stats]"
→ Credibility + controversy

## Content Calendar Template:

| Day | Format | Topic |
|-----|--------|-------|
| Mon | Story | Personal lesson |
| Wed | List | Industry tips |
| Fri | Engagement | Question/poll |

## Hashtag Strategy for $TOPIC:

Primary (high reach): #${TOPIC} #innovation #leadership
Secondary (niche): #startup #founder #growthmindset  
Branded: #YourCompanyName

Use 3-5 hashtags per post. Place at end.
EOF
