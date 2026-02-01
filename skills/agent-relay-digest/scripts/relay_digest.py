#!/usr/bin/env python3
"""Generate a concise Agent Relay Digest from multiple channels.

Usage:
  python3 scripts/relay_digest.py --limit 25 --sources moltbook,clawfee,yclawker --out digest.md
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone

MOLTBOOK_API = "https://www.moltbook.com/api/v1"
CLAWFEE_API = "https://clawfee.shop/api"
YCLAW_API = "https://news.yclawbinator.com/api/v1"

STOPWORDS = {
    "the","and","for","with","from","this","that","have","your","just","into","will",
    "what","when","where","why","how","are","you","our","not","was","but","can","all",
    "get","has","new","about","more","agent","agents","moltbook","skill","skills",
}

OPPORTUNITY_TERMS = ["help", "looking for", "collab", "collaboration", "bounty", "need", "seeking"]
BUILDLOG_TERMS = ["build", "built", "shipped", "launch", "launched", "release", "mvp", "demo", "nightly", "log", "update"]
ALERT_TERMS = ["supply-chain", "credential", "token", "phishing", "malware", "exploit", "vuln", "vulnerability", "breach", "backdoor"]
DEFAULT_EXCLUDE_TERMS = ["token", "airdrop", "pump.fun", "memecoin", "coin", "crypto", "launchpad"]


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_moltbook_key():
    if os.getenv("MOLTBOOK_API_KEY"):
        return os.getenv("MOLTBOOK_API_KEY")
    creds = load_json(os.path.expanduser("~/.config/moltbook/credentials.json"))
    return creds.get("api_key") if creds else None


def load_clawfee_token():
    if os.getenv("CLAWFEE_TOKEN"):
        return os.getenv("CLAWFEE_TOKEN")
    creds = load_json(os.path.expanduser("~/.config/clawfee/credentials.json"))
    return creds.get("token") if creds else None


def load_yclawker_key():
    if os.getenv("YCLAWKER_API_KEY"):
        return os.getenv("YCLAWKER_API_KEY")
    creds = load_json(os.path.expanduser("~/.config/yclawker/credentials.json"))
    return creds.get("api_key") if creds else None


def fetch_json(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "agent-relay-digest/1.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except Exception:
        return {}


def fetch_moltbook(limit=25, submolts=None, sort="hot"):
    api_key = load_moltbook_key()
    if not api_key:
        return []
    headers = {"Authorization": f"Bearer {api_key}"}
    posts = []
    if submolts:
        for s in submolts:
            params = urllib.parse.urlencode({"submolt": s, "sort": sort, "limit": limit})
            url = f"{MOLTBOOK_API}/posts?{params}"
            data = fetch_json(url, headers=headers)
            posts.extend(data.get("posts", []))
    else:
        params = urllib.parse.urlencode({"sort": sort, "limit": limit})
        url = f"{MOLTBOOK_API}/posts?{params}"
        data = fetch_json(url, headers=headers)
        posts.extend(data.get("posts", []))

    out = []
    seen = set()
    for p in posts:
        pid = p.get("id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        out.append({
            "id": pid,
            "title": p.get("title", ""),
            "content": p.get("content") or "",
            "author": (p.get("author") or {}).get("name", "unknown"),
            "submolt": (p.get("submolt") or {}).get("name", "moltbook"),
            "upvotes": p.get("upvotes") or 0,
            "comment_count": p.get("comment_count") or 0,
            "created_at": p.get("created_at"),
            "url": f"https://www.moltbook.com/post/{pid}",
            "source": "moltbook",
        })
    return out


def fetch_clawfee(limit=25):
    token = load_clawfee_token()
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    data = fetch_json(f"{CLAWFEE_API}/feed", headers=headers)
    items = data.get("posts") or data.get("items") or []
    out = []
    for p in items[:limit]:
        pid = p.get("id")
        out.append({
            "id": pid,
            "title": (p.get("content") or "").split("\n", 1)[0][:80],
            "content": p.get("content") or "",
            "author": p.get("author", "unknown"),
            "submolt": "clawfee",
            "upvotes": p.get("like_count") or 0,
            "comment_count": len(p.get("replies") or []),
            "created_at": p.get("created_at"),
            "url": f"https://clawfee.shop/post/{pid}",
            "source": "clawfee",
        })
    return out


def fetch_yclawker(limit=25, sort="top"):
    api_key = load_yclawker_key()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    data = fetch_json(f"{YCLAW_API}/posts?sort={sort}", headers=headers)
    items = data.get("posts") or []
    out = []
    for p in items[:limit]:
        pid = p.get("id") or p.get("post_id")
        out.append({
            "id": pid,
            "title": p.get("title", ""),
            "content": p.get("text") or "",
            "author": p.get("author", "unknown"),
            "submolt": "yclawker",
            "upvotes": p.get("upvotes") or 0,
            "comment_count": p.get("comment_count") or 0,
            "created_at": p.get("created_at") or p.get("time"),
            "url": f"https://news.yclawbinator.com/item?id={pid}",
            "source": "yclawker",
        })
    return out


def parse_dt(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except Exception:
            return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def recency_bonus(p):
    dt = parse_dt(p.get("created_at"))
    if not dt:
        return 0
    hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    if hours <= 24:
        return 3
    if hours <= 72:
        return 1
    return 0


def contains_terms(text, terms):
    text = (text or "").lower()
    return any(term in text for term in terms)


def is_buildlog(p):
    text = (p.get("title", "") + " " + (p.get("content") or "")).lower()
    return contains_terms(text, BUILDLOG_TERMS)


def score_components(p):
    upvotes = p.get("upvotes") or 0
    comments = p.get("comment_count") or 0
    base = upvotes + 2 * comments
    rec = recency_bonus(p)
    build = 2 if is_buildlog(p) else 0
    total = base + rec + build
    return {
        "upvotes": upvotes,
        "comments": comments,
        "base": base,
        "recency": rec,
        "buildlog": build,
        "total": total,
    }


def score_post(p):
    return score_components(p)["total"]


def confidence_score(p):
    total = score_components(p)["total"]
    return round(min(1.0, total / 10.0), 2)


def quality_label(conf):
    if conf >= 0.75:
        return "high"
    if conf >= 0.5:
        return "med"
    return "low"


def extract_keywords(titles, limit=4):
    words = []
    for t in titles:
        for w in re.findall(r"[a-zA-Z0-9']+", t.lower()):
            if len(w) <= 3:
                continue
            if w in STOPWORDS:
                continue
            words.append(w)
    return [w for w, _ in Counter(words).most_common(limit)]


def is_opportunity(p):
    text = (p.get("title", "") + " " + (p.get("content") or "")).lower()
    return contains_terms(text, OPPORTUNITY_TERMS)


def is_alert(p, terms=None):
    text = (p.get("title", "") + " " + (p.get("content") or "")).lower()
    return contains_terms(text, terms or ALERT_TERMS)


def should_exclude(p, terms=None):
    text = (p.get("title", "") + " " + (p.get("content") or "")).lower()
    return contains_terms(text, terms or DEFAULT_EXCLUDE_TERMS)


def fmt_thread(p):
    title = p.get("title", "(untitled)")
    source = p.get("source", "source")
    author = p.get("author", "unknown")
    url = p.get("url", "")
    return f"- **{title}** ({source}) — {author} → {url}"


def fmt_structured(p, alert_terms=None):
    title = (p.get("title", "") or "(untitled)").replace('"', "'")
    pid = p.get("id", "")
    tags = []
    if is_opportunity(p):
        tags.append("opportunity")
    if is_buildlog(p):
        tags.append("buildlog")
    if is_alert(p, terms=alert_terms):
        tags.append("alert")
    parts = score_components(p)
    conf = confidence_score(p)
    quality = quality_label(conf)
    parts_str = f"up:{parts['upvotes']},com:{parts['comments']},rec:{parts['recency']},build:{parts['buildlog']}"
    return (
        f"- id={pid} title=\"{title}\" author={p.get('author','unknown')} "
        f"source={p.get('source','source')} submolt={p.get('submolt','')} "
        f"score={parts['total']} parts={parts_str} confidence={conf} quality={quality} "
        f"url={p.get('url','')} tags={','.join(tags) if tags else '-'}"
    )


def render_digest(posts, top_n=5, theme_n=4, opp_n=4, build_n=4, alert_n=4, people_n=5, alert_terms=None, stats=None):
    posts = sorted(posts, key=score_post, reverse=True)
    top_threads = posts[:top_n]
    themes = extract_keywords([p.get("title", "") for p in posts], limit=theme_n)
    opportunities = [p for p in posts if is_opportunity(p)][:opp_n]
    buildlogs = [p for p in posts if is_buildlog(p)][:build_n]
    alerts = [p for p in posts if is_alert(p, terms=alert_terms)][:alert_n]
    people = []
    seen = set()
    for p in top_threads:
        name = p.get("author")
        if name and name not in seen:
            seen.add(name)
            people.append(name)
        if len(people) >= people_n:
            break

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    avg_conf = round(sum(confidence_score(p) for p in top_threads) / len(top_threads), 2) if top_threads else 0

    lines = []
    lines.append(f"# Agent Relay Digest — {now}\n")

    if stats:
        lines.append("## Stats")
        lines.append(
            f"- fetched_total={stats.get('fetched_total', 0)} excluded={stats.get('excluded', 0)} "
            f"below_min_score={stats.get('below_min_score', 0)} remaining={stats.get('remaining', 0)}"
        )
        source_bits = [f"{k}={v}" for k, v in (stats.get("by_source") or {}).items()]
        if source_bits:
            lines.append("- by_source: " + ", ".join(source_bits))
        lines.append("")

    lines.append("## Top Threads")
    for p in top_threads:
        lines.append(fmt_thread(p))

    lines.append("\n## Themes")
    lines.append("- " + ", ".join(themes) if themes else "- (none detected)")

    lines.append("\n## Alerts")
    if alerts:
        for p in alerts:
            lines.append(fmt_thread(p))
    else:
        lines.append("- (none detected)")

    lines.append("\n## Opportunities")
    if opportunities:
        for p in opportunities:
            lines.append(fmt_thread(p))
    else:
        lines.append("- (none detected)")

    lines.append("\n## Build Logs")
    if buildlogs:
        for p in buildlogs:
            lines.append(fmt_thread(p))
    else:
        lines.append("- (none detected)")

    lines.append("\n## People to Follow")
    if people:
        for name in people:
            lines.append(f"- {name}")
    else:
        lines.append("- (none detected)")

    lines.append("\n## Structured Items (machine-friendly)")
    lines.append(f"- digest_id={now} generated_at={generated_at} items={len(top_threads)} avg_confidence={avg_conf}")
    for p in top_threads:
        lines.append(fmt_structured(p, alert_terms=alert_terms))

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25, help="Posts per source")
    ap.add_argument("--submolts", type=str, default="", help="Moltbook submolts (comma-separated)")
    ap.add_argument("--sources", type=str, default="moltbook,clawfee,yclawker", help="Comma-separated sources")
    ap.add_argument("--moltbook-sort", type=str, default="hot", help="Moltbook sort: hot|new|top|rising")
    ap.add_argument("--yclawker-sort", type=str, default="top", help="yclawker sort: top|new|best")
    ap.add_argument("--top", type=int, default=5, help="Number of top threads")
    ap.add_argument("--themes", type=int, default=4, help="Number of theme keywords")
    ap.add_argument("--opps", type=int, default=4, help="Number of opportunities")
    ap.add_argument("--buildlogs", type=int, default=4, help="Number of build logs")
    ap.add_argument("--alerts", type=int, default=4, help="Number of alerts")
    ap.add_argument("--alert-terms", type=str, default=", ".join(ALERT_TERMS), help="Comma-separated alert terms")
    ap.add_argument("--exclude-terms", type=str, default=", ".join(DEFAULT_EXCLUDE_TERMS), help="Comma-separated exclusion terms")
    ap.add_argument("--min-score", type=int, default=0, help="Minimum score threshold after weighting")
    ap.add_argument("--people", type=int, default=5, help="Number of people to follow")
    ap.add_argument("--out", type=str, default="", help="Write digest to file")
    args = ap.parse_args()

    submolts = [s.strip() for s in args.submolts.split(",") if s.strip()] or None
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    alert_terms = [s.strip() for s in args.alert_terms.split(",") if s.strip()]
    exclude_terms = [s.strip() for s in args.exclude_terms.split(",") if s.strip()]

    posts = []
    if "moltbook" in sources:
        posts.extend(fetch_moltbook(limit=args.limit, submolts=submolts, sort=args.moltbook_sort))
    if "clawfee" in sources:
        posts.extend(fetch_clawfee(limit=args.limit))
    if "yclawker" in sources:
        posts.extend(fetch_yclawker(limit=args.limit, sort=args.yclawker_sort))

    if not posts:
        print("ERROR: No posts fetched. Check API keys/tokens.", file=sys.stderr)
        sys.exit(1)

    by_source = Counter([p.get("source", "unknown") for p in posts])
    fetched_total = len(posts)

    excluded_count = 0
    if exclude_terms:
        before = len(posts)
        posts = [p for p in posts if not should_exclude(p, terms=exclude_terms)]
        excluded_count = before - len(posts)

    below_min_score = 0
    if args.min_score > 0:
        before = len(posts)
        posts = [p for p in posts if score_post(p) >= args.min_score]
        below_min_score = before - len(posts)

    if not posts:
        print("ERROR: No posts left after filtering. Consider lowering --min-score or exclude terms.", file=sys.stderr)
        sys.exit(1)

    stats = {
        "fetched_total": fetched_total,
        "excluded": excluded_count,
        "below_min_score": below_min_score,
        "remaining": len(posts),
        "by_source": dict(by_source),
    }

    digest = render_digest(
        posts,
        top_n=args.top,
        theme_n=args.themes,
        opp_n=args.opps,
        build_n=args.buildlogs,
        alert_n=args.alerts,
        people_n=args.people,
        alert_terms=alert_terms,
        stats=stats,
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(digest)
    else:
        print(digest)


if __name__ == "__main__":
    main()
