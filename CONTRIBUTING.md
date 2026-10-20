# Contributing to reelfn

Thank you for helping! Bug reports, new example reels, themes, check types, docs fixes and translations are all
welcome. You do not need to be an expert: if something confused you, that is worth an issue.

## Ground rules

- Be kind; see the [Code of Conduct](CODE_OF_CONDUCT.md).
- Never include personal content in a pull request: your `brand/brand.json`, logos, `.env`, `reels/`, or `output/`.
  (They are git-ignored, so this only happens if you force-add them.)
- For a big change, open an issue first so we can agree on the approach.

## Development setup

```bash
git clone https://github.com/thekusaldarshana/reelfn.git
cd reelfn
npm install
npm run setup     # Python environment, Manim, audio tools; runs the doctor at the end
npm run check     # typecheck, unit tests, validate the examples (offline, no keys)
```

Before you open a pull request:

```bash
npm run check
npm run reel -- build time-complexity-loops --voice placeholder   # if you touched rendering, audio or branding
```

The GitHub Actions workflow in `.github/workflows/ci.yml` runs both on Linux, macOS and Windows. It is started
manually from the Actions tab for now, so please include the output of `npm run check` and the OS you tested on in
your pull request.

## Project map

| Path | What it is |
| --- | --- |
| `scripts/reelfn.mjs` | The `npm run reel` command line: finds a reel and runs each stage |
| `scripts/lib/` | `setup`, `doctor` and the Node-side brand resolver |
| `src/episode.ts` | Episode schema and deterministic checks (TypeScript + zod) |
| `renderer/brand.py` | Python-side brand resolver (keep in step with `scripts/lib/brand.mjs`) |
| `renderer/manim/reel_kit.py` | Shared scene helpers: brand colours/fonts, labels, counters, code panels, timing |
| `renderer/audio/` | Narrators (`gemini.mjs`, `local_voice.py`, `placeholder.py`), mixing, music, captions |
| `renderer/assemble.py` | FFmpeg assembly: captions, watermark, end card, probe, manifest |
| `brand/` | Defaults, themes, and the (ignored) user brand |
| `templates/reel/` | What `npm run reel -- new` copies |
| `examples/` | Complete reference reels |
| `skills/reelfn/` | The AI agent skill: the workflow agents follow |
| `test/` | Node tests (`*.test.ts` compiled to `dist/`, `*.test.mjs` run directly) |

How the pieces fit together: [docs/how-it-works.md](docs/how-it-works.md).

## Conventions

- **Cross-platform first.** Orchestrate with Node (`scripts/*.mjs`), not shell scripts. Use `path.join`, never
  hard-code `/` or `\`. Run FFmpeg from the repository root with relative paths (Windows drive letters break filters).
- **No hard-coded branding.** Colours, fonts, names and logos always come from the brand resolver.
- **Plain-language errors.** Every failure a user can hit should say what to do next, ideally the exact command.
- **Deterministic truth.** A new number type on screen needs a check in `src/episode.ts` with accept and reject tests.
- **Small, focused pull requests** with a clear description. Add a line to `CHANGELOG.md` under *Unreleased* for
  user-visible changes.
- Python dependencies are pinned in `requirements.lock`; top-level ranges live in `requirements.in`.

## Good first contributions

- A new colour theme in `brand/themes/`.
- A new example reel in `examples/` (with sources and checked numbers).
- A new deterministic check type (for example percentages, unit conversions, compound growth).
- Translating the starter template or docs.
- Testing setup on a machine or OS version we have not tried, and reporting what happened.

## Releasing (maintainers)

1. Update `CHANGELOG.md` and the version in `package.json`.
2. Run `npm run check` and the example build locally (and the CI workflow from the Actions tab, if available).
3. Tag `vX.Y.Z` and publish a GitHub release with the changelog section.

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
