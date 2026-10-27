#!/usr/bin/env node
// Validate data/devices.json against schema/device.schema.json plus sanity rules.
// Usage: node scripts/validate.mjs [path/to/devices.json]
import { readFileSync } from 'node:fs';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';

const file = process.argv[2] || new URL('../data/devices.json', import.meta.url);
const data = JSON.parse(readFileSync(file, 'utf8'));
const schema = JSON.parse(readFileSync(new URL('../schema/device.schema.json', import.meta.url), 'utf8'));
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const errors = [], warnings = [];
if (!ajv.validate(schema, data)) for (const e of ajv.errors) errors.push(`schema ${e.instancePath} ${e.message} ${JSON.stringify(e.params)}`);

const PPI_TOL_RECT = 0.02;   // vs Apple's rectangle diagonal
const PPI_TOL_MARKETED = 0.03; // vs the rounded marketing diagonal
const ids = new Set(), identifiers = new Map();
const byFamily = {};
const coverage = { resolution_px: 0, logical_resolution_pt: 0, ppi: 0, diagonal_in: 0, css: 0, model_identifiers: 0, safe_area: 0, corner_radius: 0 };

function checkScreen(dev, s, label) {
  const tag = `${dev.id}${label ? ' [' + label + ']' : ''}`;
  const px = s.resolution_px, pt = s.logical_resolution_pt;
  if (pt && !s.scale) errors.push(`${tag}: logical size without scale`);
  if (pt && px && s.scale) {
    const dims = dev.family === 'mac' ? [] : [['width', 'width'], ['height', 'height']];
    for (const [a] of dims) {
      const viaScale = pt[a] * s.scale;
      if (s.native_scale == null) {
        if (viaScale !== px[a]) errors.push(`${tag}: ${a} ${pt[a]}pt x @${s.scale} = ${viaScale} != ${px[a]}px and no native_scale`);
      } else {
        if (!(s.native_scale < s.scale)) errors.push(`${tag}: native_scale ${s.native_scale} should be < scale ${s.scale}`);
        if (Math.abs(pt[a] * s.native_scale - px[a]) > 1.5) errors.push(`${tag}: ${a} ${pt[a]}pt x native ${s.native_scale} = ${(pt[a] * s.native_scale).toFixed(1)} != ${px[a]}px`);
      }
    }
  }
  if (px && s.aspect_ratio) {
    const r = px.height / px.width;
    if (Math.abs(r - s.aspect_ratio.ratio) > 0.001) errors.push(`${tag}: aspect_ratio ${s.aspect_ratio.ratio} != ${r.toFixed(4)}`);
    const [fw, fh] = s.aspect_ratio.fraction.split(':').map(Number);
    if (Math.abs(fh / fw - r) > 1e-9) errors.push(`${tag}: aspect fraction ${s.aspect_ratio.fraction} does not match pixels`);
  }
  if (px && s.ppi && (s.diagonal_in || s.diagonal_rect_in)) {
    const diag = s.diagonal_rect_in || s.diagonal_in;
    const calc = Math.hypot(px.width, px.height) / diag;
    const tol = s.diagonal_rect_in ? PPI_TOL_RECT : PPI_TOL_MARKETED;
    const dev_ = Math.abs(calc - s.ppi) / s.ppi;
    if (dev_ > tol) errors.push(`${tag}: ppi ${s.ppi} vs computed ${calc.toFixed(1)} from ${diag}in (${(dev_ * 100).toFixed(1)}% > ${tol * 100}%)`);
    if (s.ppi_computed != null && Math.abs(s.ppi_computed - calc) > 0.15) errors.push(`${tag}: ppi_computed ${s.ppi_computed} != ${calc.toFixed(1)}`);
  }
  if (s.diagonal_rect_in && s.diagonal_in && s.diagonal_rect_in > s.diagonal_in + 0.15) errors.push(`${tag}: rectangle diagonal ${s.diagonal_rect_in} larger than marketed ${s.diagonal_in}`);
  if (s.promotion === true && s.refresh_rate_max_hz !== 120) errors.push(`${tag}: ProMotion without 120 Hz`);
}

for (const d of data.devices || []) {
  if (ids.has(d.id)) errors.push(`duplicate id ${d.id}`); ids.add(d.id);
  for (const mi of d.model_identifiers || []) {
    if (identifiers.has(mi)) errors.push(`model identifier ${mi} used by ${identifiers.get(mi)} and ${d.id}`);
    identifiers.set(mi, d.id);
  }
  if (!(d.sources || []).some(s => s.publisher === 'Apple')) errors.push(`${d.id}: no Apple source`);
  if (!(d.sources || []).some(s => s.url === d.source_url)) errors.push(`${d.id}: source_url not listed in sources`);
  checkScreen(d, d.screen);
  for (const s of d.secondary_screens || []) checkScreen(d, s, s.label);
  const s = d.screen, css = d.css;
  if (css.viewport_width != null) {
    if (!s.logical_resolution_pt || css.viewport_width !== s.logical_resolution_pt.width || css.viewport_height !== s.logical_resolution_pt.height)
      errors.push(`${d.id}: CSS viewport ${css.viewport_width}x${css.viewport_height} != points`);
    if (css.device_pixel_ratio !== s.scale) errors.push(`${d.id}: devicePixelRatio ${css.device_pixel_ratio} != scale ${s.scale}`);
  }
  if (d.cutout === 'dynamic-island' && d.home_button) errors.push(`${d.id}: Dynamic Island and home button`);
  if (d.biometric === 'face-id' && d.home_button) errors.push(`${d.id}: Face ID with home button`);
  if (d.release_year > Number((data.meta.generated || '9999').slice(0, 4))) errors.push(`${d.id}: release_year in the future`);
  byFamily[d.family] = (byFamily[d.family] || 0) + 1;
  if (s.resolution_px) coverage.resolution_px++;
  if (s.logical_resolution_pt) coverage.logical_resolution_pt++;
  if (s.ppi) coverage.ppi++;
  if (s.diagonal_in) coverage.diagonal_in++;
  if (css.viewport_width) coverage.css++;
  if (d.model_identifiers.length) coverage.model_identifiers++;
  if (d.safe_area_insets_pt.portrait) coverage.safe_area++;
  if (s.corner_radius_pt != null) coverage.corner_radius++;
}
if (data.meta && data.meta.count !== (data.devices || []).length) errors.push(`meta.count ${data.meta.count} != ${data.devices.length}`);

const total = (data.devices || []).length;
console.log(`devices: ${total}`);
console.log('by family:', Object.entries(byFamily).map(([k, v]) => `${k}=${v}`).join(', '));
console.log('field coverage:', Object.entries(coverage).map(([k, v]) => `${k} ${v}/${total}`).join(', '));
for (const w of warnings) console.log('WARN', w);
if (errors.length) { for (const e of errors) console.error('ERROR', e); console.error(`\n${errors.length} error(s)`); process.exit(1); }
console.log('OK: schema valid, ids unique, pixels = points x scale, PPI consistent with diagonal, CSS = points');
