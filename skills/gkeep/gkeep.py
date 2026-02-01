#!/usr/bin/env python3
"""
gkeep - CLI wrapper for gkeepapi
Usage:
  gkeep login <email>           # Login and save token
  gkeep list [--limit N]        # List notes
  gkeep search <query>          # Search notes
  gkeep get <note_id>           # Get note by ID
  gkeep create <title> [body]   # Create a note
  gkeep archive <note_id>       # Archive a note
  gkeep delete <note_id>        # Delete (trash) a note
  gkeep check <note_id> <text>  # Check an item in a list note
  gkeep add <note_id> <text>    # Add item to list or append text
  gkeep pin <note_id>           # Pin a note
  gkeep unpin <note_id>         # Unpin a note
  gkeep stats                   # Show note counts
"""
import sys
import os
import json
import getpass
from pathlib import Path

import gkeepapi

TOKEN_FILE = Path.home() / ".config" / "gkeep" / "token.json"


def load_keep():
    keep = gkeepapi.Keep()
    if TOKEN_FILE.exists():
        data = json.loads(TOKEN_FILE.read_text())
        keep.authenticate(data["email"], data["token"])
    else:
        print("Not logged in. Run: gkeep login <email>", file=sys.stderr)
        sys.exit(1)
    return keep


def cmd_login(email):
    keep = gkeepapi.Keep()
    password = os.environ.get("GKEEP_PASSWORD") or getpass.getpass(
        "Password (or app password): "
    )
    try:
        keep.login(email, password)
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        print(
            "Tip: Use an App Password from https://myaccount.google.com/apppasswords",
            file=sys.stderr,
        )
        sys.exit(1)

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(
        json.dumps({
            "email": email,
            "token": keep.getMasterToken(),
        })
    )
    TOKEN_FILE.chmod(0o600)
    print(f"Logged in as {email}. Token saved to {TOKEN_FILE}")


def cmd_list(limit=20):
    keep = load_keep()
    keep.sync()
    notes = list(keep.all())[:int(limit)]
    for note in notes:
        if note.trashed or note.archived:
            continue
        title = note.title or "(untitled)"
        preview = (note.text or "")[:50].replace("\n", " ")
        print(f"[{note.id}] {title}: {preview}...")


def cmd_search(query):
    keep = load_keep()
    keep.sync()
    results = keep.find(query=query)
    for note in results:
        if note.trashed:
            continue
        title = note.title or "(untitled)"
        preview = (note.text or "")[:50].replace("\n", " ")
        print(f"[{note.id}] {title}: {preview}...")


def cmd_get(note_id):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)
    print(f"Title: {note.title or '(untitled)'}")
    print(f"ID: {note.id}")
    print("---")
    print(note.text or "")


def cmd_create(title, body=""):
    keep = load_keep()
    note = keep.createNote(title, body)
    keep.sync()
    print(f"Created note: {note.id}")


def cmd_archive(note_id):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)
    note.archived = True
    keep.sync()
    print(f"Archived: {note_id}")


def cmd_delete(note_id):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)
    note.trashed = True
    keep.sync()
    print(f"Deleted (trashed): {note_id}")


def cmd_check(note_id, query):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)

    found = False
    if hasattr(note, "items"):
        for item in note.items:
            if query.lower() in item.text.lower() and not item.checked:
                item.checked = True
                found = True
                print(f"Checked: {item.text}")

    if found:
        keep.sync()
        print("Synced changes.")
    elif hasattr(note, "items"):
        print(f"No unchecked item found matching: {query}")
    else:
        print("This is not a list note.")


def cmd_add(note_id, text):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)

    if hasattr(note, "items"):
        note.add(text, False)
        keep.sync()
        print(f"Added item: {text}")
    else:
        current = note.text or ""
        note.text = current + "\n" + text
        keep.sync()
        print(f"Appended text: {text}")


def cmd_pin(note_id, pinned):
    keep = load_keep()
    keep.sync()
    note = keep.get(note_id)
    if not note:
        print(f"Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)
    note.pinned = pinned
    keep.sync()
    action = "Pinned" if pinned else "Unpinned"
    print(f"{action}: {note_id}")


def cmd_stats():
    keep = load_keep()
    keep.sync()

    active = 0
    archived = 0
    trashed = 0
    pinned = 0
    total = 0

    for note in keep.all():
        total += 1
        if note.pinned and not note.trashed and not note.archived:
            pinned += 1

        if note.trashed:
            trashed += 1
        elif note.archived:
            archived += 1
        else:
            active += 1

    print("Your full breakdown:")
    print(f"Active: {active}")
    print(f"Pinned: {pinned}")
    print(f"Archived: {archived}")
    print(f"Trashed: {trashed}")
    print(f"Total: {total}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "login":
        if not args:
            print("Usage: gkeep login <email>", file=sys.stderr)
            sys.exit(1)
        cmd_login(args[0])
    elif cmd == "list":
        limit = 20
        if "--limit" in args:
            idx = args.index("--limit")
            limit = args[idx + 1] if idx + 1 < len(args) else 20
        cmd_list(limit)
    elif cmd == "search":
        if not args:
            print("Usage: gkeep search <query>", file=sys.stderr)
            sys.exit(1)
        cmd_search(" ".join(args))
    elif cmd == "get":
        if not args:
            print("Usage: gkeep get <note_id>", file=sys.stderr)
            sys.exit(1)
        cmd_get(args[0])
    elif cmd == "create":
        if not args:
            print("Usage: gkeep create <title> [body]", file=sys.stderr)
            sys.exit(1)
        title = args[0]
        body = " ".join(args[1:]) if len(args) > 1 else ""
        cmd_create(title, body)
    elif cmd == "archive":
        if not args:
            print("Usage: gkeep archive <note_id>", file=sys.stderr)
            sys.exit(1)
        cmd_archive(args[0])
    elif cmd == "delete":
        if not args:
            print("Usage: gkeep delete <note_id>", file=sys.stderr)
            sys.exit(1)
        cmd_delete(args[0])
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "check":
        if len(args) < 2:
            print("Usage: gkeep check <note_id> <text>", file=sys.stderr)
            sys.exit(1)
        cmd_check(args[0], " ".join(args[1:]))
    elif cmd == "add":
        if len(args) < 2:
            print("Usage: gkeep add <note_id> <text>", file=sys.stderr)
            sys.exit(1)
        cmd_add(args[0], " ".join(args[1:]))
    elif cmd == "pin":
        if not args:
            print("Usage: gkeep pin <note_id>", file=sys.stderr)
            sys.exit(1)
        cmd_pin(args[0], True)
    elif cmd == "unpin":
        if not args:
            print("Usage: gkeep unpin <note_id>", file=sys.stderr)
            sys.exit(1)
        cmd_pin(args[0], False)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
