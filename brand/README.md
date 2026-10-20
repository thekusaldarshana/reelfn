# Your brand

Everything that makes a video look and sound like *your* channel lives here. Out of the box, reelfn uses a neutral
dark look with no watermark and no end card. Make it yours in three steps (or ask your AI agent: *"set up my brand"*).

## 1. Create your brand file

```bash
npm run reel -- brand init
```

This copies `brand.example.json` to `brand/brand.json`. Open it in any text editor and change what you like. Every
setting is optional: anything you delete falls back to the default in `default.json`.

| Setting | What it does | Example |
| --- | --- | --- |
| `name` | Your channel name. Used as a text watermark and end card if you have no logo. | `"Science Corner"` |
| `handle`, `hashtag` | Suggested in post captions. | `"@sciencecorner"`, `"#sciencecorner"` |
| `theme` | A colour theme from `themes/`: `midnight` (dark), `paper` (light), `ocean` (deep blue). | `"paper"` |
| `colors` | Override any single colour of the theme. | `{ "accent": "#FF5A5F" }` |
| `font` | The main font (`family` must be the font's exact name, `file` its path). | see below |
| `watermark` | Small mark in the upper-right corner: `image`, or `text`, plus `width`, `opacity`. | |
| `endCard` | Closing card: `image` or `text`, and `seconds` (set `0` for none). | |
| `voice` | Narrator: `provider` (`gemini`, `kokoro`, `placeholder`), `voice`, `language`, `style`. | `"voice": "Kore"` |
| `editorial` | Your audience and tone, used by the AI agent when writing scripts. | |

Check the result any time:

```bash
npm run reel -- brand
```

## 2. Add your logo (optional)

Put your files in `brand/assets/`:

- `logo.png`: shown in the middle of the end card (up to 400 px wide by default).
- `watermark.png`: shown small in the upper-right corner during the video.

Transparent PNGs look best. If your logo sits on a solid black background, set `"keyOutBlack": true` in that section
to make the black transparent. No logo? Leave the folder empty: your `name` is used as text instead.

## 3. Use your own font (optional)

Copy the font file (`.ttf` or `.otf`) somewhere inside the reelfn folder, for example `brand/assets/fonts/`, and
set:

```json
"font": { "family": "Your Font Name", "file": "brand/assets/fonts/YourFont-Regular.ttf" }
```

Make sure you are allowed to use the font in videos. The bundled fonts (Red Hat Display, JetBrains Mono, Atkinson
Hyperlegible) are under the SIL Open Font License.

## Make your own theme

Copy `themes/midnight.json` to `themes/<your-theme>.json`, change the colours, and set `"theme": "<your-theme>"`.
Keep enough contrast between `background` and `textPrimary` for small phone screens.

## Privacy

`brand/brand.json` and `brand/assets/` are ignored by git, so your personal brand is never uploaded by accident
(for example in a pull request). If you keep your own fork and want them versioned, remove those lines from
`.gitignore`.
