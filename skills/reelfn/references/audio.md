# Audio

The narrator comes from `voice` in `brand/brand.json`:

| Provider | Use | Needs |
| --- | --- | --- |
| `gemini` (default) | The real narrator | `GEMINI_API_KEY` in `.env`; free tier about 10 requests a day |
| `kokoro` | Offline narrator (experimental) | `npm run setup -- --local-voice` and model files (`renderer/audio/MODELS.md`) |
| `placeholder` | Silent timing preview; never final | Nothing |

Choose per run with `--voice <provider>`. Gemini voices are named (for example Puck, Kore, Charon); `voice.style` is a
plain-English direction applied to every beat, and `delivery.geminiStyle` adds direction to a single beat.

Keep approved narration verbatim while varying emphasis and pauses by beat. If a beat's audio is longer than its
duration, the narrator retakes it faster once; the mixer may then compress by at most 1.15x, otherwise lengthen the
beat or shorten the words. Music and cues are generated deterministically under the speech.

Captions use word-proportional timing within each beat: a good approximation that still needs a sync check.
Pipeline: `renderer/audio/gemini.mjs` | `local_voice.py` | `placeholder.py` → `compose.py` (mix) → `captions.py`.
