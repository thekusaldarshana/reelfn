// Gemini TTS narrator. The validated episode supplies the verbatim text; the voice comes from your brand.
// Usage: node renderer/audio/gemini.mjs <episode.json> <out-dir>
// Credentials are loaded locally and never written to artifacts or logs.
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadBrand } from '../../scripts/lib/brand.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
try { process.loadEnvFile(resolve(root, '.env')); }
catch (error) { if (error?.code !== 'ENOENT') throw error; }
const key = process.env.GEMINI_API_KEY;
if (!key) {
  console.error('GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey and put it in .env (see .env.example).');
  console.error('No key yet? Preview the whole video with a silent placeholder voice: add --voice placeholder');
  process.exit(1);
}

const [episodeArg, outArg] = process.argv.slice(2);
if (!episodeArg || !outArg) throw new Error('Usage: node renderer/audio/gemini.mjs <episode.json> <out-dir>');
const episodePath = resolve(episodeArg);
const outDir = resolve(outArg);
const episode = JSON.parse(await readFile(episodePath, 'utf8'));
const voiceProfile = loadBrand(root).voice;
const model = voiceProfile.model;
const voice = voiceProfile.voice;
const style = voiceProfile.style;
const episodeSha256 = createHash('sha256').update(await readFile(episodePath)).digest('hex');
const sha256 = (data) => createHash('sha256').update(data).digest('hex');
const maxAttempts = Number(process.env.GEMINI_MAX_ATTEMPTS ?? 5);
if (!Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts > 5) throw new Error('GEMINI_MAX_ATTEMPTS must be an integer from 1 to 5');

await mkdir(outDir, { recursive: true });
const manifestPath = resolve(outDir, 'provider-manifest.json');
let cached = null;
try { cached = JSON.parse(await readFile(manifestPath, 'utf8')); }
catch { /* No cache yet. */ }

const writeManifest = async (files, complete) => writeFile(manifestPath, JSON.stringify({
  provider: 'gemini', model, voice, style, language: voiceProfile.language,
  episodeSha256, complete, files,
}, null, 2) + '\n');

const results = [];
for (const beat of episode.beats) {
  const beatStyle = `${style} ${beat.delivery?.geminiStyle ?? ''}`.trim();
  const targetSeconds = (Number(beat.duration) - 0.27) * 1.15;
  const fastStyle = `${beatStyle} Deliver this exact text naturally within ${Math.max(1, Number(beat.duration) - 0.4).toFixed(1)} seconds. Keep every word, but use a brisk conversational pace and shorter pauses.`;
  const inputHash = (deliveryStyle) => sha256(JSON.stringify({ model, voice, beatStyle: deliveryStyle, narration: beat.narration }));
  const wavSeconds = (wav) => {
    const channels = wav.readUInt16LE(22);
    const rate = wav.readUInt32LE(24);
    const bits = wav.readUInt16LE(34);
    if (channels !== 1 || rate !== 24000 || bits !== 16) throw new Error(`Unexpected Gemini WAV format for ${beat.id}`);
    return (wav.length - 44) / (rate * channels * bits / 8);
  };
  const previous = cached?.files?.find((entry) => entry.id === beat.id && [inputHash(beatStyle), inputHash(fastStyle)].includes(entry.inputSha256));
  if (previous) {
    try {
      const wav = await readFile(resolve(outDir, `${beat.id}.wav`));
      if (sha256(wav) === previous.sha256 && wavSeconds(wav) <= targetSeconds) {
        results.push(previous);
        console.log(`Reusing verified ${beat.id} voice audio`);
        continue;
      }
    } catch { /* Regenerate a missing or changed file. */ }
  }
  let response;
  let retake = Boolean(previous);
  let wav;
  let inputSha256;
  for (let deliveryAttempt = 0; deliveryAttempt < 2; deliveryAttempt++) {
    const deliveryStyle = retake ? fastStyle : beatStyle;
    inputSha256 = inputHash(deliveryStyle);
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
    response = await fetch('https://generativelanguage.googleapis.com/v1beta/interactions', {
      method: 'POST',
      headers: { 'x-goog-api-key': key, 'content-type': 'application/json' },
      body: JSON.stringify({
        model,
        input: [{
          type: 'user_input',
          content: [{
            type: 'text',
            text: beat.narration,
            annotations: [{ type: 'speech_metadata', style: deliveryStyle }],
          }],
        }],
        response_format: { type: 'audio' },
        generation_config: { speech_config: [{ voice }] },
      }),
      signal: AbortSignal.timeout(90_000),
    });
    if (response.status !== 429 || attempt === maxAttempts - 1) break;
    let rateMessage = '';
    try {
      const errorBody = await response.json();
      rateMessage = errorBody.error?.message ?? '';
    } catch { /* Retry using the response status alone. */ }
    if (/requests per day|daily quota/i.test(rateMessage)) {
      throw new Error(`Gemini daily free-tier quota is exhausted for ${model}: ${rateMessage}`);
    }
    const retryAfter = Number(response.headers.get('retry-after'));
    const delaySeconds = Number.isFinite(retryAfter) && retryAfter > 0 ? Math.min(retryAfter, 60) : 20;
    console.log(`Gemini free-tier rate limit; retrying ${beat.id} in ${delaySeconds}s`);
    await new Promise((done) => setTimeout(done, delaySeconds * 1000));
    }
    if (!response.ok) {
    let message = response.statusText;
    try {
      const errorBody = await response.json();
      message = errorBody.error?.message ?? message;
    } catch { /* Keep status text; do not print raw response bodies. */ }
      throw new Error(`Gemini TTS failed for ${beat.id}: HTTP ${response.status}: ${message}`);
    }
    const body = await response.json();
    const blocks = (body.steps ?? []).flatMap((step) => step.content ?? []);
    const audioBlock = blocks.filter((block) => block.type === 'audio' && block.data).at(-1);
    if (!audioBlock) throw new Error(`Gemini TTS returned no audio for ${beat.id}`);
    wav = Buffer.from(audioBlock.data, 'base64');
    if (wav.length < 44 || wav.toString('ascii', 0, 4) !== 'RIFF' || wav.toString('ascii', 8, 12) !== 'WAVE') {
      throw new Error(`Gemini TTS returned invalid WAV data for ${beat.id}`);
    }
    if (wavSeconds(wav) <= targetSeconds) break;
    console.log(`Retaking ${beat.id}: ${wavSeconds(wav).toFixed(2)}s exceeds its ${beat.duration}s beat`);
    retake = true;
    wav = undefined;
  }
  if (!wav) throw new Error(`Gemini TTS could not fit ${beat.id} within the approved beat timing`);
  const path = resolve(outDir, `${beat.id}.wav`);
  await writeFile(path, wav);
  results.push({ id: beat.id, path, sha256: sha256(wav), inputSha256, bytes: wav.length });
  await writeManifest(results, false);
  console.log(`Saved ${beat.id} voice audio (${wav.length} bytes)`);
}

await writeManifest(results, true);
