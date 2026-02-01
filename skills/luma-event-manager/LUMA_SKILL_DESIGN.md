# Luma Event Manager Skill for Clawdbot

## 📋 Product Requirements Document (PRD)

**Version:** 2.1  
**Date:** 2026-01-29  
**Status:** Complete  
**Author:** Patti (AI Assistant) for Mario Valle Reyes

---

## 1. Overview

### 1.1 Purpose
A Clawdbot skill that uses **web scraping** to help users manage Luma events as both **host** and **attendee**, with minimal app interaction through proactive notifications and intelligent automation.

### 1.2 Why Web Scraping?
- Luma API requires **Luma Plus** (paid subscription)
- Web scraping provides free access to public event data
- User authentication via browser cookies for private data

### 1.3 Problem Statement
- Event management requires constant app switching (Luma ↔ Calendar ↔ WhatsApp)
- Geographic event discovery is manual and time-consuming
- Attendees miss updates and event details without checking the app
- Hosts lack quick access to attendance metrics without logging into Luma

### 1.4 Solution
A unified voice/text interface via Clawdbot that:
- Scrapes public Luma event data
- Uses authenticated sessions for private data (guest lists, RSVPs)
- Provides geographic event discovery
- Separates host and attendee workflows
- Syncs seamlessly with Google Calendar

---

## 2. Technical Approach: Web Scraping

### 2.1 Data Sources

| Data Type | Source | Auth Required | Status |
|-----------|--------|---------------|--------|
| Public events | lu.ma/discover, lu.ma/[event-slug] | No | ✅ |
| Event details | lu.ma/[event-slug] | No | ✅ |
| Guest lists | lu.ma/[event-slug]/guests | Yes (cookies) | ✅ |
| My RSVPs | lu.ma/home | Yes (cookies) | ✅ |
| My hosted events | lu.ma/home/manage | Yes (cookies) | ✅ |
| RSVP submission | lu.ma API | Yes (cookies) | ✅ |
| Calendar sync | gog CLI | Yes (Google) | ✅ |

### 2.2 Scraping Methods

#### Method 1: HTTP + HTML Parsing (Primary)
```typescript
const response = await fetchWithBackoff(url, options, backoffOptions);
const html = await response.text();
const $ = cheerio.load(html);
const title = selectText($, ['h1', '[data-testid="event-title"]', 'title'], 'event title');
```

#### Method 2: Next.js JSON Extraction (Fallback)
```typescript
// When HTML selectors fail, extract from __NEXT_DATA__ script
const nextData = extractJsonScript(html, '__NEXT_DATA__');
const event = findFirstObjectWithKeys(nextData, ['slug'], predicate);
```

### 2.3 Authentication

**Cookie-based auth** for private data:

1. User logs into Luma in browser
2. Export cookies via browser extension or manually
3. Store cookies in pass: `pass insert luma/cookies`
4. Skill uses cookies for authenticated requests

**Cookie format:**
```json
{
  "luma_session": "abc123...",
  "luma_user_id": "usr_xxx"
}
```

### 2.4 Rate Limiting & Resilience

- **Exponential backoff** with jitter (500ms base, 8s max)
- **Retry on:** 429, 500, 502, 503, 504
- **Rate floor:** 1 request/second minimum interval
- **Retry-After header:** Respected when present
- **Fallback selectors:** Multiple CSS selectors per field
- **Next.js fallback:** Parse `__NEXT_DATA__` when selectors fail
- **Warnings:** Log when selectors fail for debugging

---

## 3. User Personas

### 3.1 The Host
**Profile:** Organizes events (InvestorCamp, portfolio demos, industry meetups)  
**Needs:**
- Quick event creation and management
- Real-time attendance visibility
- Automated attendee communications
- Post-event analytics

### 3.2 The Attendee
**Profile:** Attends tech, VC, and startup events in Silicon Valley/LATAM  
**Needs:**
- Discover relevant events nearby
- Easy RSVP without app
- Day-of logistics (location, parking, agenda)
- Track events they've attended

---

## 4. Core Features

### 4.1 Host Mode

| Feature | Description | Status |
|---------|-------------|--------|
| **List My Events** | Show all events user is hosting | ✅ |
| **Event Details** | Get full event info | ✅ |
| **Guest List** | View RSVP'd attendees | ✅ |
| **Check-in Status** | Attendance counts | 🔜 v2.1 |

### 4.2 Attendee Mode

| Feature | Description | Status |
|---------|-------------|--------|
| **Search Events** | Search by topic/theme/keyword | ✅ |
| **Discover Events** | Search by location/date | ✅ |
| **Location Filter** | Filter by radius | ✅ |
| **My RSVP'd Events** | Events I'm attending | ✅ |
| **Event Details** | Full event info | ✅ |
| **RSVP** | yes/no/maybe/waitlist | ✅ |
| **Calendar Add** | Add to Google Calendar | ✅ |

### 4.3 Proactive Features (Future)

| Feature | Trigger | Status |
|---------|---------|--------|
| **Day-of Reminder** | Morning of event | 🔜 v2.2 |
| **New Event Alert** | Host posts new event | 🔜 v2.2 |

---

## 5. Technical Architecture

### 5.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Clawdbot Gateway                           │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ WhatsApp    │    │  HEARTBEAT  │    │   Command Parser    │ │
│  │ Interface   │    │  Scheduler  │    │                     │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│         │                  │                     │              │
│         └──────────────────┼─────────────────────┘              │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Luma Skill Module                       │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │ │
│  │  │ Host Mode   │  │ Attendee    │  │   Scraper Engine  │  │ │
│  │  │ Handler     │  │ Mode Handler│  │   (cheerio/fetch) │  │ │
│  │  └─────────────┘  └─────────────┘  └───────────────────┘  │ │
│  │                                                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │ │
│  │  │ RSVP        │  │ Calendar    │  │   Rate Limiter    │  │ │
│  │  │ Handler     │  │ Sync (gog)  │  │   + Backoff       │  │ │
│  │  └─────────────┘  └─────────────┘  └───────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         ▼                  ▼                  ▼                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │ lu.ma       │  │ Google      │  │   pass (Cookies)    │    │
│  │ (scraping)  │  │ Calendar    │  │                     │    │
│  └─────────────┘  └─────────────┘  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 File Structure

```
luma/
├── src/
│   ├── index.ts          # Main entry, command routing
│   ├── scraper.ts        # Web scraping logic
│   ├── calendar.ts       # Google Calendar sync via gog
│   ├── rsvp.ts           # RSVP submission
│   ├── utils.ts          # Backoff, parsing, geocoding
│   └── skill-types.ts    # Tool definitions
├── dist/                 # Compiled JS
├── skill.json            # Clawdbot skill manifest
├── SKILL.md              # Agent instructions
├── README.md             # User documentation
└── package.json
```

### 5.3 Data Models

#### Event Object (Scraped)
```typescript
interface LumaEvent {
  slug: string;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  timezone: string;
  location: {
    type: 'physical' | 'virtual';
    name?: string;
    address?: string;
    coordinates?: { lat: number; lng: number };
  };
  cover_image?: string;
  host_name: string;
  host_id: string;
  status: string;
  url: string;
}
```

#### RSVP Result
```typescript
interface RSVPResult {
  success: boolean;
  message: string;
}
```

#### Calendar Sync Result
```typescript
interface CalendarSyncResult {
  success: boolean;
  message: string;
  account?: string;
  calendar_id?: string;
}
```

### 5.4 Key Implementations

#### Exponential Backoff
```typescript
export async function fetchWithBackoff(
  url: string,
  options: RequestInit = {},
  backoffOptions: BackoffOptions = {}
): Promise<Response> {
  // Retries with exponential delay + jitter
  // Respects Retry-After header
  // Rate limits to 1 req/sec floor
}
```

#### Fallback Selector Pattern
```typescript
function selectText($: CheerioAPI, selectors: string[], label: string): string {
  for (const selector of selectors) {
    const text = $(selector).first().text().trim();
    if (text) return text;
  }
  console.warn(`[luma] Selector failed for ${label}`);
  return '';
}
```

#### Next.js Data Extraction
```typescript
export function extractJsonScript(html: string, scriptId: string): unknown | null {
  const regex = new RegExp(`<script[^>]*id="${scriptId}"[^>]*>([\\s\\S]*?)</script>`, 'i');
  const match = html.match(regex);
  if (!match) return null;
  return JSON.parse(match[1]);
}
```

---

## 6. Command Reference

### 6.1 Host Commands

| Command | Description | Status |
|---------|-------------|--------|
| `luma host events` | List hosted events | ✅ |
| `luma host event <slug>` | Event details | ✅ |
| `luma host guests <slug>` | Guest list | ✅ |

### 6.2 Attendee Commands

| Command | Description | Status |
|---------|-------------|--------|
| `luma search <topic>` | Search by topic/theme/keyword | ✅ |
| `luma search <topic> near <location>` | Topic + location filter | ✅ |
| `luma events near <location>` | Discover events | ✅ |
| `luma events on <date>` | Events on date | ✅ |
| `luma my events` | RSVP'd events | ✅ |
| `luma event <slug>` | Event details | ✅ |
| `luma rsvp <slug> <response>` | RSVP (yes/no/maybe/waitlist) | ✅ |
| `luma add calendar <slug>` | Add to Google Calendar | ✅ |

### 6.3 Utility Commands

| Command | Description | Status |
|---------|-------------|--------|
| `luma configure` | Set up cookies | ✅ |
| `luma status` | Check connection | ✅ |
| `luma help` | Show help | ✅ |

---

## 7. Version History & Roadmap

### 7.1 Completed

#### v1.0 — Core Scraping ✅
- [x] Discover public events (no auth)
- [x] Event details scraping
- [x] Location filtering (geocoding)
- [x] Help command

#### v1.1 — Authentication ✅
- [x] Cookie-based authentication
- [x] My RSVP'd events
- [x] My hosted events
- [x] Guest list viewing

#### v2.0 — Actions ✅
- [x] RSVP submission (yes/no/maybe/waitlist)
- [x] Calendar sync via gog CLI
- [x] Exponential backoff with jitter
- [x] Fallback selectors + Next.js parsing
- [x] Comprehensive error handling

### 7.2 Planned

#### v2.1 — Host Tools
- [ ] Check-in support for hosts
- [ ] Attendance analytics

#### v2.2 — Automation
- [ ] Event creation
- [ ] Day-of reminders
- [ ] New event alerts

---

## 8. Configuration & Setup

### 8.1 Prerequisites

```bash
# Required
npm install cheerio

# Optional: For calendar sync
# Requires gog CLI with authorized Google account
gog auth add you@example.com
```

### 8.2 Setup Commands

```bash
# 1. Store Luma cookies for authenticated features
pass insert luma/cookies
# Paste: {"luma_session": "...", "luma_user_id": "..."}

# 2. Verify
luma status
```

### 8.3 Getting Cookies

1. Log into lu.ma in Chrome
2. Open DevTools → Application → Cookies
3. Copy `luma_session` and `luma_user_id` values
4. Format as JSON and store in pass

---

## 9. Dependencies

```json
{
  "dependencies": {
    "cheerio": "^1.0.0"
  }
}
```

**System dependencies:**
- `pass` — Secure cookie storage
- `gog` — Google Calendar sync (optional)

---

## 10. Limitations

- **Scraping Changes**: Luma can change HTML structure; fallback selectors help but may still break
- **RSVP Variability**: RSVP endpoints can change; failures return actionable errors
- **Rate Limits**: Exponential backoff reduces risk, but heavy use may still trigger blocks
- **Calendar Sync**: Requires `gog` CLI and a configured Google account

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Patti | Initial draft (API-based) |
| 1.1 | 2026-01-29 | Patti | Pivoted to web scraping |
| 2.0 | 2026-01-29 | Patti | Added RSVP, calendar sync, backoff, fallback selectors |
| 2.1 | 2026-01-29 | Patti | Added topic/theme search (`luma search`) |

---

*Document created for Mario Valle Reyes*  
*Last updated: 2026-01-29*
