# Examples

Two complete reels you can build and study. Each has the same layout as your own reels in `reels/`.

| Example | Length | What it shows off |
| --- | --- | --- |
| [`time-complexity-loops`](time-complexity-loops/) | 64 s | Code panels with line focus, counters, a growing table, years vs seconds |
| [`time-complexity-45`](time-complexity-45/) | 45 s | Racing bars, a halving row of cells, growth curves |

**[Project quick start](../README.md#quick-start)** · **[Brand guide](../brand/README.md)** · **[Create your own reel](../reels/README.md)**

Complete the project setup first, then run commands from the **repository root**.
Both examples include `episode.json`, a Manim `scene.py`, and a `release.md`
with suggested post copy.

Build one without any API key (silent placeholder voice):

```bash
npm run reel -- build time-complexity-loops --voice placeholder
```

With a Gemini key in `.env`, drop `--voice placeholder` to hear the narrator. Both episodes cite their sources and
every number on screen has a deterministic check: open `episode.json` to see how.


## Validate and review

```bash
npm run reel -- validate time-complexity-loops
npm run reel -- frames time-complexity-loops
```

Build outputs go in `output/time-complexity-loops/`; the example source files
stay in this directory. Review the MP4 and contact sheet before publishing.
The placeholder voice is silent and is intended for trying the pipeline.
