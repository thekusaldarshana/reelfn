# First run: the machine, then the creator's brand

Do this once per machine and once per creator. Run every command yourself from the repository root.

## 1. Machine
1. `npm run setup` (5-10 minutes the first time; safe to re-run). It installs Node packages, builds the validator,
   creates the Python environment `.venv` (Manim, audio tools) and a `.env` file, then runs the doctor.
2. If a line says FAIL, it prints the exact fix for this operating system (for example `brew install ffmpeg` or
   `winget install Gyan.FFmpeg`). Commands with `sudo` or an installer need the creator: show the one line, say
   why it is needed, and ask them to run it (or ask permission to run it). Then `npm run setup` again.
3. Prove it works before any creative work:
   `npm run reel -- build time-complexity-loops --voice placeholder` makes a full silent preview in about a minute.

Needs: Node.js 22+, Python 3.11-3.13 (3.12 preferred), FFmpeg. On macOS and Linux Manim also needs Cairo and
Pango (the doctor gives the command). Windows needs nothing extra.

## 2. Narrator voice key
The default narrator is Gemini text-to-speech, which needs `GEMINI_API_KEY` in `.env`.
- Check it by name only: `npm run doctor` prints "is set (value hidden)". Never `cat .env`, echo it, or log headers.
- If it is missing, tell the creator: get a free key at https://aistudio.google.com/apikey, open the `.env` file in
  the reelfn folder, and paste it after `GEMINI_API_KEY=`. Never ask them to paste the key into chat.
- Free tier: roughly 10 voice requests a day, one per beat, retakes count. Until a key exists, use
  `--voice placeholder` (silent) for previews.

## 3. Brand (ask, in one batch)
If `brand/brand.json` does not exist, the video has no watermark or end card. Ask the creator, recommending defaults:
1. **Channel name** and handle (used for the text watermark, end card and hashtag).
2. **Look**: a theme from `brand/themes/` (`midnight` dark, `paper` light, `ocean` deep blue), or their own colours.
3. **Logo**: do they have a logo file? If yes, ask them to put it in `brand/assets/` as `logo.png` (end card) and
   optionally `watermark.png` (small, upper right). Transparent PNGs work best. If not, their name is used as text.
4. **Voice**: keep Gemini "Puck", or another Gemini voice; accent and language; tone of delivery.

Then run `npm run reel -- brand init` and edit `brand/brand.json` with their answers (all keys are optional; see
`brand/README.md`). Show the result with `npm run reel -- brand` and a quick
`npm run reel -- build time-complexity-loops --voice placeholder --version brand-test` so they can see the look.

`brand/brand.json`, `brand/assets/` and `reels/` are git-ignored: they belong to the creator and are never part of
a pull request to reelfn.
