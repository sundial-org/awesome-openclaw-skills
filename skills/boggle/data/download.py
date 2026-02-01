#!/usr/bin/env python3
"""Download Boggle dictionaries from GitHub."""
import os, urllib.request

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://raw.githubusercontent.com/christianhaberl/boggle-openclaw-skill/main/data"
FILES = ["words_english_boggle.txt", "words_german_boggle.txt"]

for f in FILES:
    path = os.path.join(DATA_DIR, f)
    if not os.path.exists(path):
        print(f"Downloading {f}...")
        urllib.request.urlretrieve(f"{BASE_URL}/{f}", path)
        print(f"  -> {path}")
    else:
        print(f"{f} already exists.")
