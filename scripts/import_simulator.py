#!/usr/bin/env python3
"""Normalise Xcode Simulator measurements into sources/simulator/measurements.json + summary.csv.

Inputs (all copied verbatim from the Mac run, see scripts/simulator/run_all.sh):
  sources/simulator/raw/<slug>.json          probe-app output (scripts/simulator/Measure.swift), one per device type
  sources/simulator/status.tsv               per device type: name, type id, OK/UNSUPPORTED/NO_OUTPUT, udid, runtime
  sources/simulator/devicetype_profiles.json static data from each .simdevicetype bundle (profile.plist + capabilities.plist)
  sources/simulator/chrome.json              DeviceKit chrome.json outline data (bezel art only, not the display)
Output is keyed by dataset id. build_dataset.py reads measurements.json; nothing here edits data/ directly."""
import json, os, re, csv, sys
sys.path.insert(0, os.path.dirname(__file__))
from catalog import ALL
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(ROOT, 'sources/simulator')
XCODE = 'Xcode 27.1 (27A9275)'
RUNTIME_NAMES = {'com.apple.CoreSimulator.SimRuntime.iOS-27-0': 'iOS 27.0 (24A434)', 'com.apple.CoreSimulator.SimRuntime.iOS-27-1': 'iOS 27.1 (24A94425)'}

def slug(name):
    s = re.sub(r'[^A-Za-z0-9]', '-', name + '\n'); s = re.sub(r'-{2,}', '-', s); return s.rstrip('-')

profiles = json.load(open(os.path.join(SIM, 'devicetype_profiles.json')))
status = {}
for line in open(os.path.join(SIM, 'status.tsv')):
    f = line.rstrip('\n').split('\t')
    status[f[0]] = {'type_id': f[1], 'status': f[2], 'detail': f[3] if len(f) > 3 else '', 'runtime': f[4] if len(f) > 4 else None}

# dataset ids by model identifier (iPhone/iPad/iPod), by name pattern for Watch/Vision
# same identifier source as build_dataset.py (catalog 'wiki' key -> sources/wikipedia_identifiers.json)
WIKI = {}
for page, rws in json.load(open(os.path.join(ROOT, 'sources/wikipedia_identifiers.json'))).items():
    for r in rws: WIKI.setdefault(r['name'], r['identifiers'])
by_ident = {}
for c in ALL:
    for mi in (WIKI.get(c.get('wiki')) or []) if c.get('wiki') else []: by_ident[mi] = c['id']
ids = {c['id'] for c in ALL}

def watch_id(name):
    m = re.match(r'Apple Watch (.+?) \((\d+)mm\)(?: \((\w+) generation\))?$', name)
    if not m: return None
    line, mm, gen = m.groups()
    line = line.lower()
    if line == 'se': base = f"se-{gen or '1st'}-generation"
    elif line == 'se 3': base = 'se-3rd-generation'
    else: base = line.replace(' ', '-')
    i = f'apple-watch-{base}-{mm}mm'
    return i if i in ids else None

def rnd(x):
    return None if x is None else (int(x) if float(x).is_integer() else round(float(x), 4))

def static_of(p):
    disp = [x for x in p.get('displays', []) if x.get('displayType') == 'integrated']
    sd = p.get('ScreenDimensionsCapability') or {}
    return {
        'device_type': p['name'], 'device_type_id': p['identifier'], 'model_identifier': p['profile_keys'].get('modelIdentifier'),
        'chrome_identifier': p['profile_keys'].get('chromeIdentifier'),
        'min_runtime': p.get('minRuntime'), 'max_runtime': p.get('maxRuntime'),
        'capabilities_plist': p['capabilities_path'],
        'ScreenDimensionsCapability': {k: rnd(v) for k, v in sd.items()} or None,
        'DeviceCornerRadius': rnd(p.get('DeviceCornerRadius')),
        'displays': [{'name': x.get('displayName'), 'width_px': rnd(x.get('width')), 'height_px': rnd(x.get('height')),
                      'canvas_width_px': rnd(x.get('canvasWidth')), 'canvas_height_px': rnd(x.get('canvasHeight')),
                      'scale': rnd(x.get('scale')), 'hdpi': rnd(x.get('hdpi')), 'vdpi': rnd(x.get('vdpi')),
                      'corner_radius': {k: rnd(x.get('cornerRadius' + k)) for k in ('UL', 'UR', 'LL', 'LR')},
                      'native_rotation': x.get('nativeRotation')} for x in disp],
    }

def ins(d): return {k: rnd(d[k]) for k in ('top', 'right', 'bottom', 'left')}

def runtime_of(raw, st):
    ms = raw['main_screen']
    out = {
        'runtime': RUNTIME_NAMES.get(st['runtime'], st['runtime']), 'system_version': raw.get('system_version'),
        'simulator_model_identifier': raw.get('simulator_model_identifier'),
        'bounds_pt': {'width': rnd(ms['bounds_pt']['width']), 'height': rnd(ms['bounds_pt']['height'])},
        'native_bounds_px': {'width': rnd(ms['native_bounds_px']['width']), 'height': rnd(ms['native_bounds_px']['height'])},
        'scale': rnd(ms['scale']), 'native_scale': rnd(ms['native_scale']), 'max_fps': ms.get('max_fps'),
        'display_corner_radius_unofficial': rnd(ms.get('display_corner_radius_unofficial')),
        'screens': [{'bounds_pt': {'width': rnd(s['bounds_pt']['width']), 'height': rnd(s['bounds_pt']['height'])},
                     'native_bounds_px': {'width': rnd(s['native_bounds_px']['width']), 'height': rnd(s['native_bounds_px']['height'])},
                     'scale': rnd(s['scale']), 'native_scale': rnd(s['native_scale']),
                     'display_corner_radius_unofficial': rnd(s.get('display_corner_radius_unofficial'))} for s in raw.get('uiscreen_screens_at_end', raw.get('uiscreen_screens', []))],
        'scene_roles': raw.get('scene_roles_requested'),
    }
    for key in ('portrait', 'landscape_left', 'landscape_right'):
        s = raw.get(key) or {}
        out[key] = {'interface_orientation': s.get('interface_orientation'),
                    'window_pt': {'width': rnd(s['window_frame_pt']['width']), 'height': rnd(s['window_frame_pt']['height'])} if s.get('window_frame_pt') else None,
                    'safe_area_insets_pt': ins(s['window_safe_area_insets_pt']) if s.get('window_safe_area_insets_pt') else None,
                    'status_bar_height_pt': rnd(s.get('status_bar_height_pt')), 'home_indicator_present': s.get('home_indicator_present'),
                    'geometry_error': raw.get(f'{key}_geometry_error')}
        exp = {'portrait': 'portrait', 'landscape_left': 'landscapeLeft', 'landscape_right': 'landscapeRight'}[key]
        out[key]['rotation_ok'] = s.get('interface_orientation') == exp
        w = out[key]['window_pt']; b = out['bounds_pt']
        out[key]['window_is_full_screen'] = bool(w) and sorted([w['width'], w['height']]) == sorted([b['width'], b['height']])
    return out

result, rows, unmeasured = {}, [], []
for p in profiles:
    fam = p['productFamily']
    if fam not in ('iPhone', 'iPad', 'Apple Watch', 'Apple Vision'): continue
    mi = p['profile_keys'].get('modelIdentifier')
    if fam in ('iPhone', 'iPad'):
        did = by_ident.get(mi)
    elif fam == 'Apple Watch':
        did = watch_id(p['name'])
    else:
        did = 'apple-vision-pro' if mi == 'RealityDevice14,1' else None
    st = status.get(p['name'], {'status': 'NOT_RUN' if fam in ('iPhone', 'iPad') else 'STATIC_ONLY', 'runtime': None, 'detail': ''})
    raw_path = os.path.join(SIM, 'raw', slug(p['name']) + '.json')
    rt = runtime_of(json.load(open(raw_path)), st) if st['status'] == 'OK' and os.path.exists(raw_path) else None
    entry = {'device_type': p['name'], 'status': st['status'], 'detail': st.get('detail') if st['status'] != 'OK' else None,
             'raw_file': os.path.relpath(raw_path, ROOT) if rt else None, 'static': static_of(p), 'runtime': rt}
    if did is None:
        unmeasured.append({'device_type': p['name'], 'reason': f'no dataset record matches model identifier {mi}'}); continue
    result.setdefault(did, []).append(entry)
    r = rt or {}
    pr = r.get('portrait') or {}; ll = r.get('landscape_left') or {}; lr = r.get('landscape_right') or {}
    sdisp = (entry['static']['displays'] or [{}])[0]
    def i4(x): return '/'.join(str(x[k]) for k in ('top', 'right', 'bottom', 'left')) if x else ''
    rows.append({'dataset_id': did, 'device_type': p['name'], 'model_identifier': mi, 'status': st['status'], 'runtime': r.get('runtime') or '',
                 'static_width_px': sdisp.get('width_px'), 'static_height_px': sdisp.get('height_px'), 'static_scale': sdisp.get('scale'), 'static_hdpi': sdisp.get('hdpi'),
                 'static_DeviceCornerRadius': entry['static']['DeviceCornerRadius'],
                 'bounds_w_pt': (r.get('bounds_pt') or {}).get('width'), 'bounds_h_pt': (r.get('bounds_pt') or {}).get('height'),
                 'native_w_px': (r.get('native_bounds_px') or {}).get('width'), 'native_h_px': (r.get('native_bounds_px') or {}).get('height'),
                 'scale': r.get('scale'), 'native_scale': r.get('native_scale'),
                 'safe_portrait_trbl': i4(pr.get('safe_area_insets_pt')), 'safe_landscape_left_trbl': i4(ll.get('safe_area_insets_pt')), 'safe_landscape_right_trbl': i4(lr.get('safe_area_insets_pt')),
                 'status_bar_portrait_pt': pr.get('status_bar_height_pt'), 'home_indicator': pr.get('home_indicator_present'),
                 'corner_radius_unofficial': r.get('display_corner_radius_unofficial'), 'screens': len(r.get('screens') or []),
                 'rotation_ok': all(x.get('rotation_ok') for x in (pr, ll, lr)) if rt else '', 'full_screen': all(x.get('window_is_full_screen') for x in (pr, ll, lr)) if rt else ''})

meta = {'xcode': XCODE, 'runtimes': list(RUNTIME_NAMES.values()), 'measured_on': '2026-10-27',
        'method': 'scripts/simulator/Measure.swift (scene-based UIKit app built with swiftc) run on throwaway simulators via scripts/simulator/run_all.sh; static data read from /Library/Developer/CoreSimulator/Profiles/DeviceTypes/*.simdevicetype/Contents/Resources/{profile,capabilities}.plist',
        'notes': ['profile.plist has no mainScreen* keys in Xcode 27.1; the screen keys live in the sibling capabilities.plist (ScreenDimensionsCapability, displays[], DeviceCornerRadius).',
                  'DeviceKit chrome.json (/Library/Developer/DeviceKit/Chrome/*.devicechrome) only describes the bezel artwork outline (simpleOutsideBorder.cornerRadiusX/Y), not the display corner radius.',
                  'display_corner_radius_unofficial comes from the private UIScreen _displayCornerRadius key: UNOFFICIAL.'],
        'unmatched_device_types': unmeasured}
json.dump({'meta': meta, 'devices': result}, open(os.path.join(SIM, 'measurements.json'), 'w'), indent=1, ensure_ascii=False)
with open(os.path.join(SIM, 'summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('dataset ids with simulator data:', len(result), '| device types:', len(rows), '| unmatched:', len(unmeasured))
for u in unmeasured: print('  unmatched', u)
