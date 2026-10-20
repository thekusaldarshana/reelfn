"""Time complexity: a linear scan races a halving search, then both are scaled.

Quantities come from the validated episode `episode.json`
(1,000,000 / 2,000,000 / 4,000,000 / 1,000,000,000 items; 20 / 21 / 22 / 30
halvings, each checked by `binary-search-capacity`). Sections are timed to the
measured narration of that episode; re-time them if the audio changes.
Content stays above the caption lane (y < -4.6) and left of the watermark.
"""

import math

from manim import (
    DOWN, LEFT, RIGHT, UP, AnimationGroup, Axes, Succession, Wait, Circle, Create, FadeIn, FadeOut, GrowFromEdge, Line,
    Rectangle, RoundedRectangle, Text, ValueTracker, VGroup, Dot, always_redraw, linear,
)

from reel_kit import COLORS, LEFT_X, RIGHT_X, TITLE_Y, TRACK_W, ReelScene, label, left, right


class TimeComplexityReel(ReelScene):
    def bar(self, tracker: ValueTracker, total: float, y: float, bright: bool = True) -> Rectangle:
        color = COLORS["textPrimary"] if bright else COLORS["textMuted"]
        return always_redraw(lambda: Rectangle(
            width=max(0.002, TRACK_W * tracker.get_value() / total), height=0.34,
            fill_color=color, fill_opacity=1, stroke_width=0,
        ).move_to([LEFT_X, y, 0], aligned_edge=LEFT))

    def counter(self, tracker: ValueTracker, y: float, size: int = 42) -> Text:
        return always_redraw(lambda: right(label(f"{int(round(tracker.get_value())):,}", size), y))

    def construct(self) -> None:
        self.camera.background_color = COLORS["background"]
        self.hook()
        self.race()
        self.doubling()
        self.billion()
        self.reveal()

    # 0.00-5.50: a concrete field of possibilities and two ways to search it.
    def hook(self) -> None:
        title = self.title("1,000,000 contacts")
        dots = VGroup(*[
            Dot(point=[-3.25 + col * 0.5, 3.6 - row * 0.5, 0], radius=0.075,
                color=COLORS["textSecondary"])
            for row in range(10) for col in range(14)
        ])
        self.add(title, dots)  # the first frame already shows the situation
        halo = Circle(radius=0.3, color=COLORS["textPrimary"], stroke_width=3).move_to(dots[20])
        self.play(Create(halo), run_time=0.3)
        for index in (97, 41, 133):
            self.play(halo.animate.move_to(dots[index]), run_time=0.35)
        self.hold_until(1.9)
        scan = RoundedRectangle(width=3.2, height=1.0, corner_radius=0.25,
                                color=COLORS["textMuted"], stroke_width=3).move_to([-2.0, -2.3, 0])
        split = RoundedRectangle(width=3.2, height=1.0, corner_radius=0.25,
                                 color=COLORS["textPrimary"], stroke_width=3).move_to([2.0, -2.3, 0])
        scan_text = label("SCAN", 40, width=2.6).move_to(scan)
        split_text = label("SPLIT", 40, width=2.6).move_to(split)
        self.play(FadeOut(halo), FadeIn(VGroup(scan, scan_text), shift=UP * 0.2),
                  FadeIn(VGroup(split, split_text), shift=UP * 0.2), run_time=0.45)
        self.hold_until(3.5)
        wins = label("Who wins?", 60).move_to(DOWN * 3.85)
        self.play(FadeIn(wins, shift=UP * 0.2), run_time=0.35)
        self.clear(5.05, 0.45)

    # 5.50-17.00: scan fills a million checks; the split reaches one name in twenty.
    def race(self) -> None:
        self.hold_until(5.5)
        headline = self.title("Find one name")
        self.play(FadeIn(headline, shift=UP * 0.2), run_time=0.35)

        scan_label = left(label("SCAN", 42), 2.95)
        scan_track = Line([LEFT_X, 2.1, 0], [RIGHT_X, 2.1, 0], color=COLORS["border"], stroke_width=3)
        scan_value = ValueTracker(0)
        scan_bar = self.bar(scan_value, 1_000_000, 2.1, bright=False)
        scan_count = self.counter(scan_value, 2.95)
        self.hold_until(5.9)
        self.play(FadeIn(scan_label), Create(scan_track), FadeIn(scan_bar), FadeIn(scan_count), run_time=0.3)
        scan_note = left(label("checks, up to", 30, COLORS["textSecondary"]), 1.45)
        # The fill runs to 10.4s; the note lands at 7.5s, on "up to a million checks".
        self.play(AnimationGroup(
            scan_value.animate(run_time=4.3, rate_func=linear).set_value(1_000_000),
            Succession(Wait(1.4), FadeIn(scan_note, run_time=0.3)),
        ))

        split_label = left(label("SPLIT", 42), 0.15)
        steps = ValueTracker(0)
        split_count = self.counter(steps, 0.15)
        cells = VGroup(*[
            Rectangle(width=0.19, height=0.6, stroke_width=2, stroke_color=COLORS["textSecondary"],
                      fill_color=COLORS["textPrimary"], fill_opacity=0.9)
            .move_to([LEFT_X + 0.1 + i * (TRACK_W / 32), -0.9, 0])
            for i in range(32)
        ])
        self.hold_until(10.55)
        self.play(FadeIn(split_label), FadeIn(cells), FadeIn(split_count), run_time=0.35)
        # Five visible halvings keep the half that can still hold cell 21.
        for stop, dim, count in ((10.95, range(0, 16), 1), (11.6, range(24, 32), 2),
                                 (12.3, range(16, 20), 3), (12.9, range(22, 24), 4),
                                 (13.4, [20], 5)):
            self.hold_until(stop)
            self.play(*[cells[i].animate.set_opacity(0.08) for i in dim],
                      steps.animate.set_value(count), run_time=0.4)
        self.hold_until(14.1)
        self.play(steps.animate.set_value(20), run_time=0.8, rate_func=linear)

        sliver = Line([LEFT_X, -2.5, 0], [RIGHT_X, -2.5, 0], color=COLORS["border"], stroke_width=3)
        tick = Rectangle(width=0.03, height=0.34, fill_color=COLORS["textPrimary"], fill_opacity=1,
                         stroke_width=0).move_to([LEFT_X, -2.5, 0], aligned_edge=LEFT)
        scale_note = left(label("20 of 1,000,000, to scale", 32, COLORS["textSecondary"]), -3.2)
        self.hold_until(15.3)
        self.play(Create(sliver), FadeIn(tick), FadeIn(scale_note), run_time=0.5)
        self.clear(16.55, 0.45)

    # 17.00-28.00: double the names; the scan doubles, the split adds one.
    def doubling(self) -> None:
        self.hold_until(17.0)
        headline = self.title("Double the names")
        self.play(FadeIn(headline, shift=UP * 0.2), run_time=0.35)

        rows = []

        def row(y: float, names: str, scan_value: str, split_value: str, scan_width: float):
            heading = left(label(names, 34, COLORS["textSecondary"]), y + 0.8)
            track = Line([LEFT_X, y + 0.15, 0], [LEFT_X + scan_width, y + 0.15, 0],
                         color=COLORS["textMuted"], stroke_width=0)
            bar = Rectangle(width=scan_width, height=0.3, fill_color=COLORS["textMuted"], fill_opacity=1,
                            stroke_width=0).move_to([LEFT_X, y + 0.15, 0], aligned_edge=LEFT)
            scan = left(label(f"SCAN  {scan_value}", 34), y - 0.5)
            split = right(label(f"SPLIT  {split_value}", 34), y - 0.5)
            return heading, bar, scan, split

        first = row(2.7, "1,000,000 names", "1,000,000", "20", 1.75)
        second = row(0.2, "2,000,000 names", "2,000,000", "21", 3.5)
        third = row(-2.3, "4,000,000 names", "4,000,000", "22", 7.0)
        self.hold_until(17.45)
        self.play(FadeIn(first[0]), GrowFromEdge(first[1], LEFT), FadeIn(first[2]), FadeIn(first[3]),
                  run_time=0.5)
        self.hold_until(18.9)
        self.play(FadeIn(second[0]), GrowFromEdge(second[1], LEFT), run_time=0.5)
        self.hold_until(19.6)
        self.play(FadeIn(second[2]), run_time=0.3)
        plus_one = [right(label("+1", 40), 0.2 + 0.8), right(label("+1", 40), -2.3 + 0.8)]
        self.hold_until(21.0)
        self.play(FadeIn(second[3]), FadeIn(plus_one[0], shift=UP * 0.15), run_time=0.35)
        self.hold_until(23.2)
        self.play(FadeIn(third[0]), GrowFromEdge(third[1], LEFT), run_time=0.5)
        self.hold_until(23.9)
        self.play(FadeIn(third[2]), run_time=0.3)
        self.hold_until(24.4)
        self.play(FadeIn(third[3]), FadeIn(plus_one[1], shift=UP * 0.15), run_time=0.35)
        self.clear(27.6, 0.4)

    # 28.00-34.00: the same comparison at a billion names.
    def billion(self) -> None:
        self.hold_until(28.0)
        headline = self.title("A billion names")
        self.play(FadeIn(headline, shift=UP * 0.2), run_time=0.35)
        track = Line([LEFT_X, 2.0, 0], [RIGHT_X, 2.0, 0], color=COLORS["border"], stroke_width=3)
        scan_label = left(label("SCAN", 42), 2.85)
        value = ValueTracker(0)
        bar = self.bar(value, 1_000_000_000, 2.0, bright=False)
        count = self.counter(value, 2.85, 38)
        self.hold_until(30.3)
        self.play(FadeIn(scan_label), Create(track), FadeIn(bar), FadeIn(count), run_time=0.3)
        self.play(value.animate.set_value(1_000_000_000), run_time=1.9, rate_func=linear)  # to 32.5
        split_label = left(label("SPLIT", 42), 0.35)
        tick_track = Line([LEFT_X, -0.5, 0], [RIGHT_X, -0.5, 0], color=COLORS["border"], stroke_width=3)
        tick = Rectangle(width=0.03, height=0.34, fill_color=COLORS["textPrimary"], fill_opacity=1,
                         stroke_width=0).move_to([LEFT_X, -0.5, 0], aligned_edge=LEFT)
        self.hold_until(32.6)
        self.play(FadeIn(split_label), Create(tick_track), FadeIn(tick), run_time=0.3)
        thirty = label("30", 120).move_to(DOWN * 2.6)
        self.hold_until(33.1)
        self.play(FadeIn(thirty, shift=UP * 0.25), run_time=0.35)
        self.clear(33.6, 0.4)

    # 34.00-45.00: name the idea, then show the two growth curves.
    def reveal(self) -> None:
        self.hold_until(35.4)
        headline = self.title("TIME COMPLEXITY")
        self.play(FadeIn(headline, shift=UP * 0.2), run_time=0.35)

        axes = Axes(
            x_range=[0, 64, 16], y_range=[0, 64, 16], x_length=6.6, y_length=5.0, tips=False,
            axis_config={"color": COLORS["textMuted"], "stroke_width": 3, "include_ticks": False,
                         "include_numbers": False},
        ).move_to([0.2, 0.55, 0])
        x_name = label("input size", 32, COLORS["textSecondary"]).next_to(axes, DOWN, buff=0.3)
        y_name = label("steps", 32, COLORS["textSecondary"]).next_to(axes, UP, buff=0.2).align_to(axes, LEFT)
        self.hold_until(36.0)
        self.play(Create(axes), FadeIn(x_name), FadeIn(y_name), run_time=0.8)

        scan_curve = axes.plot(lambda x: x, x_range=[0, 64], color=COLORS["textMuted"], stroke_width=6)
        split_curve = axes.plot(lambda x: math.log2(x), x_range=[1, 64], color=COLORS["textPrimary"],
                                stroke_width=6)
        scan_tag = label("O(n)", 40, COLORS["textSecondary"]).next_to(scan_curve.get_end(), LEFT, buff=0.1)
        scan_tag.shift(UP * 0.5 + LEFT * 0.3)
        split_tag = label("O(log n)", 40).next_to(split_curve.get_end(), UP, buff=0.2)
        split_tag.shift(LEFT * 0.9)
        self.hold_until(37.0)
        self.play(Create(scan_curve), run_time=1.3, rate_func=linear)
        self.play(FadeIn(scan_tag), run_time=0.25)
        self.hold_until(38.85)
        self.play(Create(split_curve), run_time=1.9, rate_func=linear)
        self.play(FadeIn(split_tag), run_time=0.25)
        question = label("Which would you rather scale?", 44).move_to(DOWN * 3.85)
        self.hold_until(41.4)
        self.play(FadeIn(question, shift=UP * 0.2), run_time=0.4)
        self.hold_until(45.0)
