# HTML Email Templates

Professional, ready-to-use HTML email templates for the Zoho Email skill.

## Available Templates

### 📰 newsletter.html
**Best for:** Monthly updates, company news, content roundups

**Features:**
- Modern gradient header
- Multiple article sections
- Call-to-action buttons
- Professional footer
- Social media links

**Use case:** Send monthly newsletters, product updates, or content digests to subscribers.

### 📢 announcement.html
**Best for:** Important notifications, system updates, maintenance alerts

**Features:**
- Bold banner design
- Highlight boxes for key information
- Multiple content sections
- Professional corporate style
- Clear visual hierarchy

**Use case:** Announce system maintenance, policy changes, or important company news.

### 🎉 welcome.html
**Best for:** New user onboarding, welcome emails

**Features:**
- Friendly, welcoming design
- Step-by-step getting started guide
- Emoji support
- Social media integration
- Engaging call-to-action

**Use case:** Welcome new users, guide them through setup, or introduce your service.

### 📝 simple.html
**Best for:** Quick, straightforward communications

**Features:**
- Clean, minimal design
- Easy to customize
- Professional signature
- Good typography
- Fast to load

**Use case:** General-purpose template for any email, great starting point for custom designs.

## How to Use

### CLI Usage

```bash
# Send a template
python3 scripts/zoho-email.py send-html recipient@example.com "Subject" examples/templates/newsletter.html

# Preview before sending
python3 scripts/zoho-email.py preview-html examples/templates/welcome.html
```

### Python Usage

```python
from scripts.zoho_email import ZohoEmail

# Load template
with open('examples/templates/newsletter.html', 'r') as f:
    html = f.read()

# Send email
zoho = ZohoEmail()
zoho.send_html_email(
    to="recipient@example.com",
    subject="Your Monthly Newsletter",
    html_body=html
)
```

## Customization Tips

### 1. Replace Placeholder Content
All templates contain example text. Simply edit the HTML to replace:
- Titles and headings
- Body text and descriptions
- Links and URLs
- Footer information

### 2. Change Colors
Each template uses CSS variables or direct color codes. Search for color codes like:
- `#667eea` (primary purple)
- `#764ba2` (secondary purple)
- `#f5576c` (red accent)

Replace with your brand colors.

### 3. Add Your Logo
Replace the emoji or text in the header with your logo:
```html
<img src="https://your-site.com/logo.png" alt="Logo" style="max-width: 200px;">
```

### 4. Update Links
Replace all `href="#"` with actual URLs:
```html
<a href="https://your-site.com/pricing">View Pricing</a>
```

### 5. Modify Layout
Each template uses inline CSS and modern layout techniques. Feel free to:
- Add/remove sections
- Adjust padding and margins
- Change font sizes
- Modify button styles

## Email Client Compatibility

All templates are designed with maximum compatibility:
- ✅ Gmail (Web, Mobile, App)
- ✅ Outlook (Desktop, Web, Mobile)
- ✅ Apple Mail (macOS, iOS)
- ✅ Yahoo Mail
- ✅ Proton Mail
- ✅ Other modern email clients

**Features used:**
- Inline CSS (best compatibility)
- Table-based layouts where needed
- Web-safe fonts with fallbacks
- Tested color schemes
- Mobile-responsive design

## Best Practices

### DO ✅
- Keep HTML under 100KB for best deliverability
- Use inline CSS instead of `<style>` tags when possible
- Test with multiple email clients
- Include plain text fallback (automatic with this skill)
- Use web-safe fonts (Arial, Helvetica, Georgia, etc.)
- Optimize images before including

### DON'T ❌
- Use JavaScript (not supported in emails)
- Rely solely on external stylesheets
- Use video or audio embeds
- Include forms (limited support)
- Use complex CSS animations
- Forget to test on mobile devices

## Creating Your Own Templates

Start with `simple.html` and customize:

1. **Copy the template:**
   ```bash
   cp examples/templates/simple.html examples/templates/my-template.html
   ```

2. **Edit the content:**
   - Update title and headings
   - Add your content sections
   - Customize colors and styles

3. **Test it:**
   ```bash
   python3 scripts/zoho-email.py preview-html examples/templates/my-template.html
   ```

4. **Send it:**
   ```bash
   python3 scripts/zoho-email.py send-html test@example.com "Test" examples/templates/my-template.html
   ```

## Template Structure

All templates follow this structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Title</title>
    <style>
        /* Inline styles for compatibility */
    </style>
</head>
<body>
    <!-- Email content -->
</body>
</html>
```

## Resources

- **Email on Acid:** Test rendering across clients
- **Litmus:** Professional email testing
- **Can I Email:** Check CSS support in email clients
- **HTML Email Template Generator:** Create custom templates

## Support

For questions or issues with templates:
1. Check `SKILL.md` for general documentation
2. Review `HTML_FEATURE.md` for implementation details
3. Run preview mode to debug: `preview-html <template>`
4. Check MIME structure with `--verbose` flag

---

**Templates Created:** January 29, 2026  
**Compatible With:** Zoho Email Skill v1.0+  
**License:** MIT (Free to use and customize)
