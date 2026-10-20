# Security policy

## Supported versions

reelfn is young. Security fixes go into the latest release on the `main` branch.

## Reporting a vulnerability

Please **do not open a public issue**. Report it privately with GitHub's
[private vulnerability reporting](https://github.com/thekusaldarshana/reelfn/security/advisories/new). Include what
you found, how to reproduce it, and its impact. You can expect a first reply within a week.

## What matters most here

- **API keys.** reelfn reads `GEMINI_API_KEY` from your environment or a local `.env` file, which is git-ignored.
  It never writes keys into manifests, logs or videos. Anything that could leak a key is a security bug.
- **Running code.** Reels are Python (Manim) scenes and run with your user's permissions, like any script. Only build
  reels from people you trust, and read a scene before you run it, just as you would any downloaded code.
- **AI agents.** The agent instructions (`AGENTS.md`, `skills/reelfn/`) tell agents never to print secrets, publish,
  or run system installers without asking. Instructions that weaken these rules are treated as security issues.
