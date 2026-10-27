#!/usr/bin/env python3
"""Build data/devices.json and data/devices.csv from:
  - sources/parsed_specs.json   (Apple Tech Specs pages, parsed by parse_specs.py)
  - sources/hig_tables_20260702.txt (Apple HIG layout tables, Wayback snapshot 2026-07-02)
  - sources/wikipedia_identifiers.json (cross-check only: model identifiers)
  - scripts/catalog.py (which page backs which device + categorical facts)
  - sources/simulator/measurements.json (Xcode 27.1 Simulator: runtime UIScreen/safe-area probe + device-type
    capabilities.plist; produced by scripts/import_simulator.py)
Writes reports/gaps.md and reports/conflicts.md as well."""
import json, re, math, csv, os, sys
from fractions import Fraction
sys.path.insert(0, os.path.dirname(__file__))
from catalog import ALL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SPECS = json.load(open('sources/parsed_specs.json'))
INDEX = {os.path.basename(x['specs_file']): x for x in json.load(open('sources/specs_index.json')) if x.get('specs_file')}
WIKI = {}
for page, rows in json.load(open('sources/wikipedia_identifiers.json')).items():
    for r in rows: WIKI.setdefault(r['name'], r['identifiers'])

HIG_URL = 'https://developer.apple.com/design/human-interface-guidelines/layout'
HIG_SNAPSHOT = 'https://web.archive.org/web/20260702060104/https://developer.apple.com/tutorials/data/design/human-interface-guidelines/layout.json'
WIKI_URLS = {'iphone': 'https://en.wikipedia.org/wiki/List_of_iPhone_models', 'ipad': 'https://en.wikipedia.org/wiki/List_of_iPad_models',
             'ipod-touch': 'https://en.wikipedia.org/wiki/IPod_Touch'}

# ---- HIG tables ----
HIG, HIG_WATCH = {}, {}
for line in open('sources/hig_tables_20260702.txt'):
    m = re.match(r'\s+(.+?) \| (\d+)x(\d+) pt \((\d+)x(\d+) px @(\d)x\)', line)
    if m:
        HIG[m.group(1)] = dict(pt=[int(m.group(2)), int(m.group(3))], px=[int(m.group(4)), int(m.group(5))], scale=int(m.group(6)))
    m = re.match(r'\s+(.+?) \| (\d+)mm \| (\d+) \| (\d+)\s*$', line)
    if m:
        HIG_WATCH[(m.group(1), int(m.group(2)))] = [int(m.group(3)), int(m.group(4))]

gaps, conflicts, warnings = [], [], []

# ---- Xcode Simulator measurements (see scripts/import_simulator.py) ----
SIMFILE = 'sources/simulator/measurements.json'
SIM = json.load(open(SIMFILE)) if os.path.exists(SIMFILE) else {'meta': {}, 'devices': {}}
SIM_SOURCE = {'url': 'https://developer.apple.com/xcode/', 'publisher': 'Apple',
              'title': 'Xcode 27.1 (27A9275) Simulator: UIKit probe app (scripts/simulator/Measure.swift) and device-type capabilities.plist, measured 2026-10-27',
              'used_for': []}
sim_stats = {'runtime_measured': [], 'static_only': [], 'radius_static_vs_runtime_mismatch': []}

def _pt(d): return {'width': d['width'], 'height': d['height']}

def apply_sim(rec, c):
    entries = SIM['devices'].get(rec['id'])
    fam = rec['family']; scr = rec['screen']; prov = rec['provenance']; rid = rec['id']
    if not entries:
        if fam in ('iphone', 'ipad', 'ipod-touch'):
            gaps.append(f"{rid}: safe-area insets, measured points and corner radius not available (no Xcode 27.1 Simulator device type)")
        return
    used = set()
    measured = [e for e in entries if e['runtime']]
    for e in measured:  # static vs runtime corner radius cross-check (justifies using the static key where no runtime exists)
        if e['static']['DeviceCornerRadius'] is not None and abs(e['runtime']['display_corner_radius_unofficial'] - e['static']['DeviceCornerRadius']) > 0.01:
            sim_stats['radius_static_vs_runtime_mismatch'].append(f"{e['device_type']}: static {e['static']['DeviceCornerRadius']} vs runtime {e['runtime']['display_corner_radius_unofficial']}")
    if measured:
        e = sorted(measured, key=lambda x: len(x['device_type']))[0]
        rt = e['runtime']; src = f"source: Xcode 27.1 Simulator, {rt['runtime']} runtime, device type '{e['device_type']}'"
        for o in measured[1:]:
            ort = o['runtime']
            if (ort['bounds_pt'], ort['native_scale'], ort['portrait']['safe_area_insets_pt'], ort['landscape_left']['safe_area_insets_pt']) != (rt['bounds_pt'], rt['native_scale'], rt['portrait']['safe_area_insets_pt'], rt['landscape_left']['safe_area_insets_pt']):
                warnings.append(f"{rid}: simulator device types '{e['device_type']}' and '{o['device_type']}' disagree")
        sim_stats['runtime_measured'].append(rid)
        screens = rt['screens'] or [{'bounds_pt': rt['bounds_pt'], 'native_bounds_px': rt['native_bounds_px'], 'scale': rt['scale'], 'native_scale': rt['native_scale'], 'display_corner_radius_unofficial': rt['display_corner_radius_unofficial']}]
        targets = [(scr, None)] + [(s2, s2.get('label')) for s2 in rec['secondary_screens']]
        main_px = (scr.get('resolution_px') or {})
        def match(target):
            px = target.get('resolution_px') or {}
            for sc in screens:
                if sc['native_bounds_px'] == px: return sc
            return None
        for target, label in targets:
            tag = f" [{label}]" if label else ''
            sc = match(target)
            if sc is None and label is None and len(screens) == 1 and not target.get('resolution_px'): sc = screens[0]
            if sc is None:
                if len(screens) > 1 or label:
                    conflicts.append(f"{rid}{tag}: no UIScreen in the Simulator has Apple's {target['resolution_px']['width']}x{target['resolution_px']['height']} px; UIScreen.screens = " + ', '.join(f"{s_['bounds_pt']['width']}x{s_['bounds_pt']['height']} pt / {s_['native_bounds_px']['width']}x{s_['native_bounds_px']['height']} px @{s_['scale']}x (nativeScale {s_['native_scale']})" for s_ in screens) + '. Points left null for this screen.')
                continue
            pts, k, ns = _pt(sc['bounds_pt']), sc['scale'], sc['native_scale']
            npx = sc['native_bounds_px']
            if target.get('resolution_px') and npx != target['resolution_px']:
                conflicts.append(f"{rid}{tag}: Simulator nativeBounds {npx['width']}x{npx['height']} px vs Apple {target['resolution_px']['width']}x{target['resolution_px']['height']} px")
            lp = target.get('logical_resolution_pt')
            pkey = 'logical_resolution_pt' + (f'[{label}]' if label else '')
            if lp is None:
                target['logical_resolution_pt'] = pts; target['scale'] = int(k)
                target['native_scale'] = round(ns, 4) if abs(ns - k) > 1e-6 else None
                prov[pkey] = f"measured: UIScreen.bounds {pts['width']}x{pts['height']} pt, scale {k}, nativeScale {ns} ({src})"
                used.add('logical_resolution'); used.add('scale')
            elif lp != pts:
                if c.get('mini_conflict'):
                    target['logical_resolution_pt'] = pts; target['scale'] = int(k); target['native_scale'] = round(ns, 4)
                    prov[pkey] = (f"measured: UIScreen.main.bounds = {pts['width']}x{pts['height']} pt, scale {k}, nativeScale {ns}, nativeBounds {npx['width']}x{npx['height']} px ({src}); "
                                  f"the device-type capabilities.plist renders a {e['static']['displays'][0]['canvas_width_px']}x{e['static']['displays'][0]['canvas_height_px']} canvas downsampled to the {npx['width']}x{npx['height']} panel. "
                                  f"Apple HIG (snapshot 2026-07-02) lists {lp['width']}x{lp['height']} pt, i.e. the panel / 3; UIKit never reports that size at the default (Standard) display zoom")
                    used.add('logical_resolution'); used.add('scale')
                    conflicts.append(f"{rid}: SETTLED by Simulator. UIScreen.main.bounds = {pts['width']}x{pts['height']} pt @{k}x, nativeScale {ns}, nativeBounds {npx['width']}x{npx['height']} px. The HIG's {lp['width']}x{lp['height']} pt is the physical panel divided by 3, not what UIKit reports. Dataset now uses {pts['width']}x{pts['height']} pt with native_scale {round(ns, 4)}.")
                else:
                    conflicts.append(f"{rid}{tag}: dataset points {lp['width']}x{lp['height']} vs Simulator UIScreen.bounds {pts['width']}x{pts['height']} pt; dataset value kept")
            else:
                if target.get('scale') != k:
                    conflicts.append(f"{rid}{tag}: dataset scale {target.get('scale')} vs Simulator {k}")
                old = prov.get(pkey, 'apple-hig')
                if old.startswith('derived'):
                    prov[pkey] = old + f"; CONFIRMED by Simulator UIScreen.bounds {pts['width']}x{pts['height']} pt @{k}x, nativeScale {ns} ({src})"
                    used.add('logical_resolution')
                if target.get('native_scale') is not None and abs(target['native_scale'] - ns) > 0.001:
                    conflicts.append(f"{rid}{tag}: dataset native_scale {target['native_scale']} vs Simulator {ns}")
            cr = sc.get('display_corner_radius_unofficial')
            if cr is not None:
                target['corner_radius_pt'] = cr
                sd_ = next((d_ for d_ in e['static']['displays'] if {'width': d_['width_px'], 'height': d_['height_px']} == sc['native_bounds_px']), None)
                asym = f"; the device type's capabilities.plist declares unequal corners for this display {sd_['corner_radius']}" if sd_ and len(set(sd_['corner_radius'].values())) > 1 else ''
                prov['corner_radius_pt' + (f'[{label}]' if label else '')] = f"UNOFFICIAL: private UIScreen _displayCornerRadius = {cr} pt ({src}){asym}; Apple does not publish this value"
                used.add('corner_radius (unofficial)')
            target['simulator_measurement'] = {'device_type': e['device_type'], 'runtime': rt['runtime'], 'bounds_pt': pts, 'native_bounds_px': npx, 'scale': k, 'native_scale': ns}
        seen_px = [sc_['native_bounds_px'] for sc_ in screens]
        for d_ in e['static']['displays']:
            if {'width': d_['width_px'], 'height': d_['height_px']} not in seen_px:
                conflicts.append(f"{rid}: Simulator device type '{e['device_type']}' declares a second integrated display '{d_['name']}' of {d_['width_px']}x{d_['height_px']} px @{d_['scale']}x (hdpi {d_['hdpi']}, corner radius {d_['corner_radius']}) that UIScreen.screens never exposed at launch; it does not match Apple's {main_px.get('width')}x{main_px.get('height')} px for the primary display")
        # safe areas (window of the app scene, i.e. the screen the app is shown on)
        pr, ll, lr = rt['portrait'], rt['landscape_left'], rt['landscape_right']
        on = next((t for t, _ in targets if t.get('simulator_measurement') and t['simulator_measurement']['bounds_pt'] == rt['bounds_pt']), scr)
        okp = pr['rotation_ok'] and pr['window_is_full_screen']; okl = ll['rotation_ok'] and ll['window_is_full_screen']
        if on is scr:
            if okp:
                rec['safe_area_insets_pt']['portrait'] = pr['safe_area_insets_pt']
            if okl:
                rec['safe_area_insets_pt']['landscape'] = ll['safe_area_insets_pt']
            if okp or okl:
                used.add('safe_area_insets')
                lr_note = '' if lr['safe_area_insets_pt'] == ll['safe_area_insets_pt'] else f"; landscapeRight differs: {lr['safe_area_insets_pt']}"
                prov['safe_area_insets_pt'] = (f"measured: key window safeAreaInsets, portrait and landscape (interface orientation landscapeLeft, rotated with requestGeometryUpdate; landscapeRight identical{lr_note if lr_note else ''})"
                                               .replace('identical; landscapeRight differs', 'checked; landscapeRight differs') + f" ({src})")
            if not okp: gaps.append(f"{rid}: portrait safe area not captured (window not full screen or rotation failed in Simulator)")
            if not okl:
                err = ll.get('geometry_error')
                gaps.append(f"{rid}: landscape safe area not captured" + (f" (iPadOS refused requestGeometryUpdate: '{err}'; a retry with UIRequiresFullScreen rotated but gave asymmetric, physically inconsistent insets, see sources/simulator/experiments/)" if err else " (rotation failed in Simulator)"))
            if fam == 'ipad' and okp:
                prov['safe_area_insets_pt'] = prov['safe_area_insets_pt'].split(' (source:')[0].replace(', portrait and landscape (interface orientation landscapeLeft, rotated with requestGeometryUpdate; landscapeRight checked; landscapeRight differs: ', ', portrait only (').replace(', portrait and landscape (interface orientation landscapeLeft, rotated with requestGeometryUpdate; landscapeRight identical)', ', portrait only') + f"; full-screen window in the iPadOS 27 default windowing mode, top inset includes the 32 pt status bar ({src})"
        else:
            on['simulator_measurement']['safe_area_insets_raw_unverified_pt'] = {'portrait': pr['safe_area_insets_pt'], 'landscape_left': ll['safe_area_insets_pt'], 'landscape_right': lr['safe_area_insets_pt']}
            on['simulator_measurement']['note'] = ('UNVERIFIED: the probe app launched only on this screen. Its safe-area insets look anomalous (portrait and landscapeLeft report the same '
                                                    f"{pr['safe_area_insets_pt']} with the window frame swapped, and a {pr['status_bar_height_pt']} pt status bar), so they are kept here as raw data and not used as safe_area_insets_pt.")
            gaps.append(f"{rid}: safe-area insets not set. The Simulator launched the app on the {on.get('label')} only (raw, unverified values under secondary_screens[].simulator_measurement); the primary display was never exposed through UIScreen.screens")
        sm = on['simulator_measurement']
        sm['status_bar_height_pt'] = {'portrait': pr['status_bar_height_pt'], 'landscape': ll['status_bar_height_pt']}
        sm['home_indicator'] = bool(pr['home_indicator_present'])
        sm['safe_area_insets_landscape_right_pt'] = lr['safe_area_insets_pt']
    else:
        # no runtime: static device-type data only (Watch, Vision Pro, iPhones/iPads the iOS 27 runtimes no longer support)
        e = entries[0]; st = e['static']; src = f"source: Xcode 27.1 Simulator device type '{e['device_type']}', {os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(st['capabilities_plist']))))} capabilities.plist (static, not booted)"
        sim_stats['static_only'].append(rid)
        d0 = (st['displays'] or [None])[0]
        if fam == 'vision':
            rec['notes'].append(f"Xcode 27.1 Simulator device type '{e['device_type']}' ({st['model_identifier']}) declares a {d0['width_px']}x{d0['height_px']} px @{d0['scale']}x virtual display. That is the Simulator window, not the per-eye panel, so it is not used for resolution_px.")
            return
        if d0:
            px = scr.get('resolution_px')
            sp = {'width': d0['canvas_width_px'] or d0['width_px'], 'height': d0['canvas_height_px'] or d0['height_px']}
            panel = {'width': d0['width_px'], 'height': d0['height_px']}
            sdc = st.get('ScreenDimensionsCapability') or {}
            sdpx = {'width': sdc.get('main-screen-width'), 'height': sdc.get('main-screen-height')}
            if px and panel != px and sp != px and sdpx != px:
                conflicts.append(f"{rid}: Simulator device type '{e['device_type']}' declares {panel['width']}x{panel['height']} px vs Apple {px['width']}x{px['height']} px")
            if fam == 'apple-watch' and px and panel == px and scr.get('logical_resolution_pt') is None and d0['scale'] in (1, 2, 3):
                k = int(d0['scale'])
                if px['width'] % k == 0 and px['height'] % k == 0:
                    scr['logical_resolution_pt'] = {'width': px['width'] // k, 'height': px['height'] // k}; scr['scale'] = k
                    prov['logical_resolution_pt'] = f"derived: Apple pixels / scale @{k}x; scale from {src}"
                    used.add('logical_resolution'); used.add('scale')
            elif fam == 'apple-watch' and px is None:
                gaps.append(f"{rid}: Simulator device type has {panel['width']}x{panel['height']} px but Apple's page does not confirm the pixels; left null")
        cr = st['DeviceCornerRadius']
        if cr is not None:
            scr['corner_radius_pt'] = cr
            prov['corner_radius_pt'] = f"UNOFFICIAL: DeviceCornerRadius key in the Simulator device type ({src}); on the booted iOS 27 device types this key matched the private UIScreen _displayCornerRadius to within 0.34 pt (it differs only for the iPhone 12 family: 47/53 vs 47.33/53.33). Apple does not publish this value"
            used.add('corner_radius (unofficial)')
        if fam in ('iphone', 'ipad', 'ipod-touch'):
            gaps.append(f"{rid}: safe-area insets and measured points not available (a Simulator device type exists but needs an iOS runtime older than the installed 27.0/27.1; see sources/simulator/status.tsv)")
    if used:
        src_ = dict(SIM_SOURCE); src_['used_for'] = sorted(used); rec['sources'].append(src_)

def aspect(w, h):
    f = Fraction(h, w)
    return {'ratio': round(h / w, 4), 'fraction': f'{w // math.gcd(w, h)}:{h // math.gcd(w, h)}'}

def classify(spec, fam, diag_line):
    """Display technology from Apple's own wording on the spec page."""
    f = spec['features']; dl = diag_line or ''
    if f['micro_oled']: return 'micro-OLED'
    if f['tandem_oled']: return 'Tandem OLED'
    if 'OLED' in dl: return 'OLED'
    if re.search(r'mini-LED', dl, re.I): return 'mini-LED'
    return 'LCD'

def rect_diag(spec, marketed):
    notes = spec['rounded_corner_notes']
    if not notes: return None
    n = notes[0]
    pairs = re.findall(r'(\d+(?:\.\d+)?)-inch [A-Za-z ]+? (?:screen )?is (\d+(?:\.\d+)?) inch', n)
    if pairs and marketed:
        for a, b in pairs:
            if abs(float(a) - marketed) < 0.3: return float(b)
    m = re.search(r'(?:screen is|is) (\d+(?:\.\d+)?) inch(?:es)? diagonally|screen is (\d+(?:\.\d+)?) inches|is (\d+(?:\.\d+)?) inches\.', n)
    if m and len(re.findall(r'(\d+(?:\.\d+)?) inch', n)) == 1:
        return float(next(g for g in m.groups() if g))
    nums = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?) inch', n)]
    if marketed:
        best = min(nums, key=lambda x: abs(x - marketed))
        if abs(best - marketed) < 0.3: return best
    return None

devices = []
for c in ALL:
    fam = c['family']
    spec = SPECS.get(c['spec'])
    if spec is None:
        print('MISSING SPEC FILE', c['spec']); continue
    spec['_file'] = c['spec']
    idx = INDEX.get(c['spec'])
    if idx and idx.get('specs_url') and idx['specs_url'] != c['source_url']:
        warnings.append(f"{c['id']}: catalog URL {c['source_url']} != crawled {idx['specs_url']}")
    prov = {}
    sources = [{'url': c['source_url'], 'publisher': 'Apple', 'title': (spec.get('title') or c['name']) + ' - Tech Specs', 'used_for': ['diagonal', 'resolution', 'ppi', 'display_type', 'refresh_rate', 'features']}]
    disp = [x for x in spec['displays'] if x.get('px')]
    scr = {k: None for k in ['diagonal_in', 'diagonal_rect_in', 'resolution_px', 'logical_resolution_pt', 'scale', 'native_scale', 'ppi', 'ppi_computed',
                             'aspect_ratio', 'display_type', 'display_marketing_name', 'refresh_rate_max_hz', 'promotion', 'always_on', 'corner_radius_pt', 'display_area_mm2']}
    secondary = []
    feats = spec['features']
    if fam == 'apple-watch':
        mm = c['case_mm']
        pairs = spec.get('watch_px_area') or []
        # Apple lists larger case first; match by order of sizes in catalog list (same order on page)
        sizes_for_line = [x for x in ALL if x['spec'] == c['spec']]
        pos = [x['case_mm'] for x in sizes_for_line].index(mm)
        px = area = None
        if len(pairs) == len(sizes_for_line):
            px, area = pairs[pos][:2], pairs[pos][2]
        elif len(spec['watch_px']) == len(sizes_for_line):
            wpx = spec['watch_px']
            # Series 1/2 pages list "(38mm)" first: sort by size so larger pixels -> larger case
            wpx_sorted = sorted(wpx, key=lambda p: -p[0]); px = wpx_sorted[pos]
        hig_px = HIG_WATCH.get((c.get('hig_watch'), mm)) if c.get('hig_watch') else None
        if px is None and hig_px:
            px = hig_px; prov['resolution_px'] = 'apple-hig'
            sources.append({'url': HIG_URL, 'publisher': 'Apple', 'title': 'HIG Layout: watchOS device screen dimensions (snapshot 2026-07-02)', 'archive_url': HIG_SNAPSHOT, 'used_for': ['resolution']})
        elif px and hig_px and px != hig_px:
            conflicts.append(f"{c['id']}: spec page pixels {px} vs HIG {hig_px}")
        if px:
            scr['resolution_px'] = {'width': px[0], 'height': px[1]}
            scr['aspect_ratio'] = aspect(*px)
        else:
            gaps.append(f"{c['id']}: pixel resolution not published on the Apple spec page or in the HIG watchOS table")
        scr['display_area_mm2'] = area
        ppis = spec['ppi_mentions']
        scr['ppi'] = ppis[0] if len(ppis) == 1 else None
        scr['display_type'] = 'OLED' if feats['oled'] or feats['ltpo'] else ('OLED' if 'OLED' in open('sources/raw/specs/' + c['spec']).read() else None)
        scr['ltpo'] = feats['ltpo']
        scr['always_on'] = feats['always_on']
        scr['promotion'] = False
        scr['refresh_rate_min_hz'] = 1 if feats['one_hz'] and feats['always_on'] else None
        gaps.append(f"{c['id']}: diagonal not published (Apple gives display area in sq mm); logical points and scale not in the HIG watchOS table (pixels only)")
        if scr['ppi'] is None: gaps.append(f"{c['id']}: ppi not stated on the Apple spec page")
        if area is None: gaps.append(f"{c['id']}: display area not stated on the Apple spec page")
    else:
        main = disp[0] if disp else {}
        if fam == 'iphone' and c['id'] == 'iphone-duo':
            main = disp[0]; secondary_raw = disp[1:]
        else:
            secondary_raw = []
        diag = main.get('diagonal_in')
        marketed = c.get('marketed_diagonal_in')
        if diag is None and spec['actual_diagonal']:
            diag = float(spec['actual_diagonal'][0]); prov['diagonal_in'] = "Apple: 'Actual diagonal screen size is …'"
        if diag is None and marketed:
            diag = float(marketed); prov['diagonal_in'] = 'Apple product name (e.g. "11-inch"); spec page gives only the rectangle measurement'
        scr['diagonal_in'] = diag
        rd = rect_diag(spec, diag)
        if c['id'] == 'iphone-duo': rd = 7.58
        scr['diagonal_rect_in'] = rd
        px = main.get('px')
        if px and fam == 'mac': px = [px[1], px[0]]  # Mac panels are landscape
        if px:
            scr['resolution_px'] = {'width': px[0], 'height': px[1]}
            scr['aspect_ratio'] = aspect(*px)
            dd = rd or diag
            if dd: scr['ppi_computed'] = round(math.hypot(*px) / dd, 1)
        scr['ppi'] = main.get('ppi')
        scr['display_type'] = classify(spec, fam, main.get('line', '') + ' ' + main.get('px_line', ''))
        txt = open([p for p in ['sources/raw/specs/' + c['spec'], 'sources/raw/' + c['spec']] if os.path.exists(p)][0]).read()
        txt = re.sub('[\u2010\u2011\u2012\u2013]', '-', txt).replace('\xa0', ' ')
        if fam in ('iphone', 'ipad') and scr['display_type'] == 'LCD' and re.search(r'OLED', txt): scr['display_type'] = 'OLED'
        if fam == 'mac' and 'Liquid Retina XDR' in txt and scr['display_type'] == 'LCD':
            scr['display_type'] = 'mini-LED'; prov['display_type'] = 'Apple spec page says "Liquid Retina XDR"; mini-LED backlight per Wikipedia cross-check'
        if fam == 'vision':
            scr['display_type'] = 'micro-OLED'
            scr['total_pixels'] = 23_000_000; scr['pixel_pitch_um'] = 7.5
            rates = [int(x) for x in re.findall(r'(\d+)Hz', spec['refresh_rates_line'] or '')]
            scr['refresh_rates_hz'] = rates; scr['refresh_rate_max_hz'] = max(rates) if rates else None
            gaps.append(f"{c['id']}: per-eye resolution, PPI, diagonal and logical size not published by Apple (only '23 million pixels', 7.5 µm pitch)")
        anchor = (main.get('px_line') or '')[:25]
        pos = txt.find(anchor) if anchor else -1
        window = txt[max(0, pos - 700): pos + len(main.get('px_line') or '')] if pos >= 0 else ''
        mks = re.findall(r'(Super Retina XDR|Liquid Retina XDR|Ultra Retina XDR|Liquid Retina|Super Retina HD|Retina HD|5K Retina|4\.5K Retina|Retina)\s+display', window)
        scr['display_marketing_name'] = mks[-1] if mks else None
        scr['promotion'] = feats['promotion'] if fam != 'vision' else None
        if feats['promotion']:
            if re.search(r'ProMotion[^\n]*120\s?Hz', txt): scr['refresh_rate_max_hz'] = 120
            else:
                scr['refresh_rate_max_hz'] = 120; prov['refresh_rate_max_hz'] = 'page says "ProMotion technology" without a number; Apple defines ProMotion as up to 120Hz'
        scr['always_on'] = feats['always_on'] if fam == 'iphone' else None
        for s in secondary_raw:
            sd = {'label': c.get('secondary_label', 'secondary'), 'diagonal_in': s.get('diagonal_in'), 'diagonal_rect_in': 5.36 if c['id'] == 'iphone-duo' else None,
                  'resolution_px': {'width': s['px'][0], 'height': s['px'][1]}, 'ppi': s.get('ppi'), 'aspect_ratio': aspect(*s['px']),
                  'ppi_computed': round(math.hypot(*s['px']) / (5.36 if c['id'] == 'iphone-duo' else s['diagonal_in']), 1),
                  'display_type': 'OLED' if 'OLED' in s.get('line', '') else None, 'display_marketing_name': None, 'logical_resolution_pt': None, 'scale': None, 'native_scale': None,
                  'refresh_rate_max_hz': None, 'promotion': None, 'corner_radius_pt': None}
            gaps.append(f"{c['id']}: {sd['label']} refresh rate not stated per display (spec page lists ProMotion once for both screens)")
            gaps.append(f"{c['id']}: {sd['label']} logical size (points) and scale not published by Apple yet")
            secondary.append(sd)
        # ---- logical points ----
        hig = HIG.get(c.get('hig')) if c.get('hig') else None
        same = HIG.get(c.get('hig_same_panel')) if c.get('hig_same_panel') else None
        if c.get('hig') and not hig: warnings.append(f"{c['id']}: HIG row {c['hig']!r} not found")
        row = hig or same
        if row and px:
            if row['px'] != px:
                conflicts.append(f"{c['id']}: HIG row '{c.get('hig') or c.get('hig_same_panel')}' lists {row['px']} px, spec page {px}")
            scr['logical_resolution_pt'] = {'width': row['pt'][0], 'height': row['pt'][1]}
            scr['scale'] = row['scale']
            if row['pt'][0] * row['scale'] != px[0]:
                scr['native_scale'] = round(px[0] / row['pt'][0], 4)
            prov['logical_resolution_pt'] = 'apple-hig' if hig else f"derived: same panel as HIG row '{c['hig_same_panel']}' (identical pixels and ppi)"
            sources.append({'url': HIG_URL, 'publisher': 'Apple', 'title': f"HIG Layout: device screen dimensions, row '{c.get('hig') or c.get('hig_same_panel')}' (snapshot 2026-07-02)", 'archive_url': HIG_SNAPSHOT, 'used_for': ['logical_resolution', 'scale']})
            if not hig: gaps.append(f"{c['id']}: logical size/scale derived from identical panel ({c['hig_same_panel']}); Apple has not listed this model in the HIG")
        elif c.get('scale_rule') and px:
            k = c['scale_rule']
            scr['logical_resolution_pt'] = {'width': px[0] // k, 'height': px[1] // k}; scr['scale'] = k
            prov['logical_resolution_pt'] = f'derived: @{k}x ({"non-Retina, 163/132 ppi" if k == 1 else "Retina 326 ppi"}); model predates the HIG table'
            gaps.append(f"{c['id']}: logical size derived (@{k}x); not in current HIG table")
        elif fam in ('iphone', 'ipad', 'ipod-touch') and px:
            gaps.append(f"{c['id']}: logical size (points) and scale not published by Apple yet")
        if fam == 'mac' and px:
            gaps.append(f"{c['id']}: default 'looks like' logical resolution and scale not captured (Mac is partial)")
    # ---- CSS ----
    css = {'viewport_width': None, 'viewport_height': None, 'device_pixel_ratio': None}
    lp = scr.get('logical_resolution_pt')
    if lp and fam in ('iphone', 'ipad', 'ipod-touch') and not c.get('mini_conflict'):
        css = {'viewport_width': lp['width'], 'viewport_height': lp['height'], 'device_pixel_ratio': scr['scale']}
        prov['css'] = 'derived: Safari CSS px = UIKit points; devicePixelRatio = scale (portrait, width=device-width)'
    if c.get('mini_conflict'):
        conflicts.append(f"{c['id']}: HIG lists 360x780 pt @3x (= the 1080x2340 panel / 3); bestlatestapps.com/tools/iphone-screen-sizes/ and the runtime UIKit/Safari behaviour it describes use 375x812 @3x rendered at 1125x2436 and downsampled (nativeScale 2.88). CSS viewport left null until verified on a device or Simulator.")
        gaps.append(f"{c['id']}: CSS viewport not set (HIG vs runtime conflict)")
    # ---- identifiers (Wikipedia cross-check) ----
    ids = WIKI.get(c.get('wiki')) if c.get('wiki') else None
    if fam in ('iphone', 'ipad', 'ipod-touch') and not ids:
        gaps.append(f"{c['id']}: model identifiers not found")
    if fam in ('apple-watch', 'mac', 'vision'):
        gaps.append(f"{c['id']}: model identifiers not collected")
    if ids:
        sources.append({'url': WIKI_URLS[fam], 'publisher': 'Wikipedia', 'title': 'Hardware strings (cross-check source)', 'used_for': ['model_identifiers']})
    # ---- safe area & corner radius ----
    if fam in ('iphone', 'ipad', 'ipod-touch'):
        pass  # reported once in gaps summary
    year = c['release_year']
    rec = {
        'id': c['id'], 'name': c['name'], 'family': fam, 'line': c['line'], 'release_year': year,
        'status': c.get('status', 'released'),
        'model_identifiers': ids or [], 'model_identifiers_source': 'wikipedia' if ids else None,
        'screen': scr,
        'secondary_screens': secondary,
        'safe_area_insets_pt': {'portrait': None, 'landscape': None},
        'cutout': c.get('cutout'), 'home_button': c.get('home_button'), 'biometric': c.get('biometric'),
        'css': css,
        'source_url': c['source_url'],
        'sources': sources,
        'provenance': prov,
        'partial': bool(c.get('partial')),
        'notes': c.get('notes', []),
    }
    if fam == 'apple-watch': rec['case_size_mm'] = c['case_mm']
    apply_sim(rec, c)
    # rewrite gap lines that the Simulator data has now closed or qualified
    def _regap(old_prefix, new=None):
        for i, g in enumerate(gaps):
            if g.startswith(f"{c['id']}: {old_prefix}"):
                if new: gaps[i] = f"{c['id']}: {new}"
                else: gaps.pop(i)
                return
    if 'CONFIRMED by Simulator' in prov.get('logical_resolution_pt', ''):
        _regap('logical size/scale derived from identical panel', f"logical size/scale derived from identical panel ({c['hig_same_panel']}) and confirmed in Xcode 27.1 Simulator; Apple has not listed this model in the HIG")
    if fam == 'apple-watch' and scr.get('logical_resolution_pt'):
        _regap('diagonal not published', 'diagonal not published (Apple gives display area in sq mm); points derived from Apple pixels / Simulator device-type scale (not in the HIG watchOS table)')
    if fam in ('iphone', 'ipad') and scr.get('logical_resolution_pt') and prov.get('logical_resolution_pt', '').startswith('measured'):
        _regap('logical size (points) and scale not published by Apple yet', 'logical size (points) and scale not published by Apple; measured in Xcode 27.1 Simulator')
    for s2 in rec['secondary_screens']:
        if s2.get('logical_resolution_pt'):
            _regap(f"{s2['label']} logical size", f"{s2['label']} logical size (points) and scale not published by Apple; measured in Xcode 27.1 Simulator")
    if c.get('mini_conflict') and scr.get('native_scale'):
        lp = scr['logical_resolution_pt']
        rec['css'] = {'viewport_width': lp['width'], 'viewport_height': lp['height'], 'device_pixel_ratio': scr['scale']}
        prov['css'] = 'derived: Safari CSS px = UIKit points (measured UIScreen.bounds); devicePixelRatio = scale (portrait, width=device-width)'
        gaps[:] = [g for g in gaps if g != f"{c['id']}: CSS viewport not set (HIG vs runtime conflict)"]
        conflicts[:] = [x for x in conflicts if not (x.startswith(c['id'] + ': HIG lists 360x780'))]
    if c.get('year_source') == 'wikipedia': prov['release_year'] = 'Wikipedia (Apple spec page has no "Year introduced")'
    devices.append(rec)

meta = {
    'name': 'Apple device screen specs', 'version': '0.1.0', 'generated': '2026-10-27',
    'license': 'CC-BY-4.0', 'attribution': 'Apple device screen specs by bestlatestapps.com (https://bestlatestapps.com/tools/apple-device-screen-sizes/), CC BY 4.0',
    'homepage': 'https://bestlatestapps.com/tools/apple-device-screen-sizes/',
    'count': len(devices),
    'units': {'diagonal_in': 'inches', 'resolution_px': 'physical pixels, portrait', 'logical_resolution_pt': 'points (UIKit/SwiftUI), portrait', 'display_area_mm2': 'square millimetres', 'safe_area_insets_pt': 'points'},
}
os.makedirs('data', exist_ok=True)
json.dump({'meta': meta, 'devices': devices}, open('data/devices.json', 'w'), indent=2, ensure_ascii=False)
json.dump({'meta': meta, 'devices': devices}, open('data/devices.min.json', 'w'), separators=(',', ':'), ensure_ascii=False)

cols = ['id', 'name', 'family', 'line', 'release_year', 'status', 'model_identifiers', 'diagonal_in', 'diagonal_rect_in', 'width_px', 'height_px', 'width_pt', 'height_pt', 'scale', 'native_scale',
        'ppi', 'ppi_computed', 'aspect_ratio', 'aspect_fraction', 'display_type', 'display_marketing_name', 'refresh_rate_max_hz', 'promotion', 'cutout', 'home_button', 'biometric',
        'css_viewport_width', 'css_viewport_height', 'css_device_pixel_ratio', 'display_area_mm2', 'case_size_mm', 'secondary_screens', 'partial', 'source_url']
with open('data/devices.csv', 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(cols)
    for r in devices:
        s = r['screen']; px = s.get('resolution_px') or {}; pt = s.get('logical_resolution_pt') or {}; ar = s.get('aspect_ratio') or {}
        sec = '; '.join(f"{x['label']}: {x['diagonal_in']}in {x['resolution_px']['width']}x{x['resolution_px']['height']} @{x['ppi']}ppi" for x in r['secondary_screens'])
        wr.writerow([r['id'], r['name'], r['family'], r['line'], r['release_year'], r['status'], ' '.join(r['model_identifiers']), s.get('diagonal_in'), s.get('diagonal_rect_in'),
                     px.get('width'), px.get('height'), pt.get('width'), pt.get('height'), s.get('scale'), s.get('native_scale'), s.get('ppi'), s.get('ppi_computed'),
                     ar.get('ratio'), ar.get('fraction'), s.get('display_type'), s.get('display_marketing_name'), s.get('refresh_rate_max_hz'), s.get('promotion'), r['cutout'], r['home_button'], r['biometric'],
                     r['css']['viewport_width'], r['css']['viewport_height'], r['css']['device_pixel_ratio'], s.get('display_area_mm2'), r.get('case_size_mm'), sec, r['partial'], r['source_url']])

os.makedirs('reports', exist_ok=True)
json.dump({'gaps': gaps, 'conflicts': conflicts, 'warnings': warnings}, open('reports/build_report.json', 'w'), indent=1)
from collections import defaultdict
grp = defaultdict(list)
for g in gaps:
    dev, msg = g.split(': ', 1)
    key = re.sub(r'\(.*?\)', '(…)', msg)
    grp[key].append(dev)
with open('reports/gaps.md', 'w') as f:
    f.write('# Gaps (auto-generated by scripts/build_dataset.py)\n\nEvery item below is a field left `null` (or derived and flagged in `provenance`) because no allowed source states it.\n\n')
    nsafe = sum(1 for d in devices if d['safe_area_insets_pt']['portrait']); ncr = sum(1 for d in devices if d['screen']['corner_radius_pt'] is not None)
    f.write('## Simulator coverage (Xcode 27.1, iOS 27.0 / 27.1 runtimes, measured 2026-10-27)\n\n'
            f"- `safe_area_insets_pt`: portrait measured for {nsafe} devices, landscape for {sum(1 for d in devices if d['safe_area_insets_pt']['landscape'])} (iPhones only: iPadOS 27 refused programmatic rotation in its default windowing mode). Key-window safeAreaInsets from scripts/simulator/Measure.swift. Apple does not publish safe areas; devices without a supported Simulator device type stay null and are listed below.\n"
            f"- `corner_radius_pt`: {ncr} devices, all UNOFFICIAL (private UIScreen `_displayCornerRadius` on booted devices, otherwise the `DeviceCornerRadius` key in the device type's capabilities.plist, which matched the runtime value within 0.34 pt on every booted type). Apple does not publish it.\n"
            '- Booted on the iOS 27.x runtimes: ' + str(len(sim_stats['runtime_measured'])) + ' dataset devices. Static device-type data only: ' + str(len(sim_stats['static_only'])) + '. Raw data: sources/simulator/.\n'
            '- No Simulator device type exists for: iPhone 5/5c/5s and older, iPod touch 1st-6th gen, iPad mini (A20 Pro), Apple Watch Series 1 and 1st gen, Apple Vision Pro (M5) (only the original Vision Pro type exists), any Mac.\n'
            '- 60 Hz refresh for non-ProMotion devices: Apple spec pages do not state a refresh rate, so `refresh_rate_max_hz` is null unless ProMotion is listed.\n\n')
    for k, v in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        f.write(f'## {k} ({len(v)})\n\n' + ', '.join(f'`{x}`' for x in v) + '\n\n')
print('devices', len(devices)); print('warnings', *warnings, sep='\n  ')
print('conflicts', len(conflicts), *conflicts, sep='\n  ')
print('simulator: runtime', len(sim_stats['runtime_measured']), 'static-only', len(sim_stats['static_only']), 'radius static/runtime mismatches', sim_stats['radius_static_vs_runtime_mismatch'])
