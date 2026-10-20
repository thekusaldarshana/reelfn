// Resolve the active brand. Keep this in step with renderer/brand.py (same rules, same files).
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const REQUIRED_COLORS = ['background', 'surface', 'border', 'textPrimary', 'textSecondary', 'textMuted'];
const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);

export function merge(base, override) {
  const merged = { ...base };
  for (const [key, value] of Object.entries(override)) {
    merged[key] = isObject(value) && isObject(merged[key]) ? merge(merged[key], value) : value;
  }
  return merged;
}

const read = (path) => {
  try { return JSON.parse(readFileSync(path, 'utf8')); }
  catch (error) { throw new Error(`${path} is not valid JSON: ${error.message}`); }
};

const mark = (root, section, name) => {
  if (section.image && existsSync(join(root, section.image))) return { ...section, kind: 'image', path: join(root, section.image) };
  const text = (section.text || name || '').trim();
  return text ? { ...section, kind: 'text', text } : { ...section, kind: 'none' };
};

export function loadBrand(root) {
  const dir = join(root, 'brand');
  const userFile = join(dir, 'brand.json');
  let brand = read(join(dir, 'default.json'));
  if (existsSync(userFile)) brand = merge(brand, read(userFile));
  const themeFile = join(dir, 'themes', `${brand.theme || 'midnight'}.json`);
  if (!existsSync(themeFile)) throw new Error(`Unknown theme '${brand.theme}': pick one in brand/themes/`);
  brand.colors = { ...read(themeFile).colors, ...brand.colors };
  const missing = REQUIRED_COLORS.filter((key) => !(key in brand.colors));
  if (missing.length) throw new Error(`Brand colours are missing: ${missing.join(', ')}`);
  const name = (brand.name || '').trim();
  brand.watermark = mark(root, brand.watermark, name);
  brand.endCard = mark(root, brand.endCard, name);
  brand.configured = existsSync(userFile);
  return brand;
}
