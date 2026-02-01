#!/usr/bin/env python3
"""Find Surfline spot ids using the public Surfline search endpoint."""

import sys
from surfline_client import search_spots


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: surfline_search.py <query>")
        return 2
    q = " ".join(sys.argv[1:])
    hits = search_spots(q)
    if not hits:
        print("No spot results.")
        return 1
    for h in hits:
        loc = f" ({h.latitude},{h.longitude})" if h.latitude is not None else ""
        print(f"{h.name}\t{h.spot_id}{loc}\t{h.url or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
