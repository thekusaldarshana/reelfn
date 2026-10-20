#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [video, directory, ...times] = process.argv.slice(2);
if (!video || !directory || !times.length) {
  console.error('Usage: node scripts/review-frames.mjs <video.mp4> <outdir> <t1> <t2> ...');
  process.exit(2);
}
const out = resolve(directory);
const ffmpeg = process.env.REELFN_FFMPEG || 'ffmpeg';
const run = (args) => {
  const result = spawnSync(ffmpeg, ['-loglevel', 'error', '-y', ...args], { cwd: root, stdio: 'inherit', windowsHide: true });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`FFmpeg exited ${result.status}`);
};
mkdirSync(out, { recursive: true });
const frames = times.map((time, i) => join(out, `f_${String(i).padStart(2, '0')}.png`));
for (let i = 0; i < frames.length; i++) {
  rmSync(frames[i], { force: true });
  run(['-ss', times[i], '-i', resolve(video), '-frames:v', '1', frames[i]]);
}
const cols = Math.min(6, frames.length);
const rows = Math.ceil(frames.length / cols);
run(['-framerate', '1', '-i', join(out, 'f_%02d.png'), '-filter_complex', `tile=${cols}x${rows}`, '-frames:v', '1', join(out, 'sheet.png')]);
console.log(join(out, 'sheet.png'));
