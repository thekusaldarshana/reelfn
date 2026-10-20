# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-20

First public release: a harness you clone and drive with an AI coding agent.

### Added
- `npm run reel` command line for the whole pipeline: `new`, `validate`, `voice`, `mix`, `captions`, `render`,
  `assemble`, `build`, `frames`, `list`, `brand`, plus `npm run setup` and `npm run doctor`.
- Reel folders (`reels/<name>/` with `episode.json`, `scene.py`, `release.md`) and a starter template.
- Episode validator: timeline, sources, concept-reveal rule, deterministic number checks
  (`binary-search-capacity`, `operation-count`), and a guard against leftover TODOs. Any language tag and subject.
- Brand system: themes (`midnight`, `paper`, `ocean`), colour overrides, your own font, logo or text watermark and
  end card, narrator voice, and editorial tone, all in a git-ignored `brand/brand.json`.
- Narrators: Gemini TTS (default), offline Kokoro (experimental), and a silent placeholder for key-free previews.
- Generated music and sound cues, word-timed captions, FFmpeg assembly with a probe, inspection report and hashes.
- Agent skill (`skills/reelfn/`) with entry points for Claude Code, Codex, Cursor and Gemini CLI.
- Two example reels with cited sources and checked numbers.
- A GitHub Actions workflow (run manually) that checks and renders an example on Linux, macOS and Windows.

[Unreleased]: https://github.com/thekusaldarshana/reelfn/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/thekusaldarshana/reelfn/releases/tag/v0.1.0
