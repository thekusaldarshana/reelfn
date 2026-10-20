// Machine checks shared by `doctor` and `setup`. Every failure says how to fix it on this OS.
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { loadBrand } from './brand.mjs';

export const MIN_NODE = 22;
export const PYTHON_VERSIONS = ['3.12', '3.13', '3.11'];
const windows = process.platform === 'win32';
const mac = process.platform === 'darwin';

const venvBin = (root, name) => join(root, '.venv', windows ? 'Scripts' : 'bin', name + (windows ? '.exe' : ''));
export const pythonPath = (root) => process.env.REELFN_PYTHON || venvBin(root, 'python');
export const tools = (root) => ({
  manim: process.env.REELFN_MANIM || venvBin(root, 'manim'),
  ffmpeg: process.env.REELFN_FFMPEG || 'ffmpeg',
  ffprobe: process.env.REELFN_FFPROBE || 'ffprobe',
});

export const works = (program, args = ['--version'], cwd) =>
  spawnSync(program, args, { cwd, encoding: 'utf8', windowsHide: true }).status === 0;

export const installHint = {
  node: windows ? 'winget install OpenJS.NodeJS.LTS' : mac ? 'brew install node' : 'https://nodejs.org/en/download (or your package manager)',
  python: windows ? 'winget install Python.Python.3.12' : mac ? 'brew install python@3.12'
    : 'sudo apt install python3.12 python3.12-venv python3.12-dev   (Fedora: sudo dnf install python3.12-devel)',
  ffmpeg: windows ? 'winget install Gyan.FFmpeg   (then open a new terminal)' : mac ? 'brew install ffmpeg' : 'sudo apt install ffmpeg   (Fedora: sudo dnf install ffmpeg)',
  manimSystem: windows ? '' : mac ? 'brew install pkg-config cairo pango'
    : 'sudo apt install build-essential pkg-config libcairo2-dev libpango1.0-dev   (Fedora: sudo dnf install cairo-devel pango-devel)',
};

export function hasGeminiKey(root) {
  if (process.env.GEMINI_API_KEY?.trim()) return true;
  const envFile = join(root, '.env');
  return existsSync(envFile) && /^\s*GEMINI_API_KEY\s*=\s*[^\s#]+/m.test(readFileSync(envFile, 'utf8'));
}

/** Print a checklist. Returns true when everything required is present. */
export function doctor(root) {
  let ok = true;
  const line = (state, text, fix) => {
    console.log(`${state.padEnd(4)} ${text}`);
    if (fix && state !== 'OK') console.log(`     → ${fix}`);
    if (state === 'FAIL') ok = false;
  };
  const { manim, ffmpeg, ffprobe } = tools(root);
  console.log('reelfn doctor\n');
  line(Number(process.versions.node.split('.')[0]) >= MIN_NODE ? 'OK' : 'FAIL', `Node.js ${process.version} (need ${MIN_NODE} or newer)`, installHint.node);
  line(existsSync(join(root, 'node_modules', 'zod')) ? 'OK' : 'FAIL', 'Node packages', 'npm install');
  line(works(pythonPath(root)) ? 'OK' : 'FAIL', 'Python environment (.venv)', 'npm run setup');
  line(works(manim) ? 'OK' : 'FAIL', 'Manim (animation)', 'npm run setup');
  line(works(ffmpeg, ['-version']) ? 'OK' : 'FAIL', 'FFmpeg', installHint.ffmpeg);
  line(works(ffprobe, ['-version']) ? 'OK' : 'FAIL', 'FFprobe (comes with FFmpeg)', installHint.ffmpeg);
  try {
    const brand = loadBrand(root);
    line(existsSync(join(root, brand.font.file)) ? 'OK' : 'FAIL', `Font: ${brand.font.family}`, `Check "font.file" in brand/brand.json`);
    const marks = [brand.watermark.kind, brand.endCard.kind];
    line(brand.configured ? 'OK' : 'INFO', brand.configured ? `Brand: ${brand.name || '(no name)'} (watermark: ${marks[0]}, end card: ${marks[1]})`
      : 'Brand: neutral defaults, no watermark or end card', 'npm run reel -- brand init   (or ask your AI agent: "set up my brand")');
  } catch (error) {
    line('FAIL', `Brand settings: ${error.message}`, 'Fix brand/brand.json (see brand/README.md)');
  }
  line(hasGeminiKey(root) ? 'OK' : 'WARN', `GEMINI_API_KEY ${hasGeminiKey(root) ? 'is set (value hidden)' : 'is not set: needed for the real narrator voice'}`,
    'Get a free key at https://aistudio.google.com/apikey and paste it into .env. Until then, use --voice placeholder.');
  console.log(ok ? '\nAll set. Try: npm run reel -- build time-complexity-loops --voice placeholder' : '\nFix the FAIL lines above, then run: npm run doctor');
  return ok;
}
