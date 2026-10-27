#!/usr/bin/env python3
"""Compare the existing bestlatestapps.com/tools/iphone-screen-sizes/ table (saved HTML) with data/devices.json."""
import re, html, json
t = open('sources/raw/bla-iphone-screen-sizes.html').read()
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S)
dev = {d['name']: d for d in json.load(open('data/devices.json'))['devices']}
def norm_names(cell):
    cell = cell.replace('iPhone SE (2nd and 3rd gen)', 'iPhone SE (2nd generation) / iPhone SE (3rd generation)')
    parts = [p.strip() for p in cell.split('/')]
    out, prefix = [], ''
    for p in parts:
        if p.startswith('iPhone'): prefix = re.match(r'(iPhone \d+)', p).group(1) if re.match(r'iPhone \d+', p) else ''; out.append(p)
        elif re.match(r'^\d', p): out.append('iPhone ' + p)
        else: out.append((prefix + ' ' + p).strip() if prefix and p in ('Pro', 'mini', 'Plus') else 'iPhone ' + p)
    return out
issues = []
for r in rows:
    cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
    if len(cells) < 6 or cells[0] == 'Model': continue
    name, pts, scale, pix, ppi, diag = cells[:6]
    pw, ph = map(int, re.findall(r'\d+', pts)); xw, xh = map(int, re.findall(r'\d+', pix))
    for n in norm_names(name):
        d = dev.get(n)
        if not d: issues.append(f'{n}: on site, not in dataset'); continue
        s = d['screen']; lp = s['logical_resolution_pt'] or {}; px = s['resolution_px']
        if lp and (lp['width'], lp['height']) != (pw, ph): issues.append(f'{n}: site points {pw}x{ph}, dataset (HIG) {lp["width"]}x{lp["height"]}')
        if not lp: issues.append(f'{n}: site points {pw}x{ph}, dataset null (not published by Apple)')
        if (px['width'], px['height']) != (xw, xh): issues.append(f'{n}: site pixels {xw}x{xh}, dataset {px["width"]}x{px["height"]}')
        if int(ppi) != s['ppi']: issues.append(f'{n}: site ppi {ppi}, dataset {s["ppi"]}')
        if float(diag.rstrip('″"')) != s['diagonal_in']: issues.append(f'{n}: site diagonal {diag}, dataset {s["diagonal_in"]}')
site_names = set()
missing = [d['name'] for d in dev.values() if d['family'] == 'iphone' and d['release_year'] >= 2014]
print('\n'.join(issues) or 'no differences')
