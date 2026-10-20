# How reelfn works

reelfn turns a written, fact-checked script into a vertical video using code only. An AI coding agent (or you)
writes two files per reel; deterministic tools do everything else.

```
reels/<name>/episode.json ──validate──▶ checked script (timeline, sources, numbers)
        │
        ├─voice──▶ one WAV per beat (Gemini / Kokoro / silent placeholder), cached by text + voice
        ├─mix────▶ voice + generated music + sound cues on the timeline; prints measured speech timings
        ├─captions▶ SRT, word-timed within each spoken beat
        │
reels/<name>/scene.py ──render──▶ Manim animation, 540x960 at 30 fps, cued to the measured timings
        │
        └─assemble▶ FFmpeg: captions + watermark + end card (from your brand) → MP4
                    + probe, contact sheet, inspection report and a manifest of SHA-256 hashes
```

## Why it is built this way

- **Code, not a video model.** Every frame is reproducible, editable and free of hallucinated visuals.
- **Voice first.** Narration is generated and measured before animating, so visuals land on the spoken words.
- **Truth is checked, not trusted.** Claims need verbatim evidence or a deterministic check the validator recomputes.
- **Gates stay human.** The pipeline produces previews. Approving a script or a final file (bound to its hash) and
  publishing are always the creator's decisions.
- **Personal things stay personal.** Brand, logos, keys and reels live in git-ignored files, so updating reelfn
  never touches them and they never leak into a pull request.

## Files a build produces (`output/<name>/`)

| File | What it is |
| --- | --- |
| `<name>.mp4` | The video |
| `<name>.manifest.json` | Hashes of every input and the output; approvals refer to `outputSha256` |
| `<name>-contact-sheet.png`, `<name>-inspection.json` | 12 evenly spaced frames and technical checks |
| `audio/`, `captions.srt`, `manim/` | Intermediate files, reused between runs (voice audio is the costly part) |
| `review/sheet.png` | The sheet from `npm run reel -- frames <name>` |

## Brand resolution

`brand/default.json` ← `brand/themes/<theme>.json` (colours) ← `brand/brand.json` (yours). The watermark and end card
use an image from `brand/assets/` if present, otherwise your `name` as text, otherwise nothing. The same rules are
implemented in `renderer/brand.py` and `scripts/lib/brand.mjs`.

## Roadmap ideas

- An `npx`-installable command and a desktop-friendly launcher, so no clone is needed.
- More narrators (OpenAI, ElevenLabs, Azure, Piper) behind the same beat-WAV interface.
- More aspect ratios (1:1, 16:9) and resolutions (1080x1920).
- A local review studio in the browser for approving scripts and final videos.
- A library of reusable scene components (graphs, equations, maps, timelines).
