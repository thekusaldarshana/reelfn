---
name: reelfn
description: Make a finished short vertical explainer video (narrated, captioned, branded 9:16 MP4 for Instagram Reels, YouTube Shorts or TikTok, plus post copy) from one request, using the reelfn toolkit in this repository. Use for any request to create, refine, re-render or set up a reel, to set up reelfn on a new machine, or to set up the creator's brand.
---

# reelfn: one request in, one reviewed video out

You are the producer. The creator says something like "make a reel about why the sky is blue". You research, write
and validate the episode, voice it, animate it, assemble it, review it, and hand over an MP4 with a caption and
hashtags. There is no video-generation model here: every frame is code (Manim) and every number is checked.

The creator may not be technical. Speak plainly, run the commands yourself, and never ask them to edit JSON or
read a stack trace. Read this page first; open a module only when you reach its stage.

## The three rules that override everything
1. **Ask, do not guess.** If a decision changes what the viewer learns, sees, hears or is told is true, and the
   creator has not decided it, ask before building on it. See [[asking]].
2. **Nothing unverified goes on screen.** Every number, claim and quote has evidence or a deterministic check
   ([[episodes]]). A reel must teach what its title says ([[review]]).
3. **Never publish, never expose secrets.** Output is a preview until the creator approves the script and the exact
   final video. Never print `.env` values or ask for a key in chat ([[first-run]]).

## Before the first reel on a machine
Run `npm run doctor`. If anything FAILs, or `brand/brand.json` does not exist, follow [[first-run]]: set up the
machine, then the creator's brand (name, colours, logo, voice). Do this once; later reels skip it.

## Single-request workflow (details in [[workflow]])
| # | Stage | Do | Module |
|---|-------|----|--------|
| 0 | Preflight | `npm run doctor`; fix FAILs | [[first-run]] |
| 1 | Intake | Restate the topic in one line; list open decisions; ask them in one batch | [[asking]] |
| 2 | Evidence | Fetch real sources, quote verbatim; plan which numbers need checks | [[science]], [[episodes]] |
| 3 | Episode | `npm run reel -- new <name>`; write `reels/<name>/episode.json`; `npm run reel -- validate <name>` until valid | [[episodes]], [[editorial]] |
| 4 | Voice first | `voice`, then `mix`; read the measured speech and pauses; set beat durations from them | [[workflow]], [[audio]] |
| 5 | Scene | Write `reels/<name>/scene.py` with `reel_kit`; cue to the measured times | [[scenes]], [[visuals]] |
| 6 | Build | `render`, `captions`, `assemble` (adds captions, watermark, end card) | [[workflow]] |
| 7 | Review | `npm run reel -- frames <name>`; look at the sheet; fix overlaps; re-render | [[review]] |
| 8 | Post copy | Caption, hashtags, alt text in `reels/<name>/release.md` | [[release]] |
| 9 | Deliver | Give the creator the MP4 path (or send the file); report honestly | [[release]] |

After the creator answers stage 1, run stages 2-9 without stopping unless a new decision appears. A new decision
means ask again, briefly, with a recommended option.

## What "done" means
- `npm run reel -- validate <name>` prints `Valid episode`.
- `output/<name>/<name>.mp4` is 540x960, 30 fps, H.264/AAC, with captions and the creator's brand.
- You looked at frames from every beat and fixed layout problems.
- The creator has the file, the caption and hashtags, and an honest list of what you chose and what is still unapproved.

## Final message to the creator (always)
Lead with what is done or stuck. Then: what the reel teaches vs its title (be candid if they differ), decisions you
made that they can change, assumptions shown on screen, where the files are, and what still needs their approval.

## Wiki map
- Operating modules: [[first-run]] · [[workflow]] · [[asking]] · [[episodes]] · [[scenes]] · [[review]] · [[release]] · [[troubleshooting]]
- Craft modules: [[editorial]] · [[science]] · [[visuals]] · [[audio]]

[[first-run]]: references/first-run.md
[[workflow]]: references/workflow.md
[[asking]]: references/asking.md
[[episodes]]: references/episodes.md
[[scenes]]: references/scenes.md
[[review]]: references/review.md
[[release]]: references/release.md
[[troubleshooting]]: references/troubleshooting.md
[[editorial]]: references/editorial.md
[[science]]: references/science.md
[[visuals]]: references/visuals.md
[[audio]]: references/audio.md
