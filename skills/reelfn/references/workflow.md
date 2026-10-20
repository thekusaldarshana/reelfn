# Workflow: one request to a finished MP4

Every command runs from the repository root, the same way on Windows, macOS and Linux:

```text
npm run reel -- <stage> <name> [--voice gemini|kokoro|placeholder] [--version v2]
```

`<name>` is a folder in `reels/` (the creator's) or `examples/`. Stages: `validate`, `voice`, `mix`, `captions`,
`render`, `assemble`, or `build` (all of them in order). Outputs go to `output/<name>/` (git-ignored).

## 0-3. Preflight, intake, evidence, episode
1. `npm run doctor` (fix FAILs, see [[first-run]]).
2. Ask the open decisions in one batch ([[asking]]).
3. `npm run reel -- new <name>` creates `reels/<name>/` with `episode.json`, `scene.py` and `release.md`.
   Research and write the episode ([[episodes]]); `npm run reel -- validate <name>` until it prints `Valid episode`.
   Start with generous, equal provisional beat durations (e.g. 14 s each): they only need to fit the voice.

## 4. Voice first, then fit the timeline (the main time-saver)
```text
npm run reel -- voice <name>   # Gemini by default; verified cached beats are reused, changed beats cost quota
npm run reel -- mix <name>     # prints each beat's speech span, a suggested duration, and the pauses
```
- Pauses of 0.2 s or more mark sentence and clause boundaries. Map each spoken phrase to a time: that is your cue sheet.
- Set each beat's `duration` to about speech + 0.12 lead + 0.27 tail + 0.8 s for visuals (`mix` suggests it).
  Beats must start where the last ended; the total must equal `durationSeconds`.
- Keep the last narration end at least the end-card length (default 2 s) before the total: the end card hides captions.
- Narration runs about 1.9-2.2 words per second. A beat with too little speech leaves dead air; add content, not padding.
- After editing durations: `validate`, `voice` (cached), `mix` again. Only beats whose words changed are re-voiced.
- No key or no quota? `--voice placeholder` times silent beats at 2.1 words/s so you can keep building; re-voice later.

## 5. Scene
Edit `reels/<name>/scene.py` (from the template), import `reel_kit` ([[scenes]]), one method per beat with absolute
cues from the cue sheet. The first frame shows the situation; no title card.

## 6. Build
```text
npm run reel -- render <name>     # Manim; raises "Storyboard overran" if a cue was missed: fix the timeline
npm run reel -- captions <name>   # SRT from the narration timings
npm run reel -- assemble <name>   # captions + watermark + end card + probe + inspection -> output/<name>/<name>.mp4
```
Use `--version v2` (and so on) for a new take without overwriting the last one.

## 7. Review loop
```text
npm run reel -- frames <name> [seconds...]   # default: the middle of every beat plus the end card
```
It prints the path of a tiled contact sheet; open it with your image viewer tool. Look for overlap, text touching
panel edges, anything under the watermark (upper right) or caption lane, missing glyphs, and visuals that do not match
what is being said. Fix, then `render` and `assemble` again. Details in [[review]].

## 8-9. Copy and delivery ([[release]])
Fill `reels/<name>/release.md`; give the creator the MP4 (send the file if your harness can) and the final message.

## Reference timings (64 s reel, a laptop-class machine)
Voice 1-2 min (more if rate-limited) · mix 5 s · render 20-60 s · assemble 10 s · review a few minutes.
