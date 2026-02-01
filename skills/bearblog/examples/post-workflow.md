# Bear Blog Post Workflow

Step-by-step workflow for creating a post using Clawdbot's browser tool.

## Prerequisites

1. Browser tool enabled in config
2. Logged into Bear Blog (session cookies persist)

## Workflow

### 1. Check Login Status

```
browser action:navigate url:https://bearblog.dev/dashboard/
browser action:snapshot
```

If not logged in, you'll see the login page.

### 2. Login (if needed)

```
browser action:navigate url:https://bearblog.dev/accounts/login/
browser action:type selector:"input[name='login']" text:"your@email.com"
browser action:type selector:"input[name='password']" text:"yourpassword"
browser action:click selector:"button[type='submit']"
```

### 3. Navigate to New Post

```
browser action:navigate url:https://<subdomain>.bearblog.dev/dashboard/post/
browser action:snapshot
```

### 4. Fill Header Content

The header textarea has id `header_content`:

```
browser action:type selector:"#header_content" text:"title: My Post Title
link: my-post-slug
published_date: 2026-01-05 15:00
tags: example, test
make_discoverable: true
meta_description: A test post"
```

### 5. Fill Body Content

The body textarea has id `body_content`:

```
browser action:type selector:"#body_content" text:"# Hello World

This is my post content.

## Section 1

Some text here.

---

*Thanks for reading!*"
```

### 6. Preview (optional)

```
browser action:click selector:"#preview-button"
browser action:snapshot
```

### 7. Publish

```
browser action:click selector:"#publish-button"
browser action:snapshot
```

## Notes

- The exact selectors may vary; use `browser action:snapshot` to inspect the page
- For drafts, skip the publish step
- The session persists between browser actions
