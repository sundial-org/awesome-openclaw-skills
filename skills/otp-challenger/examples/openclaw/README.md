# 🦞 OpenClaw Identity Guard Guide

This example shows how to use `otp-challenger` as a mandatory security layer in OpenClaw.

## 1. The Skill (The 'Hands')
Copy `SKILL.md` to your skills folder. This allows the bot to ask you for a code and verify it.

## 2. The Hook (The 'Filter')
Register `interceptor.sh` as a `PostGenerate` hook. 
- **What it does:** It intercepts the AI's response *before* it reaches your chat app.
- **The Trigger:** If the response looks like a password or secret, the script calls `check-status.sh`.
- **Success/Failure:** If you aren't verified, the script replaces the secret with a 'Security Block' message. 

## 3. User Advice
- **Elapsed Time:** Set an OpenClaw cron job to run `./verify.sh --expire` every 30 minutes to ensure 'Identity verified' status doesn't last forever.
- **High-Risk Commands:** In your system prompt, tell the bot: 'Never run `rm` or `sudo` without calling `check_auth` first.'