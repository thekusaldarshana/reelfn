#!/usr/bin/env node
// Validate every shipped example episode (used by `npm run check` and CI).
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { validateEpisode } = await import(pathToFileURL(join(root, 'dist', 'src', 'episode.js')).href);
let failed = false;
for (const name of readdirSync(join(root, 'examples')).filter((entry) => existsSync(join(root, 'examples', entry, 'episode.json')))) {
  const result = validateEpisode(JSON.parse(readFileSync(join(root, 'examples', name, 'episode.json'), 'utf8')));
  console.log(`${result.valid ? 'OK  ' : 'FAIL'} examples/${name}`);
  for (const issue of result.issues) console.log(`     ${issue.code} ${issue.path ?? ''}: ${issue.message}`);
  failed ||= !result.valid;
}
process.exitCode = failed ? 1 : 0;
