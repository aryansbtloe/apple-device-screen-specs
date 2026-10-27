#!/usr/bin/env python3
"""Pull display-related lines out of crawled Apple Tech Specs text. Research helper."""
import json, re
idx = json.load(open('sources/specs_index.json'))
PAT = re.compile(r'(diagonal|ppi|pixels per inch|pixel resolution|resolution|Hz|ProMotion|OLED|LCD|LTPO|mini-LED|Mini-LED|Liquid Retina|Retina|Dynamic Island|nits|Display Area|display area|sq mm|mm case|Touch ID|Face ID|Home button)', re.I)
out = []
for it in idx:
    if not it.get('specs_file'): continue
    t = open(it['specs_file']).read()
    title = (re.search(r'^\s*(.+?) - (Tech Specs|Technical Specifications)', t, re.M) or [None, None])[1]
    lines = [l.strip() for l in t.split('\n') if PAT.search(l) and len(l) < 400]
    # keep only first ~25 matching lines to stay compact
    it['page_title'] = title
    it['display_lines'] = lines[:30]
    out.append(it)
json.dump(out, open('sources/display_extract.json', 'w'), indent=1, ensure_ascii=False)
