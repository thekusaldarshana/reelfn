# Asking: when you must, when you may decide

The creator wants a finished video from one request **and** wants to be asked rather than have you guess. Both hold:
ask early, in one batch, then work without interruption.

## Always ask (unless the creator already answered or the repo answers)
- **Scope and angle** when the topic is broad or ambiguous. "Time complexity" can mean binary search, loops, sorting or
  big-O notation. Offer 2-4 concrete angles and say what each would teach. The title must match what the video teaches.
- **Duration** (30 / 45 / 60 s...) and **hook style**, if not specified.
- **Brand** if `brand/brand.json` does not exist yet (see [[first-run]]): name, look, logo, voice.
- **Any number or fact the creator did not give and you cannot source**: hardware speed, dataset size, dates, prices, quotes.
  If a stated assumption makes a number concrete (e.g. 200 million steps per second), say so and offer to change it.
- **Brand additions**: a new font, colour, logo treatment, sound, or a voice other than the one in `brand/brand.json`.
- **Anything outward-facing or irreversible**: publishing, pushing, opening a PR, deleting the creator's files,
  spending quota in bulk, or running a system installer (`sudo`, `winget`, `brew`) on their machine.
- **Voice budget**: if the beats needing audio exceed the day's remaining Gemini requests, or a rate limit hits mid-job, say
  so and offer the options in [[troubleshooting]] (wait, a paid key, placeholder voice for a preview).
- **Missing secrets**: ask the creator to paste the key into the `.env` file themselves, never into the chat.
- **Mismatch you notice**: if what you are about to build does not match the request, stop and say so.

## Decide, then report (do not ask)
Layout and easing, beat count within the limits, wording of captions and hashtags (drafts), file and class names, which
check type applies, code snippet details, retiming, fixing overlaps, re-rendering. List the notable ones in the final
message so the creator can redirect them.

## How to ask well
- One batch, at most four questions, before heavy work (research, TTS, rendering).
- Put your recommendation first and label it "(Recommended)". State the consequence of each option in a sentence.
- Never ask what the repository, `brand/brand.json` or earlier answers already settle. Read first.
- Do not ask permission for routine, reversible work (edit files in `reels/`, render, validate). Do not ask "should I continue?".
- Write for a non-technical creator: plain words, no jargon, no file formats unless they ask.
- If the creator says "ask me for anything", lower the bar for the first group and still keep it to one batch.
- If an answer creates a new decision later (a source contradicts the plan; a number fails its check), ask again briefly
  with the evidence, a recommendation, and what you will do by default.

## Approval gates (never self-approve)
1. **Script approval** before the video is final. If the creator asked for the finished video in one request you may render
   a clearly labelled **preview** first, then ask for script approval with the script in front of them.
2. **Final-media approval** is bound to the exact file hash (`output/<name>/<name>.manifest.json`, `outputSha256`).
3. **Rights and publishing** stay with the creator. Nothing in this repository posts anywhere.

## Worked example
Request: "Time complexity". An agent built a binary-search-vs-scan reel; the creator said it was not about time
complexity. Better: ask first, "Which angle? (a) loops and step growth with code, years vs seconds; (b) search
strategies; (c) a Big-O notation tour". The reel built on the creator's own angle landed first time.
