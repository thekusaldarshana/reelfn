# Review and refinement

Never self-approve. Script approval and final-media approval belong to the creator; the final approval is bound to
the exact file hash (`outputSha256` in `output/<name>/<name>.manifest.json`). Any change to narration or claims needs
the script approved again.

## Look at the video
`npm run reel -- frames <name>` samples the middle of every beat and the end card; add times to look closer
(`npm run reel -- frames <name> 12.4 13 13.6`). Assembly also writes `<name>-contact-sheet.png` (12 even samples).
Check, beat by beat:
- **Claim-to-visual agreement:** every number and label on screen matches the narration and a validated claim.
- **Layout:** no overlaps; text clear of panel edges, the watermark corner (upper right) and the caption lane (bottom).
- **Glyphs:** no empty boxes ("tofu") where the brand font lacks a symbol.
- **Pacing:** each visual change lands on its spoken phrase; nothing important appears during the end card.
- **Captions:** readable against the theme; timing is word-proportional, so watch for drift on long beats.
- **Audio:** you can measure levels and pauses but cannot hear. Ask the creator to listen for pronunciation, pace and
  music balance before approving.

## Refine
Treat each piece of feedback as a scoped change and regenerate only what depends on it: wording changes re-voice only
the changed beats; visual changes need `render` and `assemble` only. Use `--version v2` to keep the previous take
for comparison. Report what changed and why in the final message.

## Does it teach its title?
A reel about binary search is not "time complexity". If the finished video teaches something narrower or different
from its title, say so plainly and offer to retitle or rework it.
