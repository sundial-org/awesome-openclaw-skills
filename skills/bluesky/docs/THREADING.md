# Threading State Machine Design

## Overview

`bsky thread "Post 1" "Post 2" "Post 3"` creates a chain of posts where each reply links to the previous.

## The State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│                         IDLE                                     │
│                    (no thread active)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ thread command received
┌─────────────────────────────────────────────────────────────────┐
│                      VALIDATING                                  │
│  • Check auth (session valid?)                                   │
│  • Validate all posts (length, content)                          │
│  • Pre-flight: can we post N times without rate limit?           │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼ validation failed             ▼ validation passed
┌─────────────────────────┐     ┌─────────────────────────────────┐
│   VALIDATION_FAILED     │     │         POSTING_ROOT            │
│  • Show all errors      │     │  • Post first message           │
│  • Exit cleanly         │     │  • Store root URI + CID         │
└─────────────────────────┘     └─────────────────────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼ root failed                   ▼ root succeeded
                ┌─────────────────────────┐     ┌─────────────────────────────────┐
                │      ROOT_FAILED        │     │        POSTING_REPLIES          │
                │  • No cleanup needed    │     │  • Loop through remaining posts │
                │  • Show error           │     │  • Each reply links to previous │
                └─────────────────────────┘     │  • Track: posted[], pending[]   │
                                                └─────────────────────────────────┘
                                                              │
                                              ┌───────────────┴───────────────┐
                                              ▼ reply N failed                ▼ all succeeded
                                ┌─────────────────────────────────┐     ┌─────────────────┐
                                │        PARTIAL_FAILURE          │     │    COMPLETED    │
                                │  • posted[] has some URIs       │     │  • Show all URIs│
                                │  • pending[] has remaining text │     │  • Success!     │
                                │  • DECISION POINT (see below)   │     └─────────────────┘
                                └─────────────────────────────────┘
```

## The Hard Part: Partial Failure

When post 3 of 5 fails, we have options:

### Option A: Abort + Report (Recommended for v1.2.0)
```
Thread partially posted (2 of 5):
  ✓ https://bsky.app/profile/.../post/1
  ✓ https://bsky.app/profile/.../post/2
  ✗ Failed: "Rate limited" 
  ⏸ Skipped: "Post 4 text..."
  ⏸ Skipped: "Post 5 text..."

To continue, run:
  bsky reply <post-2-url> "Post 3 text..."
```

**Pros:** Simple, transparent, user can recover manually  
**Cons:** User has to do work

### Option B: Auto-Retry with Backoff
```
Post 3 failed (rate limited), retrying in 30s...
[=============>      ] 3/5 posts
```

**Pros:** More "magic"  
**Cons:** What if it keeps failing? User sits waiting.

### Option C: Save State + Resume Command
```bash
bsky thread --continue  # resumes from saved state
```

Saves to `~/.config/bsky/thread-state.json`:
```json
{
  "started_at": "2026-01-29T08:30:00Z",
  "root_uri": "at://did:plc:xxx/app.bsky.feed.post/yyy",
  "posted": ["uri1", "uri2"],
  "pending": ["Post 3 text", "Post 4 text", "Post 5 text"],
  "last_error": "rate_limited"
}
```

**Pros:** Robust, recoverable  
**Cons:** Complex, state management is tricky

## Recommendation

**v1.2.0:** Option A (Abort + Report)
- Simple to implement
- Clear feedback
- Manual recovery is fine for MVP

**v1.3.0:** Consider Option C if users complain about interrupted threads

## Data Structures

```python
@dataclass
class ThreadState:
    posts: list[str]           # Input texts
    root_uri: str | None       # First post URI
    root_cid: str | None       # First post CID
    posted: list[PostResult]   # Successfully posted
    pending: list[str]         # Not yet posted
    status: ThreadStatus       # IDLE, POSTING, COMPLETED, PARTIAL_FAILURE
    error: str | None          # Last error message

@dataclass  
class PostResult:
    uri: str                   # at:// URI
    cid: str                   # Content ID
    url: str                   # bsky.app URL
    text: str                  # Original text

class ThreadStatus(Enum):
    IDLE = "idle"
    VALIDATING = "validating"
    POSTING = "posting"
    COMPLETED = "completed"
    PARTIAL_FAILURE = "partial_failure"
```

## Reply Linking

Each reply needs:
```python
reply_ref = {
    "root": {
        "uri": root_post.uri,
        "cid": root_post.cid
    },
    "parent": {
        "uri": previous_post.uri,
        "cid": previous_post.cid
    }
}
```

**Important:** Both `root` and `parent` are required. Root is always the first post. Parent is the immediate previous post.

## Error Cases to Handle

| Error | Cause | Action |
|-------|-------|--------|
| `RateLimited` | Too many posts | Abort, show posted URIs |
| `InvalidToken` | Session expired | Try refresh, then abort |
| `NetworkError` | Connection failed | Abort, show posted URIs |
| `ContentFiltered` | Post rejected by moderation | Abort, show which post |
| `PostTooLong` | Over 300 chars | Fail in VALIDATING (before any posts) |

## CLI Interface

```bash
# Basic thread
bsky thread "First post" "Second post" "Third post"

# With dry-run (validate only)
bsky thread "First" "Second" "Third" --dry-run

# Output on success
Thread posted (3 posts):
  1. https://bsky.app/profile/you.bsky.social/post/abc123
  2. https://bsky.app/profile/you.bsky.social/post/def456
  3. https://bsky.app/profile/you.bsky.social/post/ghi789

# Output on partial failure
Thread partially posted (2 of 3):
  ✓ https://bsky.app/profile/you.bsky.social/post/abc123
  ✓ https://bsky.app/profile/you.bsky.social/post/def456
  ✗ Failed: Rate limited
  
Remaining text not posted:
  "Third post content here..."
```

## Testing Strategy

1. **Unit tests:** Validate ThreadState transitions
2. **Mock tests:** Simulate API responses (success, rate limit, network error)
3. **Integration tests:** Actually post a 2-post thread to test account, then delete

## Open Questions

1. **Max thread length?** Bluesky doesn't enforce, but should we cap at 10? 25?
2. **Delay between posts?** 0ms? 500ms? Configurable?
3. **Show progress?** For long threads, show `[3/10] Posting...`?
