# Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Anything in `npm run doctor` says FAIL | Missing tool | Run the `→` command it prints, then `npm run setup` again |
| `pangocairo >= 1.30.0 is required` installing Manim | Missing Cairo/Pango (macOS, Linux) | The command from `npm run doctor`, e.g. `sudo apt install libcairo2-dev libpango1.0-dev pkg-config` |
| `Could not start ffmpeg` | FFmpeg not on PATH | Install it (doctor prints how); on Windows open a new terminal afterwards |
| Python version not found | No Python 3.11-3.13 | Install 3.12 (doctor prints how), or set `REELFN_SYSTEM_PYTHON` to its path |
| `Cannot find type definition file for 'node'` | Node packages missing | `npm install`, then `npm run build` |
| `GEMINI_API_KEY is not set` | No key in `.env` | The creator pastes a key into `.env` (never in chat); meanwhile `--voice placeholder` |
| `Gemini free-tier rate limit; retrying` | Per-minute 429 | Wait; it retries up to 5 times |
| `Gemini daily free-tier quota is exhausted` (about 10 requests/day) | Free-tier daily limit | Stop and tell the creator. Options: (1) wait for the reset (the message says when); (2) a paid-tier key; (3) reuse cached beats and change fewer beats; (4) `--voice placeholder` to keep building visuals; (5) the offline Kokoro voice (`renderer/audio/MODELS.md`; a different voice, so ask first) |
| `Gemini TTS could not fit <beat> within the approved beat timing` | Narration too long for the beat | Lengthen the beat or shorten the narration |
| `needs 1.2x time compression, above the 1.15x review limit` (compose) | Same | Same |
| `Narration overlaps or exceeds the episode` | Beat durations too short for speech | Raise durations from the `mix` output |
| `Provider audio is incomplete` / `different episode revision` | Episode edited after voicing | Rerun `voice` (cached beats are reused), then `mix` |
| `Storyboard overran 47.90s by 0.20s` | A play ran past the next cue | Move the cue later or shorten the play |
| `ValueError: zip() argument 2 is shorter...` | Counter faded in together with its tracker animation | Fade in first, animate in a separate play |
| `NameError` for a constant from reel_kit | Not imported | Add it to the `from reel_kit import ...` line |
| Missing or tofu glyphs | Brand font lacks the symbol | Use words or shapes |
| `Unknown theme` / `Brand colours are missing` | Typo in `brand/brand.json` | Pick a file name from `brand/themes/`; see `brand/README.md` |
| Captions use a fallback font | `font.family` does not match the font file's real family name | Use the exact family name shown by your OS font viewer |
| `TODO_LEFT` | Template text still in the episode | Replace every TODO with real content |
| Valid episode but `FAILED_CHECK` | Check disagrees with the claim | Fix the number or the claim, not the check |
| `EARLY_CONCEPT_REVEAL` | Concept named in beat 1-2 | Reveal in the third beat or later, after the mechanism |
| `UNVISUALIZED_CLAIM` | A claim is in no beat | Map it with `claimIds` or remove it |
| `TIMELINE_GAP_OR_OVERLAP` / `TIMELINE_END` | Beat starts or total off | Starts follow the previous end; total equals `durationSeconds` |
| Captions vanish before the voice ends | Narration runs into the end card | End narration at least the end-card length before the total |
| Cannot find the finished MP4 | It is in `output/<name>/` | `npm run reel -- list` shows which reels are built |
| `No reel called ...` | Wrong name or folder | `npm run reel -- list` |
