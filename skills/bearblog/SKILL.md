---
name: bearblog
description: Create and manage blog posts on Bear Blog (bearblog.dev). Supports extended Markdown, custom attributes, and browser-based publishing.
metadata: {"clawdbot":{"emoji":"🐻","homepage":"https://bearblog.dev","requires":{"config":["browser.enabled"]}}}
---

# Bear Blog Skill

Create, edit, and manage posts on [Bear Blog](https://bearblog.dev) — a minimal, fast blogging platform.

## Authentication

Bear Blog requires browser-based authentication. Log in once via the browser tool, and cookies will persist.

```
browser action:navigate url:https://bearblog.dev/accounts/login/
```

## Creating a Post

### Step 1: Navigate to the post editor

```
browser action:navigate url:https://<subdomain>.bearblog.dev/dashboard/post/
```

### Step 2: Fill the editor

Bear Blog uses a **plain text header format** — no JavaScript DOM manipulation needed!

The editor has two textareas:
- `header_content` — metadata attributes (one per line)
- `body_content` — the actual post content in Markdown

**Header format:**
```
title: Your Post Title
link: custom-slug
published_date: 2026-01-05 14:00
tags: tag1, tag2, tag3
make_discoverable: true
is_page: false
class_name: custom-css-class
meta_description: SEO description for the post
meta_image: https://example.com/image.jpg
lang: en
canonical_url: https://original-source.com/post
alias: alternative-url
```

**Body format:** Standard Markdown with extensions (see below).

The separator `___` (three underscores) is used in templates to separate header from body.

### Step 3: Publish

Click the publish button or submit the form with `publish: true`.

## Post Attributes Reference

| Attribute | Description | Example |
|-----------|-------------|---------|
| `title` | Post title (required) | `title: My Post` |
| `link` | Custom URL slug | `link: my-custom-url` |
| `published_date` | Publication date/time | `published_date: 2026-01-05 14:30` |
| `tags` | Comma-separated tags | `tags: tech, ai, coding` |
| `make_discoverable` | Show in discovery feed | `make_discoverable: true` |
| `is_page` | Static page vs blog post | `is_page: false` |
| `class_name` | Custom CSS class (slugified) | `class_name: featured` |
| `meta_description` | SEO meta description | `meta_description: A post about...` |
| `meta_image` | Open Graph image URL | `meta_image: https://...` |
| `lang` | Language code | `lang: fr` |
| `canonical_url` | Canonical URL for SEO | `canonical_url: https://...` |
| `alias` | Alternative URL path | `alias: old-url` |

## Extended Markdown

Bear Blog uses [Mistune](https://github.com/lepture/mistune) with plugins:

### Text Formatting
- `~~strikethrough~~` → ~~strikethrough~~
- `^superscript^` → superscript
- `~subscript~` → subscript
- `==highlighted==` → highlighted (mark)
- `**bold**` and `*italic*` — standard

### Footnotes
```markdown
Here's a sentence with a footnote.[^1]

[^1]: This is the footnote content.
```

### Task Lists
```markdown
- [x] Completed task
- [ ] Incomplete task
```

### Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### Code Blocks
````markdown
```python
def hello():
    print("Hello, world!")
```
````

Syntax highlighting via Pygments (specify language after ```).

### Math (LaTeX)
- Inline: `$E = mc^2$`
- Block: `$$\int_0^\infty e^{-x^2} dx$$`

### Abbreviations
```markdown
*[HTML]: Hypertext Markup Language
The HTML specification is maintained by the W3C.
```

### Admonitions
```markdown
.. note::
   This is a note admonition.

.. warning::
   This is a warning.
```

### Table of Contents
```markdown
.. toc::
```

## Dynamic Variables

Use `{{ variable }}` in your content:

### Blog Variables
- `{{ blog_title }}` — Blog title
- `{{ blog_description }}` — Blog meta description
- `{{ blog_created_date }}` — Blog creation date
- `{{ blog_last_modified }}` — Time since last modification
- `{{ blog_last_posted }}` — Time since last post
- `{{ blog_link }}` — Full blog URL
- `{{ tags }}` — Rendered tag list with links

### Post Variables (in post templates)
- `{{ post_title }}` — Current post title
- `{{ post_description }}` — Post meta description
- `{{ post_published_date }}` — Publication date
- `{{ post_last_modified }}` — Time since modification
- `{{ post_link }}` — Full post URL
- `{{ next_post }}` — Link to next post
- `{{ previous_post }}` — Link to previous post

### Post Listing
```markdown
{{ posts }}
{{ posts limit:5 }}
{{ posts tag:"tech" }}
{{ posts tag:"tech,ai" limit:10 order:asc }}
{{ posts description:True image:True content:True }}
```

Parameters:
- `tag:` — filter by tag(s), comma-separated
- `limit:` — max number of posts
- `order:` — `asc` or `desc` (default: desc)
- `description:True` — show meta descriptions
- `image:True` — show meta images
- `content:True` — show full content (only on pages)

### Email Signup (upgraded blogs only)
```markdown
{{ email-signup }}
{{ email_signup }}
```

## Links

### Standard Links
```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Title text")
```

### Open in New Tab
Prefix URL with `tab:`:
```markdown
[External link](tab:https://example.com)
```

### Heading Anchors
Headings automatically get slugified IDs:
```markdown
## My Section Title
```
Links to: `#my-section-title`

## Typography

Automatic replacements:
- `(c)` → ©
- `(C)` → ©
- `(r)` → ®
- `(R)` → ®
- `(tm)` → ™
- `(TM)` → ™
- `(p)` → ℗
- `(P)` → ℗
- `+-` → ±

## Raw HTML

HTML is supported directly in Markdown:

```html
<div class="custom-class" style="text-align: center;">
  <p>Centered content with custom styling</p>
</div>
```

**Note:** `<script>`, `<object>`, `<embed>`, `<form>` are stripped for free accounts. Iframes are whitelisted (YouTube, Vimeo, Spotify, etc.).

## Whitelisted Iframe Sources

- youtube.com, youtube-nocookie.com
- vimeo.com
- soundcloud.com
- spotify.com
- codepen.io
- google.com (docs, drive, maps)
- bandcamp.com
- apple.com (music embeds)
- archive.org
- And more...

## Dashboard URLs

Replace `<subdomain>` with your blog subdomain:

- **Blog list:** `https://bearblog.dev/dashboard/`
- **Dashboard:** `https://<subdomain>.bearblog.dev/dashboard/`
- **New post:** `https://<subdomain>.bearblog.dev/dashboard/post/`
- **Edit post:** `https://<subdomain>.bearblog.dev/dashboard/post/<uid>/`
- **Styles:** `https://<subdomain>.bearblog.dev/dashboard/styles/`
- **Navigation:** `https://<subdomain>.bearblog.dev/dashboard/nav/`
- **Analytics:** `https://<subdomain>.bearblog.dev/dashboard/analytics/`
- **Settings:** `https://<subdomain>.bearblog.dev/dashboard/settings/`

## Example: Complete Post

**Header content:**
```
title: Getting Started with AI Assistants
link: ai-assistants-intro
published_date: 2026-01-05 15:00
tags: ai, tutorial, tech
make_discoverable: true
is_page: false
meta_description: A beginner's guide to working with AI assistants
lang: en
```

**Body content:**
```markdown
AI assistants are changing how we work. Here's what you need to know.

## Why AI Assistants?

They help with:
- [x] Writing and editing
- [x] Research and analysis
- [ ] Making coffee (not yet!)

> "The best tool is the one you actually use." — Someone wise

## Getting Started

Check out [OpenAI](tab:https://openai.com) or [Anthropic](tab:https://anthropic.com) for popular options.

---

*What's your experience with AI? Let me know!*

{{ previous_post }} {{ next_post }}
```

## Tips

1. **Preview before publishing** — Use the preview button to check formatting
2. **Use templates** — Set up a post template in dashboard settings for consistent headers
3. **Schedule posts** — Set `published_date` in the future
4. **Draft mode** — Don't click publish to keep as draft
5. **Custom CSS** — Add `class_name` and style in your blog's CSS
6. **SEO** — Always set `meta_description` and `meta_image`

## Troubleshooting

- **Post not showing?** Check `publish` status and `published_date`
- **Tags not working?** Use comma separation, no quotes
- **Styling issues?** Check `class_name` is slugified (lowercase, hyphens)
- **Date format error?** Use `YYYY-MM-DD HH:MM`
