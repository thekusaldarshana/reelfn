// One-command, re-runnable setup: Node packages, TypeScript build, Python environment, a .env file.
// System tools (Python, FFmpeg, and Manim's Cairo/Pango libraries on macOS/Linux) are not installed
// silently: we say exactly which command to run, because it may need an administrator password.
import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { doctor, installHint, PYTHON_VERSIONS, pythonPath, works } from './doctor.mjs';

const windows = process.platform === 'win32';

const step = (title) => console.log(`\n▶ ${title}`);
const stop = (message, fix) => {
  console.error(`\n✖ ${message}`);
  if (fix) console.error(`  Fix: ${fix}\n  Then run "npm run setup" again.`);
  process.exit(1);
};
const exec = (program, args, cwd) => spawnSync(program, args, { cwd, stdio: 'inherit', windowsHide: true }).status === 0;

/** Find a supported Python 3 interpreter as [program, ...prefixArgs]. */
function findPython() {
  const candidates = [];
  if (process.env.REELFN_SYSTEM_PYTHON) candidates.push([process.env.REELFN_SYSTEM_PYTHON]);
  for (const version of PYTHON_VERSIONS) candidates.push(windows ? ['py', `-${version}`] : [`python${version}`]);
  candidates.push(windows ? ['python'] : ['python3']);
  for (const [program, ...prefix] of candidates) {
    const result = spawnSync(program, [...prefix, '-c', 'import sys; print("%d.%d" % sys.version_info[:2])'], { encoding: 'utf8', windowsHide: true });
    const version = result.status === 0 ? result.stdout.trim() : '';
    if (PYTHON_VERSIONS.includes(version)) return { program, prefix, version };
  }
  return null;
}

export async function setup(root, options) {
  console.log('reelfn setup: this can take 5-10 minutes the first time.');

  step('Node packages');
  const npm = process.env.npm_execpath;
  if (!existsSync(join(root, 'node_modules', 'zod'))) {
    const ok = npm ? exec(process.execPath, [npm, 'install', '--no-audit', '--no-fund'], root)
      : exec(windows ? 'npm.cmd' : 'npm', ['install', '--no-audit', '--no-fund'], root);
    if (!ok) stop('npm install failed.', 'check your internet connection, then retry');
  } else console.log('already installed');
  if (!exec(process.execPath, [join(root, 'node_modules', 'typescript', 'bin', 'tsc')], root)) stop('TypeScript build failed.');

  step('Python');
  const python = findPython();
  if (!python) stop(`Python ${PYTHON_VERSIONS.join(' / ')} was not found.`, installHint.python);
  console.log(`using Python ${python.version}`);

  step('Python environment (.venv): Manim, audio tools');
  const venvPython = pythonPath(root);
  if (!works(venvPython)) {
    if (!exec(python.program, [...python.prefix, '-m', 'venv', join(root, '.venv')], root)) {
      stop('Could not create the Python environment.', windows ? installHint.python : 'sudo apt install python3-venv   (or reinstall Python)');
    }
  }
  exec(venvPython, ['-m', 'pip', 'install', '--quiet', '--upgrade', 'pip'], root);
  // Exact pins first (reproducible). If a pin has no wheel for this Python/OS, fall back to the
  // compatible top-level requirements so a new machine still gets a working install.
  let installed = exec(venvPython, ['-m', 'pip', 'install', '--quiet', '-r', join(root, 'requirements.lock')], root);
  if (!installed) {
    console.log('Exact versions did not install here; trying compatible versions instead.');
    installed = exec(venvPython, ['-m', 'pip', 'install', '--quiet', '-r', join(root, 'requirements.in')], root);
  }
  if (!installed) {
    stop('Installing Manim failed. On macOS and Linux it needs the Cairo and Pango libraries.',
      installHint.manimSystem || 'install the "Microsoft C++ Build Tools", or use Python 3.12');
  }
  if (options['local-voice']) {
    step('Offline voice (Kokoro)');
    if (!exec(venvPython, ['-m', 'pip', 'install', '--quiet', '-r', join(root, 'requirements-local-voice.lock')], root)) {
      stop('Installing the offline voice failed.', 'see renderer/audio/MODELS.md');
    }
    console.log('Now download the model files listed in renderer/audio/MODELS.md.');
  }

  step('Settings');
  if (!existsSync(join(root, '.env'))) {
    copyFileSync(join(root, '.env.example'), join(root, '.env'));
    console.log('created .env: paste your GEMINI_API_KEY there when you have one');
  } else console.log('.env already exists (left unchanged)');

  console.log('');
  if (!doctor(root)) process.exitCode = 1;
}
