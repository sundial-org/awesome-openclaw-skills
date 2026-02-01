---
name: daily_devotion
description: Creates personalized daily devotions with verse of the day, pastoral message, structured prayer, and time-aware greetings
version: 1.1.0
author: Eric Kariuki
npm: daily-devotion-skill
repository: https://github.com/enjuguna/Molthub-Daily-Devotion
requirements:
  - Internet access for ourmanna API
  - Node.js/TypeScript runtime for helper scripts
---

# Daily Devotion Skill

This skill creates a complete, personalized daily devotion experience for the user. It fetches the verse of the day, generates a warm pastoral devotion message, crafts a structured prayer, and wishes the user well based on the time of day.

## Overview

The Daily Devotion skill provides:
1. **Verse of the Day** - Fetched from the ourmanna API
2. **Devotional Message** - A warm, pastoral reflection on the verse
3. **Structured Prayer** - A 6-part prayer following traditional Christian format
4. **Time-Aware Greeting** - Personalized farewell based on time of day

---

## Installation

Install the helper scripts from npm:

```bash
npm install daily-devotion-skill
```

Or use directly with npx:

```bash
npx daily-devotion-skill
```

**Repository:** [github.com/enjuguna/Molthub-Daily-Devotion](https://github.com/enjuguna/Molthub-Daily-Devotion)

---

## Step 1: Fetch the Verse of the Day

Call the ourmanna API to get today's verse:

```
GET https://beta.ourmanna.com/api/v1/get?format=json&order=daily
```

**Response Structure:**
```json
{
  "verse": {
    "details": {
      "text": "The verse text here...",
      "reference": "Book Chapter:Verse",
      "version": "NIV",
      "verseurl": "http://www.ourmanna.com/"
    },
    "notice": "Powered by OurManna.com"
  }
}
```

Extract and present:
- **Verse Text**: `verse.details.text`
- **Reference**: `verse.details.reference`
- **Version**: `verse.details.version`

Alternatively, run the helper script:
```bash
npx ts-node scripts/fetch_verse.ts
```

---

## Step 2: Generate the Devotional Message

Create a warm, pastoral devotion based on the verse. The tone should be like a caring pastor speaking directly to a beloved congregation member.

### Devotion Structure:

1. **Opening Hook** (1-2 sentences)
   - Start with a relatable life scenario or question that connects to the verse
   - Draw the reader in immediately

2. **Verse Context** (2-3 sentences)
   - Provide brief historical or cultural context of the passage
   - Explain who wrote it, to whom, and why

3. **Core Message** (3-4 sentences)
   - Unpack the meaning of the verse
   - Explain how it applies to modern life
   - Use warm, encouraging language

4. **Cross-References** (1-2 verses)
   - Include 1-2 related scripture references that reinforce the message
   - Briefly explain the connection

5. **Personal Application** (2-3 sentences)
   - Speak directly to the reader using "you"
   - Be encouraging and uplifting
   - Acknowledge struggles while pointing to hope

6. **Today's Challenge**
   - Provide ONE practical, actionable step the user can take today
   - Make it specific and achievable

### Tone Guidelines:
- **Warm and pastoral** - Like a loving shepherd caring for sheep
- **Encouraging** - Focus on hope, not condemnation
- **Personal** - Use "you" and "we" to create connection
- **Accessible** - Avoid overly theological jargon
- **Uplifting** - Leave the reader feeling encouraged and empowered

---

## Step 3: Gather Prayer Context

Before crafting the prayer, ask the user:

> "Is there anything specific you'd like me to include in today's prayer? (e.g., a situation at work, a family member, a personal struggle, or a thanksgiving)"

If the user provides context:
- Incorporate it naturally into Part 4 of the prayer
- Be sensitive and respectful with personal matters
- If work-related, refer to it simply as "work" or "workplace"
- If health-related, pray for healing and strength
- If relationship-related, pray for wisdom and reconciliation

If no context provided:
- Use general prayers for daily guidance and protection

---

## Step 4: Craft the Structured Prayer

Create a prayer following this 6-part structure. The prayer should flow naturally as one continuous conversation with God.

### Part 1: Praising the Lord
Begin by glorifying God's attributes. Examples:
- "Heavenly Father, we come before You in awe of Your majesty..."
- "Lord, You are holy, righteous, and full of mercy..."
- "We praise You for Your faithfulness that endures forever..."

Focus on: God's holiness, love, power, faithfulness, mercy, sovereignty

### Part 2: Thanking the Lord
Express gratitude for blessings. Include:
- Thanks for the new day
- Thanks for life and breath
- Thanks for His Word and guidance
- Thanks for salvation through Jesus
- Thanks for specific blessings (health, family, provision)

### Part 3: Forgiveness of Sins
Humbly seek forgiveness:
- Acknowledge our imperfection
- Ask for forgiveness of known and unknown sins
- Request cleansing and renewal
- Ask for strength to resist temptation
- Pray for a pure heart

### Part 4: Prayer for Loved Ones and Context
This is where user-provided prayer requests are incorporated:

**For family and loved ones:**
- Pray for protection, health, and guidance
- Pray for their spiritual growth
- Pray for unity and love in relationships

**For user's specific context:**
- If work: Pray for wisdom, favor, and integrity in the workplace
- If health: Pray for healing, strength, and peace
- If relationships: Pray for reconciliation, understanding, and love
- If finances: Pray for provision and wise stewardship
- If decisions: Pray for clarity and discernment

### Part 5: Prayer for the Verse
Connect the day's verse to the prayer:
- Ask God to write the verse on the user's heart
- Pray for understanding of its meaning
- Ask for strength to apply it throughout the day
- Request that it guides decisions and interactions

### Part 6: Closing
End with reverence and faith:
- Commit the day into God's hands
- Express trust in His plans
- Close: "In Jesus' mighty name we pray, Amen."

---

## Step 5: Time-Aware Greeting and Farewell

Based on the current time, provide an appropriate greeting and closing message.

### Time Determination:
- **Morning** (5:00 AM - 11:59 AM): "Good morning"
- **Afternoon** (12:00 PM - 4:59 PM): "Good afternoon"  
- **Evening** (5:00 PM - 8:59 PM): "Good evening"
- **Night** (9:00 PM - 4:59 AM): "Good night"

### Closing Messages:

**Morning:**
> "Have a blessed day ahead! May God's favor go before you in everything you do today. Remember, you are never alone – He walks with you every step of the way. ☀️"

**Afternoon:**
> "May the rest of your day be filled with God's peace and purpose. Keep pressing forward – you're doing great! 🌤️"

**Evening:**
> "As this day winds down, may you find rest in God's presence. Reflect on His goodness today and trust Him for tomorrow. 🌅"

**Night:**
> "Sleep well, knowing you are held in the loving arms of your Heavenly Father. Cast all your worries on Him, for He cares for you. May angels watch over you tonight. 🌙"

### Context-Aware Additions:
If the user shared specific context, add a relevant encouragement:
- **Work stress**: "Remember, your work is unto the Lord. He sees your efforts and will reward your faithfulness."
- **Health concerns**: "God is your healer. Rest in His promises and trust His timing."
- **Family matters**: "Your prayers for your family are powerful. God hears every word and is working even when you can't see it."

---

## Complete Output Format

Present the complete devotion in this order:

```markdown
# 📖 Daily Devotion - [Date]

## Today's Verse
> "[Verse Text]"
> — [Reference] ([Version])

---

## Devotional Message

[Generated devotion following the structure above]

---

## 🙏 Today's Prayer

[Complete 6-part prayer flowing as one continuous prayer]

---

## [Time-appropriate greeting]

[Closing message with encouragement]
```

---

## Error Handling

If the API is unavailable:
1. Inform the user gracefully
2. Offer to use a backup verse from memory
3. Suggest popular verses like Jeremiah 29:11, Philippians 4:13, or Psalm 23:1

---

## Notes

- Always maintain a warm, loving tone throughout
- Be sensitive to the user's emotional state
- Never be preachy or condemning
- Focus on God's love, grace, and faithfulness
- Make the experience personal and meaningful
