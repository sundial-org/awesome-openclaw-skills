# Premium Source Authentication

## Contents
- [Overview](#overview)
- [Option 1: Keep It Simple (Recommended)](#option-1-keep-it-simple-recommended)
- [Option 2: Use Premium Sources (Advanced)](#option-2-use-premium-sources-advanced)
- [Troubleshooting](#troubleshooting)
- [Alternative: Use APIs Instead](#alternative-use-apis-instead)
- [Recommendation](#recommendation)

## Overview

WSJ and Barron's are premium financial news sources that require subscriptions. This guide explains how to authenticate and use premium sources with the finance-news skill.

**Recommendation:** For simplicity, we recommend using **free sources only** (Yahoo Finance, CNBC, MarketWatch). Premium sources add complexity and maintenance burden.

If you have subscriptions and want premium content, follow the steps below.

---

## Option 1: Keep It Simple (Recommended)

**Use free sources only.** They provide 90% of the value without authentication complexity:

- ✅ Yahoo Finance (free, reliable)
- ✅ CNBC (free, real-time news)
- ✅ MarketWatch (free, broad coverage)
- ✅ Reuters (free via Yahoo RSS)

**To disable premium sources:**
1. Edit `config/config.json` (legacy: `config/sources.json`)
2. Set `"enabled": false` for WSJ/Barron's entries
3. Done - no authentication needed

---

## Option 2: Use Premium Sources (Advanced)

### Prerequisites

- Active WSJ or Barron's subscription
- Browser with active login session (Chrome/Firefox)
- **Option B only:** Install `requests` library if needed:
  ```bash
  pip install requests
  ```

### Step 1: Export Cookies from Browser

**Chrome:**
1. Install extension: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/)
2. Navigate to wsj.com (logged in)
3. Click EditThisCookie icon → Export → Copy JSON

**Firefox:**
1. Install extension: [Cookie Quick Manager](https://addons.mozilla.org/en-US/firefox/addon/cookie-quick-manager/)
2. Navigate to wsj.com (logged in)
3. Right-click page → Inspect → Storage → Cookies
4. Copy relevant cookies (see format below)

### Step 2: Create Cookie File

Create `config/cookies.json` (this file is gitignored):

```json
{
  "feeds.a.dj.com": {
    "wsjgeo": "US",
    "djcs_session": "YOUR_SESSION_TOKEN_HERE",
    "djcs_route": "YOUR_ROUTE_HERE"
  },
  "www.barrons.com": {
    "wsjgeo": "US",
    "djcs_session": "YOUR_SESSION_TOKEN_HERE"
  }
}
```

**Important:** Cookie domain must match feed URL domain:
- WSJ feeds use `feeds.a.dj.com` (not `wsj.com`)
- Barron's feeds use `www.barrons.com`
- Check `config/config.json` for actual feed URLs

**Note:** Cookie names/values vary by site. Export from browser to get actual values.

### Step 3: Pass Cookies to fetch_news.py

**Option A: Modify fetch_news.py (not officially supported)**

Add cookie loading to `fetch_rss()` function (maintains existing signature):

```python
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

def fetch_rss(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse RSS feed with optional cookie authentication."""
    
    # Load cookies if they exist
    cookie_file = Path(__file__).parent.parent / "config" / "cookies.json"
    cookies = {}
    if cookie_file.exists():
        with open(cookie_file) as f:
            all_cookies = json.load(f)
            # Extract domain from URL (e.g., feeds.a.dj.com)
            domain = urlparse(url).netloc
            cookies = all_cookies.get(domain, {})
    
    # Fetch with cookies and User-Agent
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'})
    if cookies:
        cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        req.add_header("Cookie", cookie_header)
    
    # ... rest of function (unchanged)
```

**Note:** This is a doc-only suggestion, not officially supported by the skill.

**Option B: Use requests library instead of urllib**

Replace `urllib` with `requests` for easier cookie handling (maintains API signature):

```python
import requests

def fetch_rss(url: str, limit: int = 10, cookies_dict: dict = None) -> list[dict]:
    response = requests.get(url, cookies=cookies_dict, timeout=10)
    response.raise_for_status()
    # ... parse with feedparser
```

### Step 4: Security Considerations

**Critical: Do NOT commit cookies to git**

1. **`.gitignore` already includes cookie files:**
   - `config/cookies.json`
   - `*.cookie`
   - No action needed (already configured)

2. **Set restrictive file permissions:**
   ```bash
   chmod 600 config/cookies.json
   ```

2. **Set restrictive file permissions:**
   ```bash
   chmod 600 config/cookies.json
   ```

3. **Rotate cookies regularly:**
   - Browser session cookies expire (usually 7-30 days)
   - Re-export cookies when authentication fails

4. **Never share cookie files:**
   - Cookies grant full account access
   - Treat like passwords

---

## Troubleshooting

### "HTTP 403 Forbidden" errors

**Cause:** Cookies expired or invalid

**Fix:**
1. Log in to WSJ/Barron's in browser
2. Re-export cookies
3. Update `config/cookies.json`

### "Paywall detected" in articles

**Cause:** RSS feed doesn't require auth, but full article does

**Fix:**
- Premium sources often provide headlines/snippets in RSS (no auth needed)
- Full articles require subscription + cookie auth
- If you only need headlines → no cookies needed

### Cookies not working

**Debug checklist:**
- [ ] Correct domain in cookies.json:
  - WSJ: Use `feeds.a.dj.com` (not `wsj.com`)
  - Barron's: Use `www.barrons.com` (not `barrons.com`)
- Check `config/config.json` for actual feed URLs
- [ ] Cookie values copied completely (no truncation)
- [ ] Browser session still active (test by visiting site)
- [ ] File permissions correct (chmod 600)

---

## Alternative: Use APIs Instead

Some premium sources offer APIs:
- **WSJ API:** Not publicly available
- **Barron's API:** Part of Dow Jones API (enterprise only)
- **Bloomberg API:** Enterprise only

**Conclusion:** Cookie-based auth is the only practical option for individual users.

---

## Recommendation

**For most users:** Stick with free sources. They're reliable, no auth needed, and provide comprehensive market coverage.

**For premium subscribers:** Follow Option 2, but be prepared to maintain cookie files and handle expiration.
