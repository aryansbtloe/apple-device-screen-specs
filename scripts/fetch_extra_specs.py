#!/usr/bin/env python3
"""Fetch Apple Tech Specs pages not linked from the support.apple.com/docs indexes. Research helper."""
import subprocess, re, html
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
EXTRA = {'watch': [111985, 112022, 111891, 111984, 118453, 111918, 111833, 121202, 125093, 148589, 148758, 112009],
         'vision': [117810, 125436]}
def text(h):
    h = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<(tr|br|p|h\d|li|div|td|th|dt|dd)[^>]*>', '\n', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = html.unescape(re.sub(r'[ \t\xa0]+', ' ', h))
    return re.sub(r'\n\s*\n+', '\n', h)
for fam, ids in EXTRA.items():
    for i in ids:
        h = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, f"https://support.apple.com/en-us/{i}"], capture_output=True, text=True).stdout
        open(f"sources/raw/specs/{fam}-sp{i}.txt", "w").write(text(h))
        print(fam, i, len(h))
