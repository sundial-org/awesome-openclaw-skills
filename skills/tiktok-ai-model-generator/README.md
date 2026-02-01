# TikTok AI Model Video Generator

Generate AI-powered fashion models wearing your products and animate them into engaging TikTok videos in under 5 minutes.

## 🎯 What This Skill Does

This skill provides a complete, step-by-step workflow to create professional product showcase videos without hiring real models, photographers, or videographers. Perfect for:

- **E-commerce sellers** showcasing products on TikTok
- **Content creators** producing automated livestream content
- **Social media marketers** scaling video production
- **Small businesses** creating professional product videos on a budget

## 🚀 Quick Start (3 Steps)

1. **Find a reference** on Pinterest (fashion pose you like)
2. **Generate prompt** using Claude AI
3. **Create video** with Nano Banana Pro + Veo/Kling

That's it! Full video in ~5 minutes.

## 💡 Why Use This Skill?

### Traditional Approach vs AI Workflow

| Aspect | Traditional Shoot | AI Workflow |
|--------|------------------|-------------|
| Time | Days to weeks | 5 minutes |
| Cost | $500-$5,000+ | Free to $50/month |
| Models | Need to hire | AI-generated |
| Flexibility | Limited reshoots | Unlimited iterations |
| Scale | Difficult to scale | Batch generation |
| Location | Studio required | All online |

### Key Benefits

- ✅ **95% time savings** - From days to minutes
- ✅ **98% cost reduction** - From thousands to free/cheap
- ✅ **Unlimited iterations** - Test different poses instantly
- ✅ **Scalable production** - Generate 100+ videos easily
- ✅ **No scheduling** - Create anytime, anywhere
- ✅ **Professional quality** - Studio-grade results

## 📋 What You Need

### Required Tools (Free Tiers Available)

1. **Pinterest** - Find reference poses (Free)
2. **Claude AI** - Generate structured prompts (Free tier / Paid)
3. **Higgsfield (Nano Banana Pro)** - Create AI model images (Free tier / Paid)
4. **Higgsfield (Veo or Kling)** - Animate videos (Free tier / Paid)

### Product Requirements

- Product image with **white background**
- High resolution (minimum 1024x1024)
- Professional lighting
- No text or watermarks
- Clear, sharp details

## 🎬 Workflow Overview

```
┌─────────────┐
│  Pinterest  │  ← Find fashion pose reference
│  Reference  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Claude    │  ← Generate JSON prompt
│   Prompt    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Nano Banana │  ← Generate AI model
│     Pro     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Veo /     │  ← Animate to video
│   Kling     │
└─────────────┘
```

## 📚 Step-by-Step Guide

### Step 1: Pinterest Reference (1-2 minutes)

1. Go to Pinterest
2. Search for poses: "fashion model pose", "[your product] model"
3. Save 2-3 high-quality references
4. Note: Pose, angle, lighting style

**Tip:** Choose simple, natural poses for best AI results.

### Step 2: Claude Prompt (1 minute)

Ask Claude to generate JSON prompt:

```
Give me detailed JSON prompt for this Pinterest image holding [PRODUCT DESCRIPTION]:

{
  "subject": {
    "description": "[Your product details]",
    "pose": "[Pose from Pinterest]",
    "angle": "[Camera angle]",
    "lighting": "[Lighting style]"
  },
  "model": {
    "appearance": "[Model details]",
    "outfit": "[Clothing style]",
    "expression": "[Facial expression]"
  },
  "environment": {
    "background": "[Background type]",
    "location": "[Setting]",
    "atmosphere": "[Mood]"
  },
  "technical": {
    "style": "[Photography style]",
    "camera": "[Camera settings]",
    "resolution": "1024x1024"
  }
}
```

### Step 3: Nano Banana Pro (1-2 minutes)

1. Open https://higgsfield.ai
2. Upload your product image (white background)
3. Paste Claude's JSON prompt
4. Generate 2-3 options
5. Select best result

### Step 4: Veo/Kling Animation (1-2 minutes)

1. Upload Nano Banana image to Veo or Kling
2. Choose animation style (subtle recommended)
3. Enter prompt: "Gentle body sway, natural breathing motion"
4. Generate 3-5 second video
5. Export as MP4 (1080x1920 for TikTok)

## 🎨 Use Cases

### E-commerce Product Videos
- Fashion: T-shirts, dresses, hoodies
- Jewelry: Necklaces, earrings, rings
- Accessories: Phone cases, watches, bags
- Cosmetics: Lipstick, makeup, skincare

### TikTok Livestreams
- 24/7 AI model streams
- Product showcase loops
- Automated content production
- Multi-variant testing

### Social Media Marketing
- TikTok product launches
- Instagram Reels
- YouTube Shorts
- Cross-platform campaigns

## 💰 Cost Estimate

| Tool | Free Tier | Paid Plans |
|------|----------|------------|
| Pinterest | Unlimited | N/A |
| Claude AI | Limited credits | $20/month+ |
| Nano Banana Pro | Limited generations | $20-50/month |
| Veo/Kling | Limited videos | $20-50/month |

**Total per month:** Free (limited) to ~$100 (unlimited)

**Per video cost:** $0 to $2 (depending on plan)

**Comparison:** Traditional shoot = $500-$5,000

## 🛠️ Included Resources

This skill includes:

- **SKILL.md** - Complete documentation with troubleshooting
- **README.md** - This user guide
- **CHANGELOG.md** - Version history
- **scripts/generate_claude_prompt.py** - Automation script for prompts
- **references/prompt_templates.md** - Pre-built JSON templates
- **references/pinterest_tips.md** - Pinterest selection guide

## 📊 Quality Tips

### Better Results

1. **High-quality product images** - White background, good lighting
2. **Simple Pinterest references** - Natural poses, clear angles
3. **Specific JSON prompts** - Include all details
4. **Subtle animations** - Natural movements work best

### Common Mistakes to Avoid

- ❌ Complex or awkward poses
- ❌ Poor quality reference images
- ❌ Product images with busy backgrounds
- ❌ Overly complex animation prompts
- ❌ Rushing the process

## 🔧 Troubleshooting

### Issue: Product not visible in generated image
- **Solution:** Add explicit "product in foreground" to JSON prompt
- **Check:** Product image has clean white background

### Issue: AI model looks fake
- **Solution:** Increase resolution, add specific model details
- **Try:** Different random seed, adjust "style strength"

### Issue: Animation looks jerky
- **Solution:** Use "gentle", "subtle" keywords in prompt
- **Try:** Different animation tool (Veo vs Kling)

See `SKILL.md` for comprehensive troubleshooting guide.

## 🚀 Advanced Features

### Batch Production
Generate 10-20 images at once, animate top selections, schedule content calendar.

### A/B Testing
Create multiple variations, test different poses/backgrounds, optimize for engagement.

### Seasonal Campaigns
Update prompts for seasons (spring: bright, summer: outdoor, fall: warm, winter: cozy).

### 24/7 Livestreams
Generate video library, loop variations, create automated TikTok streams.

## 📖 Documentation

- **SKILL.md** - Full technical documentation
- **references/prompt_templates.md** - Ready-to-use JSON templates
- **references/pinterest_tips.md** - Pinterest selection best practices

## 🤝 Support

- Check included documentation in `references/` folder
- Use bundled scripts for automation
- Review FAQ in SKILL.md for common issues

## 📄 License

MIT License - Free for personal and commercial use.

**Version:** 1.0.0
**Last Updated:** 2025-01-30

---

Ready to create your first AI model video? Start with Step 1 above! 🎉
