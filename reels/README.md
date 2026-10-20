# Your reels

**[Project quick start](../README.md#quick-start)** · **[Examples](../examples/README.md)** · **[Brand guide](../brand/README.md)**

After setup, run commands from the **repository root**. Each reel is a folder
here, created with:

```bash
npm run reel -- new my-topic
```

```text
reels/my-topic/
├── episode.json   the script: beats, narration, sources and checked claims
├── scene.py       the animation (Manim)
└── release.md     caption, hashtags and alt text for posting
```

Finished videos go to `output/my-topic/` (not here). See [the examples](../examples/README.md) for two complete reels.

This folder's contents are ignored by git, so ordinary Git staging skips your reel files. Keep them out of shared archives and force-added commits too. To keep
them in your own fork, remove the `reels/*` lines from `.gitignore`.


## From draft to reviewed video

Fill in the new episode and scene, or ask your AI agent to do it with you.
Then validate, build, and review:

```bash
npm run reel -- validate my-topic
npm run reel -- build my-topic --voice placeholder
npm run reel -- frames my-topic
```

Use a configured narrator when you want speech. The placeholder option is
silent. `release.md` is draft post copy; the tool does not publish the video.
