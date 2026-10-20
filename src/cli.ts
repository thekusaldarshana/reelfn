import { readFile } from 'node:fs/promises';
import { validateEpisode } from './episode.js';

const [command, path] = process.argv.slice(2);
if (command !== 'validate' || !path) {
  console.error('Usage: node dist/src/cli.js validate <episode.json>');
  process.exitCode = 2;
} else {
  try {
    const result = validateEpisode(JSON.parse(await readFile(path, 'utf8')));
    if (result.valid) console.log(`Valid episode: ${result.episode?.slug}`);
    else {
      for (const issue of result.issues) console.error(`${issue.code} ${issue.path ?? ''}: ${issue.message}`);
      console.error(`\n${result.issues.length} problem(s). Codes are explained in skills/reelfn/references/troubleshooting.md`);
      process.exitCode = 1;
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
