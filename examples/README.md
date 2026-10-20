# Examples

Two complete reels you can build and study. Each has the same layout as your own reels in `reels/`.

| Example | Length | What it shows off |
| --- | --- | --- |
| [`time-complexity-loops`](time-complexity-loops/) | 64 s | Code panels with line focus, counters, a growing table, years vs seconds |
| [`time-complexity-45`](time-complexity-45/) | 45 s | Racing bars, a halving row of cells, growth curves |

Build one without any API key (silent placeholder voice):

```bash
npm run reel -- build time-complexity-loops --voice placeholder
```

With a Gemini key in `.env`, drop `--voice placeholder` to hear the narrator. Both episodes cite their sources and
every number on screen has a deterministic check: open `episode.json` to see how.
