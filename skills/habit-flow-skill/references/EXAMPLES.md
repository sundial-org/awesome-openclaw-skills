# Conversation Flow Examples

These examples demonstrate how to interact with users and use HabitFlow capabilities effectively.

## Example 1: Creating a Habit

**User:** "I want to start meditating every morning"

**Assistant:**
1. Parse intent (habit creation)
2. Ask clarifying questions:
   - "How many minutes would you like to meditate?"
   - "What time works best for you?"
   - "Would you like a reminder?"
3. Create habit:
```bash
npx tsx scripts/manage_habit.ts create \
  --name "Morning meditation" \
  --category mindfulness \
  --frequency daily \
  --target-count 10 \
  --target-unit minutes \
  --reminder "07:00"
```
4. Sync reminder:
```bash
npx tsx scripts/sync_reminders.ts --habit-id h_xxx --add
```
5. Respond:
> "Perfect! I've set up your morning meditation habit. Target: 10 minutes daily at 7am. You'll get WhatsApp reminders. Start small if needed—even 2 minutes counts!"

## Example 2: Natural Language Logging

**User:** "I meditated today"

**Assistant:**
1. Parse:
```bash
npx tsx scripts/parse_natural_language.ts --text "I meditated today"
```
2. Check confidence (assume 0.92)
3. Log automatically:
```bash
npx tsx scripts/log_habit.ts --habit-id h_abc123 --status completed
```
4. Respond:
> "Logged! 🔥 Your meditation streak is now 8 days (excellent quality). You're at 87% completion this week. Keep it up!"

## Example 3: Struggling User

**User:** "I keep forgetting to exercise"

**Assistant:**
1. Load stats:
```bash
npx tsx scripts/get_stats.ts --habit-id h_exercise --period 14
```
2. Analyze breakdown points
3. Apply coaching technique (reduce friction):
> "I see you've completed 3 of 14 days. Let's make it easier:
>
> 1. **Reduce friction:** Lay out workout clothes the night before
> 2. **Minimum quota:** Start with just 2 push-ups. That's it. You can stop or continue.
> 3. **Habit stack:** After brushing teeth → change into workout clothes → do 2 push-ups
>
> Which of these resonates most with you?"

## Example 4: Checking Progress

**User:** "How am I doing with my habits?"

**Assistant:**
1. Get all habits stats:
```bash
npx tsx scripts/get_stats.ts --all --period 7
```
2. Calculate streaks:
```bash
npx tsx scripts/calculate_streaks.ts --all
```
3. Respond with summary:
> "Here's your weekly progress:
>
> **Meditation** - 6/7 days (86%) - 12-day streak 🔥
> **Exercise** - 4/7 days (57%) - 2-day streak
> **Reading** - 7/7 days (100%) - 21-day streak! 🎉
>
> You're doing great overall! Reading is solid. Want to work on exercise consistency?"

## Example 5: Milestone Celebration

**User:** [System trigger: user reaches 21-day streak]

**Assistant:**
1. Detect milestone (21 days)
2. Generate visualization:
```bash
npx tsx assets/canvas-dashboard.ts streak \
  --habit-id h_abc123 \
  --output ./celebration.png
```
3. Display image and celebrate:
> [Display celebration.png]
>
> 🎉 MAJOR MILESTONE! You've hit a 21-DAY STREAK on meditation!
>
> This is HUGE! Research shows it takes 21+ days to form a habit. You're officially building neural pathways that make this automatic. You're not just meditating—you ARE a meditator now. That's identity-level change!
>
> Keep this momentum going. The hardest part is behind you. 💪

## Example 6: Persona Switch

**User:** "Switch to Coach Blaze"

**Assistant:**
1. Read config:
```bash
cat ~/clawd/habit-flow-data/config.json
```
2. Update persona field to "coach-blaze"
3. Load new persona:
```bash
cat references/personas/coach-blaze.md
```
4. Respond in new persona's voice:
> 🔥 BOOM! Coach Blaze is IN THE HOUSE, champ!
>
> Let's DO THIS! I'm here to PUMP YOU UP and help you CRUSH those habits! We're gonna build UNSTOPPABLE momentum together!
>
> What habit are we DOMINATING today? Let's GOOOO! 💪🔥

## Example 7: Bulk Logging

**User:** "I walked on Monday, Wednesday, and Friday"

**Assistant:**
1. Parse natural language:
```bash
npx tsx scripts/parse_natural_language.ts --text "I walked on Monday, Wednesday, and Friday"
```
2. Extract dates: 2026-01-20, 2026-01-22, 2026-01-24
3. Bulk log:
```bash
npx tsx scripts/log_habit.ts \
  --habit-id h_walk123 \
  --dates "2026-01-20,2026-01-22,2026-01-24" \
  --status completed
```
4. Respond:
> "Logged 3 walking sessions! Your consistency pattern is strong—you're hitting every other day. Current streak: 5 days with the 1-day forgiveness system working for you. Keep it up!"

## Example 8: Adding a Reminder

**User:** "Can you remind me to journal at 9pm?"

**Assistant:**
1. Check if journal habit exists:
```bash
npx tsx scripts/view_habits.ts --active
```
2. If exists, add reminder:
```bash
npx tsx scripts/manage_habit.ts update \
  --habit-id h_journal123 \
  --reminder "21:00"
```
3. Sync to cron:
```bash
npx tsx scripts/sync_reminders.ts --habit-id h_journal123 --add
```
4. Respond:
> "Done! You'll get a reminder every day at 9pm to journal. The reminder will go to your last active chat channel (WhatsApp, etc.). You can respond with 'done', 'skipped', or 'missed' and I'll log it automatically."

## Example 9: Viewing Visualizations

**User:** "Show me my meditation heatmap"

**Assistant:**
1. Generate heatmap:
```bash
npx tsx assets/canvas-dashboard.ts heatmap \
  --habit-id h_meditation123 \
  --days 90 \
  --output /tmp/meditation-heatmap.png
```
2. Display using Read tool:
```bash
cat /tmp/meditation-heatmap.png
```
3. Provide context:
> [Display heatmap]
>
> Here's your 90-day meditation heatmap. Green = completed, yellow = partial, grey = missed.
>
> **Patterns I see:**
> - Strong weekday performance (Mon-Fri)
> - Weekends are your challenge (60% completion)
> - You're building momentum—last 30 days are greener than first 30
>
> Want to work on a weekend strategy?

## Example 10: First-Time User Welcome

**User:** "I want to track my habits"

**Assistant:**
1. Check if data directory exists
2. If not, initialize:
```bash
mkdir -p ~/clawd/habit-flow-data/logs
```
3. Create config with default timezone
4. Welcome message:
> "Welcome to HabitFlow! I'm your habit coach, here to help you build lasting habits.
>
> I can help you:
> - Track habits with natural language ("I meditated today")
> - Maintain streaks with 1-day forgiveness
> - Set up smart reminders
> - Get evidence-based coaching
>
> **Choose your coaching style:**
> - **Flex**: Professional, data-driven (default)
> - **Coach Blaze**: Energetic motivational coach 🔥
> - **Luna**: Gentle therapist 💜
> - **Ava**: Curious productivity nerd 🤓
> - **Max**: Chill buddy 😎
> - **The Monk**: Wise minimalist 🧘
>
> What habit would you like to start tracking first?"
