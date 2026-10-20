import assert from 'node:assert/strict';
import { cpSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { loadBrand, merge } from '../scripts/lib/brand.mjs';

const repo = fileURLToPath(new URL('..', import.meta.url));

function sandbox(userBrand, files = []) {
  const root = mkdtempSync(join(tmpdir(), 'reelfn-brand-'));
  cpSync(join(repo, 'brand', 'default.json'), join(root, 'brand', 'default.json'), { recursive: true });
  cpSync(join(repo, 'brand', 'themes'), join(root, 'brand', 'themes'), { recursive: true });
  if (userBrand) writeFileSync(join(root, 'brand', 'brand.json'), JSON.stringify(userBrand));
  for (const file of files) {
    mkdirSync(join(root, file, '..'), { recursive: true });
    writeFileSync(join(root, file), 'png');
  }
  return root;
}

test('deep merge keeps defaults the user did not override', () => {
  assert.deepEqual(merge({ a: { b: 1, c: 2 }, d: [1] }, { a: { c: 3 }, d: [2] }), { a: { b: 1, c: 3 }, d: [2] });
});

test('with no brand.json the video is unbranded and uses the default theme', () => {
  const root = sandbox();
  try {
    const brand = loadBrand(root);
    assert.equal(brand.configured, false);
    assert.equal(brand.watermark.kind, 'none');
    assert.equal(brand.endCard.kind, 'none');
    assert.match(brand.colors.background, /^#[0-9A-F]{6}$/i);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('a name alone gives text marks; an uploaded image wins over text', () => {
  const root = sandbox({ name: 'Science Corner', theme: 'paper', colors: { accent: '#123456' } }, ['brand/assets/logo.png']);
  try {
    const brand = loadBrand(root);
    assert.equal(brand.configured, true);
    assert.deepEqual([brand.watermark.kind, brand.watermark.text], ['text', 'Science Corner']);
    assert.equal(brand.endCard.kind, 'image');
    assert.equal(brand.colors.accent, '#123456');
    assert.equal(brand.colors.background, '#F7F5F0');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('an unknown theme is a clear error', () => {
  const root = sandbox({ theme: 'neon' });
  try { assert.throws(() => loadBrand(root), /Unknown theme 'neon'/); }
  finally { rmSync(root, { recursive: true, force: true }); }
});
