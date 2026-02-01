---
name: evowebai-website-builder
description: Create a Website Designed to Bring Clients from ChatGPT, Gemini & Modern Search
homepage: https://evoweb.ai/
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":[],"env":["EVOWEB_API_KEY"]}}}
---

# EvoWeb Website Builder

Create complete websites from text descriptions using AI-powered generation.

## Overview

EvoWeb automatically generates modern, responsive websites from natural language prompts. Simply describe what you want, and the AI creates HTML, CSS, JavaScript, and content - delivering a complete, live website in ~4 minutes.

**Perfect for:** Landing pages, portfolios, online stores, blogs, business websites

**API Base URL:** `https://api.web.oto.dev/openapi/api/v1`

## Authentication

Get your API key from https://evoweb.ai/ (by clicking Login → Create Account) or register directly at https://hub.oto.dev/app/register/

**Important:** After registration, the API Key will be displayed in the Dashboard under the "API Key Settings" section.

Include this header in all requests:
```
Access-Token: your-api-key-here
```

## How It Works

The workflow is simple:

1. **Create** - Submit a text prompt describing your website
2. **Poll** - Check generation status every 15-20 seconds
3. **Get Result** - Receive live URL and editor link when ready

Typical generation time: **2-5 minutes**

## API Endpoints

### 1. Create Website

**POST** `/sites`

Creates a new website generation task from a text description.

**Request Body:**
```json
{
  "prompt": "Create a modern landing page for a coffee shop with menu section, gallery of drinks, contact form, and location map. Use warm brown tones and inviting imagery."
}
```

**Response (200 OK):**
```json
{
  "site_id": "abc123xyz",
  "status": "queued"
}
```

**Status values:**
- `queued` - Task is in queue, waiting to start
- `building` - Website is being generated

**Error Responses:**
- `401 Unauthorized` - Invalid or missing API key
- `402 Payment Required` - Insufficient credits on account

---

### 2. Check Generation Status

**GET** `/sites/{site_id}`

Check the current status of website generation.

**Example:** `GET /sites/abc123xyz`

**Response when building:**
```json
{
  "status": "building"
}
```

**Response when ready:**
```json
{
  "status": "ready",
  "url": "https://my-site.evoweb.ai",
  "editor_url": "https://editor.evoweb.ai/sites/abc123xyz"
}
```

**Response when failed:**
```json
{
  "status": "failed",
  "error": "Generation failed: Invalid prompt structure"
}
```

**Status values:**
- `queued` - Waiting in queue
- `building` - Currently generating (be patient!)
- `ready` - Complete! URLs are available
- `failed` - Generation encountered an error

**Error Responses:**
- `404 Not Found` - Site ID doesn't exist

---

### 3. Retry Failed Generation

**POST** `/sites/{site_id}/remake`

Restart generation for a failed website. Only works for sites with `failed` status.

**Example:** `POST /sites/abc123xyz/remake`

**Response (200 OK):**
```json
{
  "status": "queued",
  "editor_url": "https://editor.evoweb.ai/sites/abc123xyz"
}
```

**Error Responses:**
- `400 Bad Request` - Can only remake sites with 'failed' status
- `404 Not Found` - Site ID doesn't exist

## Instructions for AI Assistant

When a user requests a website, follow this workflow:

### Step 1: Enhance the Prompt

Convert the user's request into a detailed, structured prompt that includes:
- Purpose and type of website
- Specific sections/pages needed (Home, About, Contact, etc.)
- Features (forms, galleries, pricing tables, etc.)
- Design style (modern, minimal, elegant, professional, etc.)
- Color preferences
- Target audience

**Example transformation:**
- User: "Create a website for my yoga studio"
- Enhanced: "Create a modern landing page for a yoga studio with class schedule section, pricing table for membership tiers, instructor bios with photos, contact form for inquiries, and location with embedded map. Use calming colors like soft blues and greens with natural imagery."

### Step 2: Create the Site

Call `POST /sites` with the enhanced prompt.

Store the returned `site_id` - you'll need it for status checks.

### Step 3: Inform the User

Tell them:
- Website generation has started
- It will take approximately 4 minutes
- You'll check progress automatically

Example: "✨ Creating your website now! Generation typically takes 3-5 minutes. I'll check the status and let you know when it's ready."

### Step 4: Poll for Status

Call `GET /sites/{site_id}` to check progress:

- **Polling interval:** Every 17 seconds (between 15-20 seconds)
- **Maximum attempts:** 20 polls (total ~6 minutes)
- **Between polls:** You can inform user of progress ("Still building...")

Continue polling until:
- Status is `ready` → Proceed to Step 5
- Status is `failed` → Proceed to Step 6
- Max attempts reached → Inform user generation is taking longer than expected

### Step 5: Deliver Success

When status is `ready`:

1. **Provide URLs:**
   - `url` - The live website
   - `editor_url` - Link to customize the site

2. **Suggest improvements:**
   Offer 3 specific ways to enhance the site:
   - "Add an online booking system"
   - "Customize colors to match your brand"
   - "Add customer testimonial section"

3. **Be concise and actionable**

**Example response:**
```
🎉 Your website is ready!

🌐 View it here: https://yoga-studio-23f4.evoweb.ai
✏️ Customize it: https://editor.evoweb.ai/sites/abc123xyz

Quick improvements you might want:
1. Add online class booking system
2. Integrate your Instagram feed
3. Add a blog section for wellness tips

Would you like help with any of these?
```

### Step 6: Handle Failures

When status is `failed`:

1. **Show the error message** from the API response
2. **Offer to retry:** Ask if they want you to remake the site
3. **If they agree:** Call `POST /sites/{site_id}/remake` and restart polling

**Example response:**
```
❌ Website generation failed: [error message]

Would you like me to try again? I can restart the generation process.
```

If user agrees, call remake endpoint and resume polling from Step 4.

## Example Prompts & Use Cases

### Coffee Shop Landing Page
```
User request: "Create a website for my coffee shop"

Enhanced prompt:
"Create a modern landing page for 'Bean & Brew Cafe' with:
- Hero section featuring coffee and cozy atmosphere
- Menu section with drinks and pastries (with prices)
- About section highlighting locally sourced beans
- Hours and location with map
- Contact form for catering inquiries
- Instagram feed integration
Use warm brown and cream colors with inviting photography style"
```

### Photographer Portfolio
```
User request: "I need a portfolio site"

Enhanced prompt:
"Create a professional portfolio website for a wedding photographer with:
- Stunning hero image showcasing best work
- Project gallery organized by wedding collections
- About page with photographer bio and experience
- Services and pricing packages
- Contact form for booking inquiries
- Testimonials from happy couples
Use clean, elegant design with white space, black and white aesthetic, and large image displays"
```

### Online Store
```
User request: "Build an e-commerce site for my jewelry"

Enhanced prompt:
"Create an online store for handmade jewelry with:
- Product catalog with filtering by category (necklaces, earrings, rings, bracelets)
- Individual product pages with multiple photos and descriptions
- Shopping cart functionality
- Checkout form with shipping options
- About the artisan section
- Custom order inquiry form
Use elegant design with soft rose gold accents and luxury feel"
```

### SaaS Landing Page
```
User request: "Landing page for my app"

Enhanced prompt:
"Create a SaaS landing page for a project management tool with:
- Value proposition above the fold with app screenshot
- Feature showcase with icons (task tracking, team collaboration, reporting)
- Pricing table with 3 tiers (Free, Pro, Enterprise)
- Customer testimonials with logos
- Free trial CTA buttons throughout
- FAQ section
Use modern, professional design with blue primary color and clean interface"
```

### Restaurant Website
```
User request: "Website for our Italian restaurant"

Enhanced prompt:
"Create a restaurant website for an authentic Italian trattoria with:
- Rotating hero images of signature dishes
- Full menu with appetizers, pasta, entrees, desserts, wine list
- Online reservation system
- About section telling family story and traditions
- Location with map and parking info
- Photo gallery of dining room and dishes
- Catering services page
Use warm, inviting design with red and green accents, rustic Italian aesthetic"
```

## Best Practices

### Writing Good Prompts

✅ **Do:**
- Be specific about sections and features
- Mention design style and mood
- Include color preferences
- Specify the purpose and audience
- List key pages/sections needed

❌ **Don't:**
- Be too vague ("make a website")
- Skip important details
- Assume AI will guess preferences

### Polling Strategy

- **Interval:** 15-20 seconds (recommend 17s)
- **Maximum:** 20 attempts total
- **Typical time:** 3-5 minutes (8-15 polls)
- **Inform user:** Let them know you're checking progress

### Error Handling

- Show clear error messages
- Offer to retry automatically
- If multiple failures, suggest the user check their account at https://evoweb.ai/

### User Experience

- Set expectations (4 minute wait time)
- Provide both view and edit URLs
- Suggest concrete improvements
- Be concise in responses
- Always end with next-step options

## Technical Details

- **Protocol:** HTTPS REST API
- **Format:** JSON
- **Authentication:** Header-based API key
- **Rate limits:** Check with EvoWeb (may have per-account limits)
- **Generation time:** Typically 2-5 minutes
- **Costs:** Credits per generation (see https://evoweb.ai/ for pricing)

## Support & Resources

- **Get API Key:** https://evoweb.ai/
- **API Issues:** Contact EvoWeb support
- **Account/Billing:** Visit https://evoweb.ai/

## Notes

- Each generation consumes credits from your EvoWeb account
- Editor URL allows users to customize the generated site
- Generated sites are hosted on EvoWeb infrastructure
- Custom domains may be available (check EvoWeb documentation)
- Sites remain live as long as account is active

---

**Ready to create amazing websites with just a text description!** 🚀
