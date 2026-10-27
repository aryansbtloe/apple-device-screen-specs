#!/usr/bin/env python3
"""Parse display facts out of saved Apple Tech Specs text (sources/raw/specs/*.txt and apple.com spec pages).
Output: sources/parsed_specs.json keyed by spec file. Every value here is copied from Apple's own wording;
the build step decides which values go into the dataset."""
import re, json, glob, os
D = None
def norm(t): return re.sub('[\u2010\u2011\u2012\u2013]', '-', t).replace('\u00a0', ' ')
def parse(path):
    raw = open(path).read(); t = norm(raw)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    title = None
    for l in lines[:15]:
        m = re.match(r'(.+?) - (Tech Specs|Technical Specifications)', l)
        if m: title = m.group(1).strip(); break
    year = (re.search(r'Year introduced:\s*(\d{4})', t) or [None, None])[1]
    displays, cur = [], None
    for l in lines:
        if re.search(r'external|AirPlay|Supports one (?:external )?display|Support for one (?:external )?display|connector|video mirroring|up to a native|One display up', l, re.I): continue
        m = re.search(r'(\d+(?:\.\d+)?)-inch \(diagonal\)', l)
        if m and len(l) < 300:
            cur = {'diagonal_in': float(m.group(1)), 'line': l}; displays.append(cur)
        m = re.search(r'(\d{3,4}) ?-?by-? ?(\d{3,4})(?:-pixel)?(?: native)? resolution(?: at (\d{2,3}) (?:ppi|pixels? per inch))?', l)
        if m and len(l) < 300:
            if cur is None or 'px' in cur: cur = {}; displays.append(cur)
            a, b = int(m.group(1)), int(m.group(2))
            cur['px'] = [min(a, b), max(a, b)] if True else None
            cur['px_line'] = l
            if m.group(3): cur['ppi'] = int(m.group(3))
    watch_px = [[int(a), int(b)] for a, b in re.findall(r'^\s*(\d{3}) by (\d{3}) pixels', t, re.M)]
    ppi_any = sorted(set(int(x) for x in re.findall(r'(\d{3}) (?:pixels? per inch|ppi)', t)))
    rect = [norm(l) for l in lines if 'rounded corners' in l and re.search(r'\d+(?:\.\d+)? inch', l)]
    act = re.findall(r'Actual diagonal screen size is (\d+(?:\.\d+)?)', t)
    feats = {
        'promotion': bool(re.search(r'ProMotion', t)),
        'refresh_120': bool(re.search(r'up to 120\s?Hz', t)) and bool(re.search(r'ProMotion', t)),
        'dynamic_island': 'Dynamic Island' in t,
        'face_id': bool(re.search(r'\bFace ID\b', t)),
        'touch_id': bool(re.search(r'\bTouch ID\b', t)),
        'home_button': bool(re.search(r'Home button|Home/Touch ID', t)),
        'top_button_touch_id': bool(re.search(r'Touch ID in the top button|Touch ID (?:sensor )?(?:built into|in) the top button', t, re.I)),
        'oled': bool(re.search(r'OLED', t)), 'tandem_oled': 'Tandem OLED' in t, 'micro_oled': 'Micro-OLED' in t or 'Micro‑OLED' in raw,
        'mini_led': bool(re.search(r'mini-LED', t, re.I)), 'lcd': bool(re.search(r'\bLCD\b|IPS technology|LED-backlit|LED backlit', t)),
        'ltpo': (re.search(r'LTPO\d?', t) or [None])[0], 'liquid_retina_xdr': 'Liquid Retina XDR' in t,
        'always_on': bool(re.search(r'Always-On', t, re.I)), 'one_hz': bool(re.search(r'\b1\s?Hz refresh|down to 1Hz|1Hz', t)),
    }
    watch_pairs = [[int(a), int(b), int(c)] for a, b, c in re.findall(r'(\d{3}) by (\d{3}) pixels\s*\n\s*(\d{3,4}) sq mm display area', t)]
    area = [int(x) for x in re.findall(r'(\d{3,4}) sq mm display area', t)]
    refresh_list = (re.search(r'Supported refresh rates: ([^\n]+)', t) or [None, None])[1]
    return {'title': title, 'year_introduced': year, 'displays': displays, 'watch_px': watch_px, 'ppi_mentions': ppi_any,
            'rounded_corner_notes': rect[:3], 'actual_diagonal': act[:1], 'display_area_mm2': area, 'watch_px_area': watch_pairs, 'features': feats,
            'refresh_rates_line': refresh_list}
out = {}
for p in sorted(glob.glob('sources/raw/specs/*.txt') + glob.glob('sources/raw/applecom-*-specs.txt')):
    out[os.path.basename(p)] = parse(p)
json.dump(out, open('sources/parsed_specs.json', 'w'), indent=1, ensure_ascii=False)
for k, v in out.items():
    d = '; '.join(f"{x.get('diagonal_in')}in {x.get('px')} {x.get('ppi')}ppi" for x in v['displays'])
    print(k, '|', v['title'], v['year_introduced'], '|', d, '| w', v['watch_px'], '| rect', [re.findall(r'(\d+(?:\.\d+)?) inch', r) for r in v['rounded_corner_notes'][:1]], v['actual_diagonal'])
