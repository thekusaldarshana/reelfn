"""Shared building blocks for Manim scenes (brand colours, fonts, timing, code panels).

New scenes should import from here instead of copying helpers. Layout rules:
- 540x960 frame on a 9x16 coordinate plane; keep content between y = 5.6 and y = -4.6.
- The watermark owns the upper-right corner (x > 2.3, y > 6) and captions own y < -5.
- Bright (textPrimary) = what the narration is on now; dimmed = already explained.

Colours and fonts come from your brand (brand/brand.json, see brand/README.md), so the same
scene renders in any channel's look.
"""

import sys
from pathlib import Path

from manimpango import register_font
from manim import (
    DOWN, LEFT, RIGHT, UP, FadeOut, Rectangle, RoundedRectangle, Scene, Text, VGroup, always_redraw, config,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from brand import load_brand  # noqa: E402  (renderer/ is put on the path just above)

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

BRAND = load_brand()
COLORS = BRAND["colors"]
FONT = BRAND["font"]["family"]
MONO = BRAND["monoFont"]["family"]
register_font(str(BRAND["fontPath"]))
for _path in BRAND["monoFontPaths"]:
    register_font(str(_path))

LEFT_X, RIGHT_X, TRACK_W = -3.5, 3.5, 7.0
TITLE_Y = 5.0
DIM = 0.38


def label(value: str, size: int = 45, color: str | None = None, width: float = 7.4) -> Text:
    item = Text(value, font=FONT, font_size=size, color=color or COLORS["textPrimary"])
    if item.width > width:
        item.scale_to_fit_width(width)
    return item


def left(item: Text, y: float, x: float = LEFT_X) -> Text:
    return item.move_to([x, y, 0], aligned_edge=LEFT)


def right(item: Text, y: float, x: float = RIGHT_X) -> Text:
    return item.move_to([x, y, 0], aligned_edge=RIGHT)


def counter(tracker, y: float, size: int = 40, suffix: str = "", x: float = RIGHT_X):
    """Right-aligned number that follows a ValueTracker (thousands separators)."""
    return always_redraw(lambda: right(label(f"{int(round(tracker.get_value())):,}{suffix}", size), y, x))


class CodeBlock(VGroup):
    """A monospace snippet in a quiet panel. `lines` keep their indentation."""

    def __init__(self, source: list[str], y: float, size: int = 30, width: float = 7.6):
        super().__init__()
        probe = Text("M" * 10, font=MONO, font_size=size)
        self.char_w = probe.width / 10
        self.line_h = probe.height * 1.9
        pad = 0.28
        height = self.line_h * len(source) + 2 * pad
        self.panel = RoundedRectangle(
            width=width, height=height, corner_radius=0.18, stroke_color=COLORS["border"], stroke_width=2,
            fill_color=COLORS["surface"], fill_opacity=1,
        ).move_to([0, y, 0])
        self.lines: list[Text] = []
        top = y + height / 2 - pad - self.line_h / 2
        x0 = -width / 2 + pad + 0.1
        for index, raw in enumerate(source):
            indent = len(raw) - len(raw.lstrip(" "))
            text = Text(raw.strip(), font=MONO, font_size=size, color=COLORS["textPrimary"])
            available = width - 2 * pad - 0.2 - indent * self.char_w
            if text.width > available:  # never overflow the panel
                text.scale_to_fit_width(available)
            text.move_to([x0 + indent * self.char_w, top - index * self.line_h, 0], aligned_edge=LEFT)
            self.lines.append(text)
        self.add(self.panel, *self.lines)

    def focus(self, *indexes: int):
        """Animations that brighten `indexes` and dim the other lines."""
        return [line.animate.set_opacity(1.0 if i in indexes else DIM) for i, line in enumerate(self.lines)]

    def all_bright(self):
        return [line.animate.set_opacity(1.0) for line in self.lines]


class ReelScene(Scene):
    """Absolute-time scheduling: every cue is a time in the final video, not a duration."""

    def hold_until(self, target: float) -> None:
        remaining = target - self.renderer.time
        if remaining < -0.035:
            raise ValueError(f"Storyboard overran {target:.2f}s by {-remaining:.2f}s")
        if remaining > 0.001:
            self.wait(remaining)

    def clear(self, start: float, run: float = 0.4) -> None:
        self.hold_until(start)
        self.play(FadeOut(*self.mobjects), run_time=run)

    def title(self, text: str, size: int = 52) -> Text:
        return label(text, size).move_to(UP * TITLE_Y)
