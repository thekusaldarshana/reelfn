"""Resolve the active brand: built-in defaults, a colour theme, then the user's brand/brand.json.

Keep this in step with scripts/lib/brand.mjs (the Node side uses the same rules).

- brand/default.json   tracked defaults; never edited by users
- brand/themes/*.json  colour themes, selected with "theme"
- brand/brand.json     the user's own overrides (git-ignored), created by `npm run brand`

The watermark and end card use an image when its file exists, otherwise text, otherwise nothing.
Text falls back to the brand "name"; an empty name means an unbranded video.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brand"
REQUIRED_COLORS = ("background", "surface", "border", "textPrimary", "textSecondary", "textMuted")


def _merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path.relative_to(ROOT)} is not valid JSON: {error}") from error


def _mark(section: dict, name: str) -> dict:
    image = ROOT / section["image"] if section.get("image") else None
    if image and image.is_file():
        return {**section, "kind": "image", "path": image}
    text = (section.get("text") or name or "").strip()
    if text:
        return {**section, "kind": "text", "text": text}
    return {**section, "kind": "none"}


def load_brand(root: Path = ROOT) -> dict:
    brand_dir = root / "brand"
    brand = _read(brand_dir / "default.json")
    user_file = brand_dir / "brand.json"
    if user_file.is_file():
        brand = _merge(brand, _read(user_file))
    theme_file = brand_dir / "themes" / f"{brand.get('theme') or 'midnight'}.json"
    if not theme_file.is_file():
        raise ValueError(f"Unknown theme '{brand.get('theme')}': add {theme_file.relative_to(root)} or pick one in brand/themes/")
    brand["colors"] = {**_read(theme_file)["colors"], **brand.get("colors", {})}
    missing = [key for key in REQUIRED_COLORS if key not in brand["colors"]]
    if missing:
        raise ValueError(f"Brand colours are missing: {', '.join(missing)}")
    brand["fontPath"] = root / brand["font"]["file"]
    if not brand["fontPath"].is_file():
        raise FileNotFoundError(f"Brand font not found: {brand['fontPath']}")
    brand["monoFontPaths"] = [root / path for path in brand["monoFont"]["files"]]
    name = (brand.get("name") or "").strip()
    brand["watermark"] = _mark(brand["watermark"], name)
    brand["endCard"] = _mark(brand["endCard"], name)
    brand["sources"] = [path for path in (brand_dir / "default.json", theme_file, user_file) if path.is_file()]
    return brand


if __name__ == "__main__":
    resolved = load_brand()
    print(json.dumps({key: value for key, value in resolved.items() if key != "sources"}, indent=2, default=str))
