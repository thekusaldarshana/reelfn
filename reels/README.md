# Your reels

Each reel is a folder here, created with:

```bash
npm run reel -- new my-topic
```

```
reels/my-topic/
├── episode.json   the script: beats, narration, sources and checked claims
├── scene.py       the animation (Manim)
└── release.md     caption, hashtags and alt text for posting
```

Finished videos go to `output/my-topic/` (not here). See `examples/` for two complete reels.

This folder's contents are ignored by git, so your reels stay private and never clash with reelfn updates. To keep
them in your own fork, remove the `reels/*` lines from `.gitignore`.
