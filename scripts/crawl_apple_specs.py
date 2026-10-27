#!/usr/bin/env python3
"""Crawl support.apple.com/docs index pages -> product doc pages -> Tech Specs pages.
Saves raw HTML + extracted plain text under sources/raw/specs/. Research helper, not part of the published package."""
import re, html, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
OUT = "sources/raw/specs"; os.makedirs(OUT, exist_ok=True)

def get(url):
    return subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, url], capture_output=True, text=True).stdout

def text(h):
    h = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<(tr|br|p|h\d|li|div|td|th|dt|dd)[^>]*>', '\n', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = html.unescape(re.sub(r'[ \t\xa0]+', ' ', h))
    return re.sub(r'\n\s*\n+', '\n', h)

KEEP = {
 'iphone': lambda t: t.startswith('iPhone') and not re.search(r'Battery|MagSafe', t),
 'ipad': lambda t: t.startswith('iPad'),
 'ipod': lambda t: t.startswith('iPod touch'),
 'watch': lambda t: t.startswith('Apple Watch'),
 'mac': lambda t: re.match(r'(MacBook|iMac)', t) and re.search(r'20(2\d)|M\d|Neo', t),
}
items = []
for fam, keep in KEEP.items():
    t = open(f"sources/raw/docs-{fam}.html").read()
    seen = set()
    for h, txt in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', t, flags=re.S):
        txt = html.unescape(re.sub(r'<[^>]+>', '', txt)).strip()
        if '/en-us/docs/' in h and re.search(r'/(\d{6}|pl\d+)$', h) and keep(txt) and h not in seen:
            seen.add(h); items.append({'family_index': fam, 'title': txt, 'docs_url': h})

def work(it):
    pid = it['docs_url'].rstrip('/').split('/')[-1]
    d = get(it['docs_url'])
    m = re.search(r'data-ss-analytics-link-url="([^"]+)" data-ss-analytics-link-text="tech specs"', d) or \
        re.search(r'href="(https://support.apple.com/en-us/\d+)"[^>]*>\s*Tech Specs', d)
    it['year_introduced'] = (re.search(r'Year introduced:\s*</?[^>]*>?\s*(\d{4})', d) or re.search(r'Year introduced:.*?(\d{4})', text(d), re.S) or [None,None])[1]
    if m:
        it['specs_url'] = m.group(1)
        s = get(it['specs_url'])
        open(f"{OUT}/{it['family_index']}-{pid}.html", 'w').write(s)
        open(f"{OUT}/{it['family_index']}-{pid}.txt", 'w').write(text(s))
        it['specs_file'] = f"{OUT}/{it['family_index']}-{pid}.txt"
    return it

with ThreadPoolExecutor(12) as ex:
    res = list(ex.map(work, items))
json.dump(res, open("sources/specs_index.json", "w"), indent=1)
print(len(res), sum(1 for r in res if r.get('specs_url')))
