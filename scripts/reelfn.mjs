#!/usr/bin/env node
// reelfn command line. Works the same on Windows, macOS and Linux.
// Run `node scripts/reelfn.mjs help` (or `npm run reel -- help`) for usage.
import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, delimiter, dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadBrand } from './lib/brand.mjs';
import { doctor, pythonPath, tools } from './lib/doctor.mjs';
import { setup } from './lib/setup.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const STAGES = ['validate', 'voice', 'mix', 'captions', 'render', 'assemble'];

const HELP = `reelfn: narrated, captioned 9:16 explainer videos, made with code.

Usage: npm run reel -- <command> [options]      (or: node scripts/reelfn.mjs <command>)

Getting started
  setup [--local-voice]          Install everything reelfn needs (safe to re-run)
  doctor                         Check your machine and say exactly how to fix anything missing
  brand [init]                   Show your brand, or create brand/brand.json to customise it

Making a reel (<reel> is a folder name in reels/ or examples/, or a path)
  new <name>                     Start a new reel in reels/<name>/
  list                           List your reels and the examples
  build <reel>                   Run every stage below in order
  validate <reel>                Check the script, timeline, sources and every number
  voice <reel>                   Generate narration (Gemini by default; cached per beat)
  mix <reel>                     Lay voice, music and sound cues on the timeline; prints timings
  captions <reel>                Make captions from the narration
  render <reel>                  Animate the scene with Manim
  assemble <reel>                Add captions, watermark and end card; write the final MP4
  frames <reel> [seconds...]     Save a contact sheet of frames for review (default: one per beat)

Options
  --voice gemini|kokoro|placeholder   Narrator for this run (default: from your brand).
                                      "placeholder" is silent: try the pipeline with no API key.
  --version <tag>                     Save as <reel>-<tag>.mp4 instead of overwriting (e.g. v2)

Examples
  npm run reel -- build time-complexity-loops --voice placeholder
  npm run reel -- new black-holes`;

const fail = (message, code = 1) => { console.error(`\n✖ ${message}`); process.exit(code); };

const run = (program, args, env = {}, failure) => {
  const result = spawnSync(program, args, {
    cwd: root, stdio: 'inherit', windowsHide: true, env: { ...process.env, ...env },
  });
  if (result.error) {
    if (result.error.code === 'ENOENT') fail(`Could not start ${program}. Run: npm run doctor`);
    throw result.error;
  }
  if (result.status !== 0) fail(failure ?? `${basename(program)} stopped with exit code ${result.status} (see the message above).`);
};

function parseArgs(argv) {
  const options = { positional: [] };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--voice' || arg === '--version') options[arg.slice(2)] = argv[++i];
    else if (arg.startsWith('--')) options[arg.slice(2)] = true;
    else options.positional.push(arg);
  }
  return options;
}

/** Resolve a reel name or path to its folder, episode and scene. */
function findReel(name) {
  if (!name) fail('Name a reel, for example: npm run reel -- build time-complexity-loops');
  const candidates = [resolve(name), join(root, 'reels', name), join(root, 'examples', name)];
  const dir = candidates.find((path) => existsSync(join(path, 'episode.json')));
  if (!dir) fail(`No reel called "${name}". Run "npm run reel -- list" to see them, or "npm run reel -- new ${name}" to start one.`);
  const scene = join(dir, 'scene.py');
  if (!existsSync(scene)) fail(`${relative(root, dir)} has no scene.py`);
  const sceneClass = readFileSync(scene, 'utf8').match(/^class\s+(\w+)\((?:ReelScene|Scene)\)/m)?.[1];
  if (!sceneClass) fail(`${relative(root, scene)} has no class that extends ReelScene`);
  const slug = basename(dir);
  const out = join(root, 'output', slug);
  return { dir, slug, scene, sceneClass, episode: join(dir, 'episode.json'), out };
}

function stage(step, reel, options) {
  const python = pythonPath(root);
  const { ffmpeg, ffprobe, manim } = tools(root);
  const beats = join(reel.out, 'audio', 'beats');
  const placeholderBeats = join(reel.out, 'audio', 'placeholder-beats');
  const mix = join(reel.out, 'audio', 'mix');
  const srt = join(reel.out, 'captions.srt');
  const name = options.version ? `${reel.slug}-${options.version}` : reel.slug;
  const video = join(reel.out, 'manim', 'videos', 'scene', '960p30', `${name}.mp4`);
  const voice = options.voice ?? loadBrand(root).voice.provider ?? 'gemini';
  const providerDir = voice === 'placeholder' ? placeholderBeats : beats;
  console.log(`\n▶ ${step} ${reel.slug}`);
  switch (step) {
    case 'validate':
      run(process.execPath, [join(root, 'node_modules', 'typescript', 'bin', 'tsc')]);
      run(process.execPath, [join(root, 'dist', 'src', 'cli.js'), 'validate', reel.episode], {}, 'Fix the problems listed above, then validate again.');
      break;
    case 'voice':
      if (voice === 'gemini') {
        console.log('Gemini narration: only new or changed beats use quota; verified cached beats are reused.');
        run(process.execPath, [join(root, 'renderer', 'audio', 'gemini.mjs'), reel.episode, beats]);
      } else if (voice === 'kokoro') run(python, [join(root, 'renderer', 'audio', 'local_voice.py'), reel.episode, beats]);
      else if (voice === 'placeholder') run(python, [join(root, 'renderer', 'audio', 'placeholder.py'), reel.episode, placeholderBeats]);
      else fail(`Unknown voice "${voice}". Use gemini, kokoro or placeholder.`);
      break;
    case 'mix':
      run(python, [join(root, 'renderer', 'audio', 'compose.py'), '--episode', reel.episode, '--provider-dir', providerDir, '--out', mix, '--ffmpeg', ffmpeg]);
      run(python, [join(root, 'scripts', 'measure_speech.py'), mix]);
      break;
    case 'captions':
      run(python, [join(root, 'renderer', 'audio', 'captions.py'), '--episode', reel.episode, '--audio-manifest', join(mix, 'audio-manifest.json'), '--out', srt]);
      break;
    case 'render': {
      // The scene is copied to a fixed name so Manim's output path is predictable.
      mkdirSync(reel.out, { recursive: true });
      const staged = join(reel.out, 'scene.py');
      copyFileSync(reel.scene, staged);
      const pythonPathEnv = [join(root, 'renderer', 'manim'), join(root, 'renderer'), reel.dir].join(delimiter);
      run(manim, ['-qh', '-v', 'WARNING', '--media_dir', join(reel.out, 'manim'), staged, reel.sceneClass, '-o', `${name}.mp4`], { PYTHONPATH: pythonPathEnv });
      break;
    }
    case 'assemble':
      run(python, [join(root, 'renderer', 'assemble.py'), '--video', video, '--audio', join(mix, 'mix.wav'), '--captions', srt,
        '--out', join(reel.out, `${name}.mp4`), '--ffmpeg', ffmpeg, '--ffprobe', ffprobe]);
      console.log(`\n✔ Your video: ${relative(root, join(reel.out, `${name}.mp4`))}`);
      if (voice === 'placeholder') console.log('  (Silent placeholder voice: a preview only. Run with the real voice before sharing.)');
      break;
  }
}

function frames(reel, times, options) {
  const brand = loadBrand(root);
  const episode = JSON.parse(readFileSync(reel.episode, 'utf8'));
  const name = options.version ? `${reel.slug}-${options.version}` : reel.slug;
  const video = join(reel.out, `${name}.mp4`);
  if (!existsSync(video)) fail(`Build the reel first: npm run reel -- build ${reel.slug}`);
  const endCard = brand.endCard.kind === 'none' ? 0 : Number(brand.endCard.seconds ?? 0);
  const picks = times.length ? times : [
    ...episode.beats.map((beat) => (beat.start + beat.duration / 2).toFixed(2)),
    ...(endCard ? [(episode.durationSeconds - endCard + 0.8).toFixed(2)] : []),
  ];
  run(process.execPath, [join(root, 'scripts', 'review-frames.mjs'), video, join(reel.out, 'review'), ...picks]);
}

function newReel(name) {
  if (!name || !/^[a-z][a-z0-9-]*$/.test(name)) fail('Give the reel a short lowercase name with dashes, for example: npm run reel -- new black-holes');
  const dir = join(root, 'reels', name);
  if (existsSync(dir)) fail(`reels/${name} already exists.`);
  mkdirSync(dir, { recursive: true });
  const template = join(root, 'templates', 'reel');
  const className = name.split('-').map((part) => part[0].toUpperCase() + part.slice(1)).join('') + 'Reel';
  for (const file of readdirSync(template)) {
    const text = readFileSync(join(template, file), 'utf8').replaceAll('__SLUG__', name).replaceAll('__CLASS__', className);
    writeFileSync(join(dir, file), text);
  }
  console.log(`✔ Created reels/${name}/ with episode.json, scene.py and release.md.`);
  console.log('  Next: fill in episode.json (or ask your AI agent to), then: npm run reel -- validate ' + name);
}

function list() {
  for (const folder of ['reels', 'examples']) {
    const dir = join(root, folder);
    const reels = existsSync(dir) ? readdirSync(dir).filter((name) => existsSync(join(dir, name, 'episode.json'))) : [];
    console.log(`${folder}/`);
    if (!reels.length) console.log(folder === 'reels' ? '  (none yet: npm run reel -- new <name>)' : '  (none)');
    for (const name of reels) {
      const episode = JSON.parse(readFileSync(join(dir, name, 'episode.json'), 'utf8'));
      const built = existsSync(join(root, 'output', name, `${name}.mp4`)) ? '  ✔ built' : '';
      console.log(`  ${name.padEnd(28)} ${String(episode.durationSeconds ?? '?').padStart(4)} s  ${episode.question ?? ''}${built}`);
    }
  }
}

function brandCommand(sub) {
  const target = join(root, 'brand', 'brand.json');
  if (sub === 'init') {
    if (existsSync(target)) fail('brand/brand.json already exists. Edit it directly.');
    copyFileSync(join(root, 'brand', 'brand.example.json'), target);
    console.log('✔ Created brand/brand.json. Edit the name, colours and voice, and drop your logo files into brand/assets/ (see brand/README.md).');
    return;
  }
  const brand = loadBrand(root);
  const describe = (mark) => mark.kind === 'image' ? `image ${relative(root, mark.path)}` : mark.kind === 'text' ? `text "${mark.text}"` : 'none';
  console.log(`Brand file:  ${brand.configured ? 'brand/brand.json' : 'not created yet (using neutral defaults; run: npm run reel -- brand init)'}`);
  console.log(`Name:        ${brand.name || '(none)'}`);
  console.log(`Theme:       ${brand.theme}  (background ${brand.colors.background}, text ${brand.colors.textPrimary})`);
  console.log(`Font:        ${brand.font.family}`);
  console.log(`Watermark:   ${describe(brand.watermark)}`);
  console.log(`End card:    ${describe(brand.endCard)}${brand.endCard.kind === 'none' ? '' : `, ${brand.endCard.seconds} s`}`);
  console.log(`Voice:       ${brand.voice.provider} / ${brand.voice.voice} (${brand.voice.language})`);
}

const [command, ...rest] = process.argv.slice(2);
const options = parseArgs(rest);
switch (command) {
  case undefined: case 'help': case '--help': case '-h': console.log(HELP); break;
  case 'setup': await setup(root, options); break;
  case 'doctor': process.exitCode = doctor(root) ? 0 : 1; break;
  case 'brand': brandCommand(options.positional[0]); break;
  case 'new': newReel(options.positional[0]); break;
  case 'list': list(); break;
  case 'frames': frames(findReel(options.positional[0]), options.positional.slice(1), options); break;
  case 'build': {
    const reel = findReel(options.positional[0]);
    for (const step of STAGES) stage(step, reel, options);
    break;
  }
  default:
    if (STAGES.includes(command)) stage(command, findReel(options.positional[0]), options);
    else fail(`Unknown command "${command}". Run: npm run reel -- help`, 2);
}
