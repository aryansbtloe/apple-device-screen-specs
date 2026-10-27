#!/usr/bin/env python3
"""Cross-check helper: parse model identifiers ("hardware strings") from Wikipedia wikitext tables.
Wikipedia is a secondary source; identifiers are flagged as such in the dataset."""
import re, json, sys
def clean(c):
    c = re.sub(r'^[^|]*\|(?=[^\]]*$)', '', c) if c.count('[[') == 0 and '|' in c and ('style=' in c or 'scope=' in c or 'colspan' in c) else c
    c = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', c)
    c = re.sub(r'<br\s*/?>', ' / ', c); c = re.sub(r'<[^>]+>', '', c)
    c = re.sub(r'\{\{[^}]*\}\}', '', c); c = re.sub(r"'''?", '', c)
    return re.sub(r'\s+', ' ', c).strip()
def cells(row, header=False):
    out = []
    for line in row.split('\n'):
        line = line.strip()
        if not line or line[0] not in '!|': continue
        body = line[1:]
        span = 1
        m = re.match(r'\s*([^|\[]*?colspan\s*=\s*"?(\d+)"?[^|\[]*)\|(.*)$', body)
        if m: span = int(m.group(2)); body = m.group(3)
        else:
            m2 = re.match(r'\s*((?:scope|style|class|rowspan)[^|\[]*)\|(.*)$', body)
            if m2: body = m2.group(2)
        out.append((clean(body), span, line.startswith('!')))
    return out
res = {}
for page in sys.argv[1:]:
    t = open(page).read()
    for tb in re.findall(r'\{\|.*?\n\|\}', t, re.S):
        rows = re.split(r'\n\|-[^\n]*', tb)
        hs = [r for r in rows if re.search(r'\|\s*(Hardware [Ss]trings?|Model identifiers?|Identifier)\s*$', r, re.M)]
        if not hs: continue
        head = cells(rows[0])
        # first header cells "Model" with colspan>1 are the row-label columns
        models = []
        for txt, span, _ in head:
            if txt.lower() in ('model', ''): continue
            models += [txt] * span if span > 1 else [txt]
        vals = []
        for txt, span, isH in cells(hs[0]):
            if isH: continue
            vals += [txt] * span
        if not models or len(models) < len(vals):
            # fallback for multi-row sortable headers: take [[iPad ...|label]] header cells in order
            models = re.findall(r'^!.*?\|\s*(?:\[\[)?([^\]\n]*iPad[^\]\n]*)', tb[:3000], re.M)
            models = [m.strip() for m in models]
            raw = re.search(r'Hardware strings?\s*\n((?:\|[^\n]*\n)+)', tb, re.I)
            if raw: vals = [clean(x[1:]) for x in raw.group(1).strip().split('\n') if x.startswith('|') and not x.startswith('|-')]
        for m, v in zip(models, vals):
            res.setdefault(page.split('wiki-')[-1].split('.')[0], []).append({'name': m, 'identifiers': [x.strip() for x in re.split(r'[ /,]+(?=[A-Za-z])', v) if x.strip()]})
json.dump(res, open('sources/wikipedia_identifiers.json', 'w'), indent=1)
for k, v in res.items():
    print(k, len(v))
    for e in v: print('   ', e['name'], '=>', e['identifiers'])
