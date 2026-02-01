#!/usr/bin/env python3
"""Bluesky CLI - bird-like interface for Bluesky/AT Protocol"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.2.0"

try:
    from atproto import Client, client_utils
except ImportError:
    print("Error: atproto not installed. Run: pip install atproto", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = Path.home() / ".config" / "bsky" / "config.json"


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    os.chmod(CONFIG_PATH, 0o600)


def get_client():
    config = load_config()

    # Prefer session string (no password stored)
    if config.get("session"):
        client = Client()
        try:
            client.login(session_string=config["session"])
            # Update session in case it was refreshed
            new_session = client.export_session_string()
            if new_session != config["session"]:
                config["session"] = new_session
                save_config(config)
            return client
        except Exception:
            # Session expired/invalid, need to re-login
            print(
                "Session expired. Run: bsky login --handle your.handle --password your-app-password",
                file=sys.stderr,
            )
            sys.exit(1)

    # Legacy: support old configs with app_password (migrate on use)
    if config.get("handle") and config.get("app_password"):
        client = Client()
        client.login(config["handle"], config["app_password"])
        # Migrate to session-based auth
        config["session"] = client.export_session_string()
        del config["app_password"]
        save_config(config)
        print("(Migrated to session-based auth, app password removed)", file=sys.stderr)
        return client

    print(
        "Not logged in. Run: bsky login --handle your.handle --password your-app-password",
        file=sys.stderr,
    )
    sys.exit(1)


def cmd_login(args):
    try:
        client = Client()
        client.login(args.handle, args.password)
        # Store session string only - password never saved to disk
        config = {
            "handle": client.me.handle,
            "did": client.me.did,
            "session": client.export_session_string(),
        }
        save_config(config)
        print(f"Logged in as {client.me.handle} ({client.me.did})")
        print("(Password not stored - using session token)")
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_logout(args):
    config = load_config()
    if config.get("session"):
        config.pop("session", None)
        config.pop("handle", None)
        config.pop("did", None)
        save_config(config)
        print("Logged out successfully")
    else:
        print("Not logged in")


def cmd_whoami(args):
    config = load_config()
    if config.get("handle"):
        client = get_client()
        print(f"Handle: {client.me.handle}")
        print(f"DID: {client.me.did}")
    else:
        print("Not logged in")


def cmd_timeline(args):
    client = get_client()
    response = client.get_timeline(limit=args.count)

    for item in response.feed:
        post = item.post
        author = post.author.handle
        text = post.record.text if hasattr(post.record, "text") else ""
        created = post.record.created_at if hasattr(post.record, "created_at") else ""
        likes = post.like_count or 0
        reposts = post.repost_count or 0
        replies = post.reply_count or 0

        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            time_str = dt.strftime("%b %d %H:%M")
        except Exception:
            time_str = created[:16] if created else ""

        print(f"@{author} · {time_str}")
        print(f"  {text[:200]}")
        print(f"  ❤️ {likes}  🔁 {reposts}  💬 {replies}")
        print(f"  🔗 https://bsky.app/profile/{author}/post/{post.uri.split('/')[-1]}")
        print()


def cmd_post(args):
    text = args.text

    # Validate text
    if not text or not text.strip():
        print("Error: Post text cannot be empty", file=sys.stderr)
        sys.exit(1)

    if len(text) > 300:
        print(f"Error: Post is {len(text)} chars (max 300)", file=sys.stderr)
        sys.exit(1)

    # Dry run - show what would be posted without actually posting
    if args.dry_run:
        print("=== DRY RUN (not posting) ===")
        print(f"Text ({len(text)} chars):")
        print(f"  {text}")

        # Check for URLs
        url_pattern = r"(https?://[^\s]+)"
        urls = re.findall(url_pattern, text)
        if urls:
            print(f"Links detected: {len(urls)}")
            for url in urls:
                print(f"  • {url}")

        print("=============================")
        return

    client = get_client()

    # Auto-detect URLs and create proper facets using TextBuilder
    url_pattern = r"(https?://[^\s]+)"
    urls = re.findall(url_pattern, text)

    # Also detect @mentions
    mention_pattern = r"@([a-zA-Z0-9._-]+)"
    mentions = re.findall(mention_pattern, text)

    if urls or mentions:
        # Use TextBuilder for proper facets (links and mentions)
        builder = client_utils.TextBuilder()

        # Combined pattern to find both URLs and mentions in order
        combined_pattern = r"(https?://[^\s]+)|(@[a-zA-Z0-9._-]+)"
        last_end = 0

        # Resolve mention handles to DIDs
        mention_dids = {}
        for handle in mentions:
            full_handle = handle if "." in handle else f"{handle}.bsky.social"
            try:
                profile = client.get_profile(full_handle)
                mention_dids[handle] = profile.did
            except Exception:
                # If we can't resolve, skip making it a facet
                pass

        for match in re.finditer(combined_pattern, text):
            # Add text before the match
            if match.start() > last_end:
                builder.text(text[last_end : match.start()])

            if match.group(1):  # URL
                url = match.group(1)
                builder.link(url, url)
            elif match.group(2):  # Mention
                mention_text = match.group(2)
                handle = mention_text[1:]  # Remove @
                if handle in mention_dids:
                    builder.mention(mention_text, mention_dids[handle])
                else:
                    builder.text(mention_text)  # Can't resolve, just text

            last_end = match.end()

        # Add any remaining text
        if last_end < len(text):
            builder.text(text[last_end:])
        response = client.send_post(builder)
    else:
        response = client.send_post(text=text)

    uri = response.uri
    post_id = uri.split("/")[-1]
    print(f"Posted: https://bsky.app/profile/{client.me.handle}/post/{post_id}")


def cmd_delete(args):
    client = get_client()
    # Extract post ID from URL or use raw ID
    post_id = args.post_id
    if "bsky.app" in post_id:
        post_id = post_id.rstrip("/").split("/")[-1]

    # Construct the URI
    uri = f"at://{client.me.did}/app.bsky.feed.post/{post_id}"

    try:
        client.delete_post(uri)
        print(f"Deleted post: {post_id}")
    except Exception as e:
        print(f"Delete failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_profile(args):
    client = get_client()
    handle = args.handle.lstrip("@") if args.handle else client.me.handle

    # Auto-append .bsky.social if no domain specified
    if handle and "." not in handle:
        handle = f"{handle}.bsky.social"

    profile = client.get_profile(handle)
    print(f"@{profile.handle}")
    print(f"  Name: {profile.display_name or '(none)'}")
    print(f"  Bio: {profile.description or '(none)'}")
    print(f"  Followers: {profile.followers_count}")
    print(f"  Following: {profile.follows_count}")
    print(f"  Posts: {profile.posts_count}")
    print(f"  DID: {profile.did}")


def cmd_search(args):
    client = get_client()
    response = client.app.bsky.feed.search_posts({"q": args.query, "limit": args.count})

    if not response.posts:
        print("No results found.")
        return

    for post in response.posts:
        author = post.author.handle
        text = post.record.text if hasattr(post.record, "text") else ""
        likes = post.like_count or 0

        print(f"@{author}: {text[:150]}")
        print(
            f"  ❤️ {likes}  🔗 https://bsky.app/profile/{author}/post/{post.uri.split('/')[-1]}"
        )
        print()


def cmd_notifications(args):
    client = get_client()
    response = client.app.bsky.notification.list_notifications({"limit": args.count})

    for notif in response.notifications:
        reason = notif.reason
        author = notif.author.handle
        time_str = notif.indexed_at[:16] if notif.indexed_at else ""

        icons = {
            "like": "❤️",
            "repost": "🔁",
            "follow": "👤",
            "reply": "💬",
            "mention": "📢",
            "quote": "💭",
        }
        icon = icons.get(reason, "•")

        if reason == "like":
            print(f"{icon} @{author} liked your post · {time_str}")
        elif reason == "repost":
            print(f"{icon} @{author} reposted · {time_str}")
        elif reason == "follow":
            print(f"{icon} @{author} followed you · {time_str}")
        elif reason == "reply":
            print(f"{icon} @{author} replied · {time_str}")
        elif reason == "mention":
            print(f"{icon} @{author} mentioned you · {time_str}")
        elif reason == "quote":
            print(f"{icon} @{author} quoted you · {time_str}")
        else:
            print(f"{icon} {reason} from @{author} · {time_str}")


def main():
    parser = argparse.ArgumentParser(description="Bluesky CLI")
    parser.add_argument("-v", "--version", action="version", version=f"bsky {VERSION}")
    subparsers = parser.add_subparsers(dest="command")

    # login
    login_p = subparsers.add_parser("login", help="Login to Bluesky")
    login_p.add_argument(
        "--handle", required=True, help="Your handle (e.g. user.bsky.social)"
    )
    login_p.add_argument(
        "--password", required=True, help="App password (not your main password)"
    )

    # logout
    subparsers.add_parser("logout", help="Log out and clear session")

    # whoami
    subparsers.add_parser("whoami", help="Show current user")

    # timeline
    tl_p = subparsers.add_parser(
        "timeline", aliases=["tl", "home"], help="Show home timeline"
    )
    tl_p.add_argument("-n", "--count", type=int, default=10, help="Number of posts")

    # post
    post_p = subparsers.add_parser("post", aliases=["p"], help="Create a post")
    post_p.add_argument("text", help="Post text")
    post_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without posting",
    )

    # delete
    del_p = subparsers.add_parser("delete", aliases=["del", "rm"], help="Delete a post")
    del_p.add_argument("post_id", help="Post ID or URL")

    # profile
    profile_p = subparsers.add_parser("profile", help="Show profile")
    profile_p.add_argument(
        "handle", nargs="?", help="Handle to look up (default: self)"
    )

    # search
    search_p = subparsers.add_parser("search", aliases=["s"], help="Search posts")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument(
        "-n", "--count", type=int, default=10, help="Number of results"
    )

    # notifications
    notif_p = subparsers.add_parser(
        "notifications", aliases=["notif", "n"], help="Show notifications"
    )
    notif_p.add_argument(
        "-n", "--count", type=int, default=20, help="Number of notifications"
    )

    args = parser.parse_args()

    commands = {
        "login": cmd_login,
        "logout": cmd_logout,
        "whoami": cmd_whoami,
        "timeline": cmd_timeline,
        "tl": cmd_timeline,
        "home": cmd_timeline,
        "post": cmd_post,
        "p": cmd_post,
        "delete": cmd_delete,
        "del": cmd_delete,
        "rm": cmd_delete,
        "profile": cmd_profile,
        "search": cmd_search,
        "s": cmd_search,
        "notifications": cmd_notifications,
        "notif": cmd_notifications,
        "n": cmd_notifications,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
