# Scenes: authoring the animation

`npm run reel -- new <name>` gives you `reels/<name>/scene.py` from the template. Real examples to read:
`examples/time-complexity-loops/scene.py` (code, tables, counters, focus/dim) and `examples/time-complexity-45/scene.py`
(race bars, halving cells, growth curves). Shared helpers live in `renderer/manim/reel_kit.py`; import them, do not copy.
Helper modules placed next to `scene.py` can be imported too.

## reel_kit API
- Brand: `COLORS` (background, surface, surfaceRaised, border, textPrimary/Strong/Secondary/Tertiary/Muted, accent), `FONT`,
  `MONO`, all from the creator's brand. Never hard-code a colour or font: the same scene must work in every theme, light or dark.
- Text: `label(text, size, color, width)` auto-shrinks to `width`; `left(item, y)` / `right(item, y)` pin to the 7 unit column.
- `counter(tracker, y, size, suffix)`: a right-aligned number that follows a `ValueTracker` (thousands separators).
- `CodeBlock(lines, y, size=30)`: quiet panel + monospace lines (indent kept). `.focus(i, j)` brightens those lines and dims
  the rest; `.all_bright()` resets. `.lines` are the Text objects.
- `ReelScene`: `hold_until(t)` (absolute seconds, raises on overrun), `clear(t, run)` (fade everything at t), `title(text)`.

## Timing discipline
- Every cue is a time in the final video from the measured narration ([[workflow]], stage 4). A `play` blocks, so
  `hold_until(t)` then a short play (0.3-0.5 s) must end before the next cue. Overran by 0.2 s? Move the next cue or shorten.
- For "this appears while the bar keeps filling" use `AnimationGroup(tracker.animate(run_time=4, rate_func=linear).set_value(x),
  Succession(Wait(1.4), FadeIn(note, run_time=0.3)))`.
- One method per beat; end each beat with `self.clear(next_start - 0.45, 0.4)`.
- At t=0 use `self.add(...)` so the first frame already shows the situation. No title card.
- Do not animate anything after `total - 2 s`; the end card takes over. Closing text must be visible before then.

## Visual grammar (see [[visuals]])
- `textPrimary` = what the narration is on now; `textMuted`/dim = already explained; `accent` sparingly, for the one thing to notice. Motion, position or opacity must carry the
  distinction too, never colour alone.
- One primary visual claim per shot. Show the pattern before the equation or label.
- Keep positions consistent between related beats (the loops Reel reuses panel positions in the hook and the reveal).
- Patterns that worked: counters + bars for work done; a halving cell row for search; a table that fills cell by cell
  for comparisons; code panels with line focus for algorithms; axes with two curves for growth (use a range where both
  curves are visible and say "input size" and "steps", nothing more).
- Size for a phone: text 28 or larger (code 28-30), headings 44-60, hero numbers 80-120. Few words, large type.

## Layout box (540x960 on a 9x16 plane)
Content between y = 5.6 and y = -4.6 · title at y = 5.0 · watermark upper right (x > 2.3, y > 6) · captions below y = -5 ·
side margins of 0.5 (columns x = -3.5 to 3.5). Check bounds after font substitution by looking at frames.

## Pitfalls
- Do not `FadeIn` a counter or `always_redraw` object in the same `play` that animates its tracker (`zip()` error). Fade it in
  first, then animate the tracker.
- The brand font may lack arrows or math symbols: use words or draw shapes. `x`, `²` and `...` render fine in the default font; check others.
- Compute positions from measured bounds (`next_to`, `get_end()`), not guessed numbers, for labels attached to shapes.
- Labels must come from the approved narration, `onScreen` or cited claims; no new facts in the scene.
- Rendering uses `-qh` with the pixel size fixed in `reel_kit.py`; the raw scene lands in `output/<name>/manim/`.
