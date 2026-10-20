# Visuals: motion language

Colours, fonts, watermark and end card come from the creator's brand (`brand/brand.json`, read through `reel_kit`).
Preserve legibility in the 540x960 frame, including the lower caption lane. Diagrams encode quantities accurately and
reveal the causal step before its label.

## Grammar
- Start with a concrete field of possibilities and one unresolved question. Keep the academic name until the visible
  mechanism earns it.
- One active pointer, split or comparison at a time. Muted objects stay visible briefly so viewers see what was removed.
- Let each spoken decision cause an immediate visual consequence: a disappearing half, a changed counter, a moved pointer.
- Change scale to prevent monotony: the whole situation, one local operation, the numerical proof, a practical use.
- Brightness, opacity, position and motion carry meaning together; never colour alone.
- One primary visual claim per shot. Equations appear only after the audience has seen the pattern they describe.

## Layout
- 9x16 Manim frame rendered at 540x960. Content between y = 5.6 and y = -4.6; captions own y < -5; the watermark
  owns the upper-right corner. Anchor related elements to each other's measured bounds (`next_to`), not guessed numbers.
- Size for a phone: body text 28+, headings 44-60, hero numbers 80-120. Fewer words, larger type, more motion than a web page.
- Nothing important during the end card (the last `endCard.seconds`).

## Patterns that worked
Counters and bars for work done · a halving row of cells for search · a table that fills cell by cell for comparisons ·
code panels with line focus for algorithms · axes with two curves for growth (label only "input size" and "steps").

## Sound
A short cue marks each change of beat (a change in understanding), not every animation. Music stays under speech and
rises between phrases. All of it is generated in code (`renderer/audio/sound.py`), so there are no rights to clear.
