"""Print the status and first lines of each URL given on the command line (format checks only).

    uv run python scripts/peek_urls.py URL [URL ...]
"""

from __future__ import annotations

import json
import re
import sys

import requests

HEADERS = {"User-Agent": "uap-geo-research/0.1 (+https://github.com/Fagundo/uap-analytics)"}

for url in sys.argv[1:]:
    print(f"==> {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        print(f"status {resp.status_code}, {len(resp.content):,} bytes")
        lines = resp.text.splitlines()
        if "action=raw" in url:  # wikitext: show the infobox only
            end = next((i for i, l in enumerate(lines) if l.strip() == "}}"), 40)
            lines = lines[:min(end + 1, 60)]
        for line in lines[:60 if "action=raw" in url else 12]:
            print(line[:400])
        if "format=json" in url:  # ScienceBase item: list attached files
            for f in resp.json().get("files", []):
                print(f"file {f.get('name')} {f.get('size', 0):,} bytes {f.get('url')}")
        elif "<html" in resp.text[:2000].lower():  # HTML page: list links to data files
            for href in sorted(set(re.findall(r'href="([^"]+\.(?:zip|gz|tgz|shp|csv|gdb)[^"]*)"', resp.text))):
                print(f"link {href}")
        if len(lines) > 12:
            print(f"... {len(lines):,} lines; last: {lines[-1][:400]}")
    except Exception as exc:  # report and continue
        print(f"failed: {exc}")
