# Apple Device Screen Specs

An open, source-linked dataset of the screen specs of **every iPhone, iPad, iPod touch and Apple Watch**, with partial coverage of Mac built-in displays and Apple Vision Pro. Each value is tied to an Apple Tech Specs page or the Apple Human Interface Guidelines, or was measured in the Xcode Simulator (safe areas and corner radius, which Apple doesn't publish). Anything Apple hasn't published is left `null` and listed in [`reports/gaps.md`](reports/gaps.md). Nothing is guessed.

Maintained by **[bestlatestapps.com](https://bestlatestapps.com/)**. You can browse every device in the [Apple device screen sizes](https://bestlatestapps.com/tools/apple-device-screen-sizes/) table, or just iPhones in the [iPhone screen sizes tool](https://bestlatestapps.com/tools/iphone-screen-sizes/).

| Family | Records |
|---|---|
| iPhone | 55 |
| iPad | 46 |
| iPod touch | 7 |
| Apple Watch | 36 (20 models × case sizes) |
| Mac (partial) | 29 |
| Apple Vision Pro (partial) | 2 |
| **Total** | **175** |

Data version 0.1.0, generated 2026-10-27. It covers devices up to iPhone 18 Pro / iPhone Duo, Apple Watch Series 12 / Ultra 4 and iPad mini (A20 Pro).

## Why another screen-size list?

- **Sourced.** Each record has a `source_url` pointing at Apple. A `sources[]` array says which source each field group came from, and `provenance` flags every derived value.
- **Honest about gaps.** Values Apple doesn't publish stay `null`. Other lists fill these in by guessing.
- **Validated.** A JSON Schema and `npm run validate` check that pixels = points × scale (or native scale), that PPI matches the diagonal, that ids are unique, and more.
- **Developer formats.** Pretty and minified JSON, CSV, and CSS viewport plus `devicePixelRatio` for web developers.

## Usage

### Fetch (jsDelivr CDN, from GitHub)

```js
const url = "https://cdn.jsdelivr.net/gh/aryansbtloe/apple-device-screen-specs@main/data/devices.min.json";
const { devices } = await fetch(url).then(r => r.json());

const iphone = devices.find(d => d.id === "iphone-16-pro");
console.log(iphone.screen.logical_resolution_pt); // { width: 402, height: 874 }
console.log(iphone.css);                          // { viewport_width: 402, viewport_height: 874, device_pixel_ratio: 3 }
```

To get a stable, cacheable URL, pin a tag instead of `@main`, for example `@v0.1.0`. For example, `https://cdn.jsdelivr.net/gh/aryansbtloe/apple-device-screen-specs@v0.1.0/data/devices.json`.

### Static JSON API

The same data is served from bestlatestapps.com with CORS enabled and no key:

- `https://bestlatestapps.com/api/devices.json` (all devices, pretty-printed)
- `https://bestlatestapps.com/api/devices.min.json` (all devices, minified)
- `https://bestlatestapps.com/api/devices.csv` (CSV)
- `https://bestlatestapps.com/api/devices/<id>.json` (one device, for example `iphone-15.json`)

```js
const res = await fetch('https://bestlatestapps.com/api/devices/iphone-15.json');
const device = await res.json();
```

### npm (planned)

```bash
npm install apple-device-screen-specs   # planned package name
```

```js
import data from "apple-device-screen-specs/data/devices.json" with { type: "json" };
```

### CSV

[`data/devices.csv`](data/devices.csv) has one row per device and can be opened in a spreadsheet. Nested fields are flattened, and secondary screens are JSON-encoded.

### Examples

```js
// All iPhones with a Dynamic Island, newest first
devices.filter(d => d.family === "iphone" && d.cutout === "dynamic-island")
       .sort((a, b) => b.release_year - a.release_year);

// Unique CSS viewports for responsive testing
[...new Set(devices.filter(d => d.css).map(d => `${d.css.viewport_width}x${d.css.viewport_height}@${d.css.device_pixel_ratio}`))];
```

## Field reference

Top level: `{ meta, devices[] }`. `meta` holds `version`, `generated`, `count`, `license`, `attribution` and `units`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable slug, e.g. `iphone-16-pro` or `apple-watch-series-10-46mm` |
| `name` | string | Apple's product name |
| `family` | enum | `iphone`, `ipad`, `ipod-touch`, `apple-watch`, `mac`, `vision` |
| `line` | string | Product line, e.g. "iPhone Pro" or "iPad Air" |
| `release_year` | int | Year introduced |
| `status` | enum | `released` or `announced` |
| `model_identifiers` | string[] | e.g. `iPhone17,1`. Cross-checked from Wikipedia (`model_identifiers_source`) |
| `screen.diagonal_in` | number | Apple's marketed diagonal in inches (measured as a rectangle) |
| `screen.diagonal_rect_in` | number | Diagonal computed from pixels ÷ PPI |
| `screen.resolution_px` | `{width,height}` | Physical pixels. Portrait for iPhone, iPad, iPod and Watch, landscape for Mac |
| `screen.logical_resolution_pt` | `{width,height}` | Points (UIKit/SwiftUI `UIScreen.bounds`), portrait |
| `screen.scale` | 1, 2 or 3 | `UIScreen.scale` (@1x/@2x/@3x) |
| `screen.native_scale` | number or null | Set only when the panel is downsampled (e.g. Plus models: 2.608) |
| `screen.ppi` | int | Pixels per inch as stated by Apple |
| `screen.ppi_computed` | number | √(w²+h²) ÷ diagonal, as a sanity check |
| `screen.aspect_ratio` | `{ratio,fraction}` | Long side ÷ short side, plus the reduced fraction |
| `screen.display_type` | enum | `LCD`, `OLED`, `Tandem OLED`, `mini-LED`, `micro-OLED` |
| `screen.display_marketing_name` | string | e.g. "Super Retina XDR" or "Liquid Retina" |
| `screen.refresh_rate_max_hz` | int or null | 120 for ProMotion. Null when Apple doesn't state a rate |
| `screen.promotion`, `screen.always_on` | bool | Features from the spec page |
| `screen.corner_radius_pt` | number or null | **Unofficial.** Display corner radius measured in the Xcode 27.1 Simulator for 103 devices. Apple doesn't publish it; null elsewhere |
| `screen.display_area_mm2` | number | Apple Watch display area |
| `secondary_screens[]` | object[] | Extra displays, e.g. the iPhone Duo cover screen |
| `safe_area_insets_pt.portrait` / `.landscape` | `{top,right,bottom,left}` or null | Key-window `safeAreaInsets` measured in the Xcode 27.1 Simulator: portrait for 56 devices, landscape for 33 (iPhones only). Null where no Simulator device type exists, and for iPad landscape |
| `cutout` | enum | `none`, `notch`, `dynamic-island` |
| `home_button` | bool | Physical or solid-state Home button |
| `biometric` | enum or null | `face-id`, `touch-id`, `optic-id`, or null (none or not applicable) |
| `css.viewport_width/height`, `css.device_pixel_ratio` | number | Safari CSS px with `width=device-width`, in portrait |
| `source_url` | url | Primary Apple source |
| `sources[]` | object[] | `{url, publisher, title, used_for[], archive_url?}` |
| `provenance` | object | Field → how the value was derived (only for values not read directly) |
| `partial` | bool | `true` when the record intentionally covers only some fields (Mac, Vision) |
| `notes` | string[] | Caveats and conflicts |

The full JSON Schema (draft 2020-12) is in [`schema/device.schema.json`](schema/device.schema.json).

## Sources and method

1. **Apple Tech Specs** (support.apple.com, plus apple.com for current products) for the diagonal, pixels, PPI, display technology, ProMotion and display area.
2. **Apple Human Interface Guidelines, Layout** for points and scale. Apple removed the device tables from the live page on 2026-09-09, so this project uses the [Wayback snapshot of 2026-07-02](https://web.archive.org/web/20260702060104/https://developer.apple.com/tutorials/data/design/human-interface-guidelines/layout.json).
3. **Wikipedia**, only as a cross-check and for model identifiers. These values are flagged.
4. **Xcode 27.1 Simulator** (iOS 27.0 runtime; iOS 27.1 for iPhone Duo), measured 2026-10-27 with a small probe app ([`scripts/simulator/Measure.swift`](scripts/simulator/Measure.swift), run by `scripts/simulator/run_all.sh`). It logs `UIScreen` bounds, `nativeBounds`, `scale` and `nativeScale`, plus key-window safe-area insets in portrait and landscape. It was used to:
   - record **safe-area insets**: 56 devices in portrait and 33 in landscape. Landscape covers iPhones only, because iPadOS 27 refused programmatic rotation in its default windowing mode.
   - record **corner radius** for 103 devices. These values are **unofficial**: they come from the private `UIScreen` `_displayCornerRadius`, or from the device type's `DeviceCornerRadius` capability when the device wasn't booted.
   - confirm points and scale where the HIG table is missing or wrong.

   Raw output is in [`sources/simulator/`](sources/simulator/). Simulator pixel density is never used for `ppi`.

**Finding: iPhone 12 mini and 13 mini.** The HIG (snapshot 2026-07-02) lists them as 360×780 pt @3x. In the Simulator, `UIScreen.main.bounds` is **375×812 pt** with `scale` 3, `nativeScale` **2.88** and `nativeBounds` 1080×2340 px. The device renders a 1125×2436 canvas and downsamples it to the 1080×2340 panel, so 360×780 is just the panel divided by 3. The dataset uses 375×812 pt with `native_scale` 2.88. This was measured at the default (Standard) display zoom only, and not checked on physical hardware. See [`reports/conflicts.md`](reports/conflicts.md) #1.

Known source conflicts are documented in [`reports/conflicts.md`](reports/conflicts.md), and the remaining gaps in [`reports/gaps.md`](reports/gaps.md).

## Build and validate

```bash
npm install
npm run build      # python3 scripts/build_dataset.py -> data/*.json, data/devices.csv, reports/
npm run validate   # node scripts/validate.mjs
```

The validator checks:
- the JSON Schema
- unique `id` and model identifiers
- that pixels = points × scale, or match `native_scale`
- PPI against the diagonal (±2% rectangle, ±3% marketed)
- aspect ratio
- that ProMotion means 120 Hz
- that CSS = points and DPR = scale
- no Face ID or Dynamic Island alongside a Home button
- no future release years
- that `meta.count` matches

## License and attribution

- **Data** (`data/`): [CC BY 4.0](LICENSE-DATA)
- **Code** (`scripts/`, `schema/`): [MIT](LICENSE)

If you use the data, please credit it like this:

> Apple device screen specs by [bestlatestapps.com](https://bestlatestapps.com/tools/apple-device-screen-sizes/), CC BY 4.0

Device specifications are Apple's published facts. This project is not affiliated with Apple Inc.

## Contributing

Corrections are welcome. Every change must cite an **Apple** source: a Tech Specs page, the HIG, or developer documentation. Values measured in the Xcode Simulator are accepted with the Xcode and runtime versions noted.

1. Edit `scripts/catalog.py`, or the parser if a new Apple page format breaks it.
2. Run `npm run build && npm run validate`.
3. Open a PR that includes the Apple URL. Do not submit values copied from third-party size sites.

Data that would most help right now:
- **iPad landscape safe-area insets**
- **points for the iPhone Duo's inner display**
- **Apple Watch model identifiers**
- **physical-device confirmation** of the iPhone 12/13 mini values (375×812 pt, `nativeScale` 2.88), including Display Zoom
