# Episodes: the validated contract for a Reel

An episode is `reels/<name>/episode.json` (`schemaVersion: 2`). Validate with `npm run reel -- validate <name>`.
The validator is `src/episode.ts`; `examples/*/episode.json` are complete, valid references.

## Shape
`slug (= folder name), language (a tag such as "en" or "pt-BR"), audience, subject (free text), question, payoff,
conceptReveal {name, beatId}, brandVersion, templateVersion, durationSeconds (<=180), evidence[], claims[], beats[]`.
Any string still containing `TODO` (from the template) fails validation with `TODO_LEFT`.

- **evidence**: `id, title, publisher, url (https), accessedAt (YYYY-MM-DD), passage, locator?` (verbatim from the fetch).
- **claims**: `id, text, kind, evidenceIds, assumptions[], limitations[], check?`
  - `sourced` needs at least one evidence id; `derived` needs a `check` the validator can recompute.
  - Every claim must appear in some beat's `claimIds` (a claim nobody sees is rejected).
- **beats**: `id, start, duration, narration, onScreen, visual {template, parameters}, claimIds, delivery?`
  - Beats are contiguous from 0 and end exactly at `durationSeconds` (tolerance 0.001 s).
  - The `conceptReveal` beat must be the third beat or later and name the concept in **both** `narration` and `onScreen`.
  - `narration` is spoken verbatim by the narrator: write numbers as words ("two hundred million"). It also becomes captions.
  - `delivery.geminiStyle` (optional) adds per-beat direction to the voice style ("brisk challenge", "slow, land the reveal").

## Checks you can use today
```json
{ "type": "binary-search-capacity", "universeSize": 1000000, "questions": 20, "strategy": "balanced" }
{ "type": "operation-count", "n": 1000, "growth": "quadratic", "steps": 1000000 }
{ "type": "operation-count", "n": 1000000000, "growth": "quadratic", "stepsApprox": 1e18,
  "stepsPerSecond": 200000000, "years": 158.4 }
```
- `operation-count` growth: `linear` (n), `quadratic` (n x n), `pairs` (n(n-1)/2), `set-scan` (2n modeled operations). Give exact `steps` when it fits a safe
  integer, otherwise `stepsApprox`. Add `stepsPerSecond` with `seconds` and/or `years` for run times (0.5% tolerance,
  Julian year of 365.25 days). A run time without a rate is rejected.
- A new kind of fact needs a new check: add a zod schema and a verifier in `src/episode.ts`, put it in the `Claim.check`
  union, add accept and reject tests in `test/episode.test.ts`, then `npm test`. A general-purpose check is a welcome
  contribution upstream (see CONTRIBUTING.md).
  Never mark a number `derived` without a real check. Do not stretch an existing check to fit the topic.

## Evidence rules
- Fetch the page; copy a passage that the fetch returned. If a table cell is garbled, quote what you can, record the
  uncertainty in the claim's `limitations`, or drop the claim.
- Assumptions that make a number concrete (a CPU speed, a list that is sorted) belong in `assumptions`, in the caption, and
  on screen.
- Limitations are part of the claim: constant factors, best vs worst case, memory cost, "counts steps not seconds".

## Writing the beats
Open inside a situation; show the mechanism; reveal the name after the viewer has seen it; end on a question. One idea per
beat. Voice and tone are in [[editorial]] and the creator's `brand/brand.json` (`editorial`); fact discipline in [[science]].
