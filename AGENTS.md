# Agent guide

reelfn makes narrated, captioned, branded 9:16 explainer videos with code (Manim + FFmpeg), not a video model.
The person you are helping is usually a **creator, not a programmer**: run commands yourself, explain in plain words,
and never ask them to edit JSON or read a stack trace.

## Making or refining a reel
Read `skills/reelfn/SKILL.md` first and follow it. In short:
1. `npm run doctor`. If anything FAILs, or there is no `brand/brand.json`, follow
   `skills/reelfn/references/first-run.md` (machine setup, voice key, the creator's brand).
2. Ask about anything undecided in one batch (do not guess), then use the workflow in
   `skills/reelfn/references/workflow.md`: `npm run reel -- new <name>` … `npm run reel -- build <name>`.

## Hard rules
- Never print, log or ask for secrets in chat. `.env` is git-ignored; check the key with `npm run doctor` only.
- Never publish, push, or open a pull request unless asked. Never self-approve a script or a final video.
- Every number on screen needs evidence or a deterministic check in the episode (`npm run reel -- validate <name>`).
- `reels/`, `brand/brand.json` and `brand/assets/` belong to the creator: never delete them, never commit them upstream.
- Ask before running system installers (`sudo`, `brew`, `winget`) on the creator's machine.

## Changing reelfn itself
- Project map and conventions: `CONTRIBUTING.md`. Run `npm run check` before you finish (offline; no keys needed).
- Keep it cross-platform: Node scripts (not shell scripts) for orchestration, `path.join`, no shell-only syntax.
- Keep `renderer/brand.py` and `scripts/lib/brand.mjs` in step; they resolve the same brand rules.
- Never hard-code a brand, colour, font, channel name or person into code, scenes, examples or docs.
