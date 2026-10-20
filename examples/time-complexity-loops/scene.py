"""Time complexity through duplicate detection: pair comparisons versus a set scan.

Quantities come from the validated `episode.json` (every step count and
run time there has a deterministic `operation-count` check at the stated 200,000,000 steps/s).
Cues are absolute times measured from the narration (scripts/measure_speech.py).
"""

from manim import (
    DOWN, UP, AnimationGroup, Arrow, Create, FadeIn, FadeOut, Line, RoundedRectangle, Succession,
    Wait,
)

from reel_kit import (
    COLORS, LEFT_X, RIGHT_X, TITLE_Y, CodeBlock, ReelScene, label, left, right,
)

LOOP_ONE = ["seen = set()", "for x in items:", "    if x in seen: return True", "    seen.add(x)"]
LOOP_TWO = ["for i in range(n):", "    for j in range(i + 1, n):", "        if a[i] == a[j]: return True"]
A_Y, B_Y = 2.9, -0.65          # code panel centres, shared by hook and reveal for continuity
A_TAG_Y, B_TAG_Y = 1.0, -2.3  # counters/tags below each panel


class TimeComplexityLoops(ReelScene):
    def construct(self) -> None:
        self.camera.background_color = COLORS["background"]
        self.hook()
        self.grow()
        self.reveal()
        self.years()
        self.fix()
        self.close()

    # 0-10: the situation, then one loop vs a loop inside a loop.
    def hook(self) -> None:
        title = self.title("1,000 distinct items")
        rows = [label(t, 38, COLORS["textSecondary"], width=3.0) for t in ("item 1", "item 2", "item 3", "...", "item 1,000")]
        stack = []
        for i, row in enumerate(rows):
            box = RoundedRectangle(width=4.2, height=0.85, corner_radius=0.18, stroke_color=COLORS["textMuted"],
                                   stroke_width=2).move_to([0, 3.1 - i * 1.05, 0])
            stack.append(row.move_to(box))
            stack.append(box)
        self.add(title, *stack)  # the first frame already shows the situation
        self.hold_until(1.6)
        self.play(FadeOut(*stack), run_time=0.3)

        block_a = CodeBlock(LOOP_ONE, A_Y)
        block_b = CodeBlock(LOOP_TWO, B_Y)
        count_a = right(label("2,000 ops", 40), A_TAG_Y)
        count_b = right(label("499,500 checks", 40), B_TAG_Y)
        self.hold_until(1.9)
        self.play(FadeIn(block_a), run_time=0.3)
        self.play(FadeIn(count_a), run_time=1.4)
        self.hold_until(3.63)
        self.play(FadeIn(block_b), run_time=0.3)
        self.hold_until(4.93)
        self.play(FadeIn(count_b), run_time=1.3)
        same = label("Same duplicate check", 52).move_to(DOWN * 3.6)
        self.hold_until(6.5)
        self.play(FadeIn(same, shift=UP * 0.2), run_time=0.35)
        self.clear(9.55, 0.4)

    # 10-19: ten times the items -> x10 set operations vs about x100 pair checks.
    def grow(self) -> None:
        self.hold_until(10.2)
        head = self.title("10,000 distinct items")
        self.play(FadeIn(head, shift=UP * 0.2), run_time=0.3)

        def row(name: str, y: float, old: str, new: str, badge: str):
            tag = left(label(name, 32, COLORS["textSecondary"]), y + 0.75)
            before = left(label(old, 40, COLORS["textSecondary"], width=4.6), y)
            after = left(label(new, 56, width=3.2), y - 0.95)
            gain = right(label(badge, 96), y - 0.95)
            return tag, before, after, gain

        l_tag, l_old, l_new, l_gain = row("SET SCAN", 3.0, "2,000 ops", "20,000 ops", "x10")
        r_tag, r_old, r_new, r_gain = row("EVERY PAIR", -0.6, "499,500 checks", "49,995,000 checks", "~x100")
        self.hold_until(10.6)
        self.play(FadeIn(l_tag), FadeIn(l_old), run_time=0.3)
        self.hold_until(11.73)
        self.play(FadeIn(l_new, shift=UP * 0.15), FadeIn(l_gain, scale=0.8), run_time=0.5)
        self.hold_until(12.6)
        self.play(FadeIn(r_tag), FadeIn(r_old), run_time=0.3)
        self.hold_until(13.96)
        self.play(FadeIn(r_new, shift=UP * 0.15), FadeIn(r_gain, scale=0.8), run_time=0.5)
        self.clear(18.55, 0.4)

    # 19-29: name the idea after the mechanism; annotate each loop with its Big O.
    def reveal(self) -> None:
        self.hold_until(19.1)
        prompt = label("how duplicate checks grow", 34, COLORS["textSecondary"]).move_to(UP * TITLE_Y)
        block_a, block_b = CodeBlock(LOOP_ONE, A_Y), CodeBlock(LOOP_TWO, B_Y)
        self.play(FadeIn(prompt), FadeIn(block_a), FadeIn(block_b), run_time=0.4)
        self.hold_until(22.3)
        name = self.title("TIME COMPLEXITY")
        self.play(FadeOut(prompt), FadeIn(name, shift=UP * 0.2), run_time=0.35)
        self.hold_until(23.77)
        self.play(FadeIn(right(label("avg O(n)", 52), A_TAG_Y), shift=UP * 0.15), run_time=0.3)
        self.hold_until(25.0)
        self.play(FadeIn(right(label("O(n²)", 60), B_TAG_Y), shift=UP * 0.15), run_time=0.3)
        self.clear(28.55, 0.4)

    # 29-43: the same duplicate check at a million and a billion distinct items.
    def years(self) -> None:
        self.hold_until(29.1)
        rate = self.title("Hypothetical: 200M ops/s", 44)
        self.play(FadeIn(rate, shift=UP * 0.2), run_time=0.4)
        assumption = label("equal-cost ops; no duplicates", 30, COLORS["textSecondary"]).move_to(UP * 4.05)
        self.play(FadeIn(assumption), run_time=0.25)

        col1, col2, head_y = -0.5, 2.45, 2.5
        row1, row2 = 0.55, -1.75

        def header(number: str, x: float):
            top = label(number, 34, width=2.8).move_to([x, head_y + 0.2, 0])
            sub = label("distinct items", 25, COLORS["textSecondary"]).move_to([x, head_y - 0.35, 0])
            return top, sub

        def value(text: str, x: float, y: float, size: int = 56):
            return label(text, size, width=2.8).move_to([x, y, 0])

        h1, h2 = header("1,000,000", col1), header("1,000,000,000", col2)
        grid = [Line([LEFT_X, 1.6, 0], [RIGHT_X + 0.5, 1.6, 0], color=COLORS["textMuted"], stroke_width=2),
                Line([LEFT_X, -0.6, 0], [RIGHT_X + 0.5, -0.6, 0], color=COLORS["border"], stroke_width=2)]
        names = [left(label("set scan", 28), row1, x=-4.0), left(label("pair checks", 28), row2, x=-4.0)]
        self.hold_until(32.6)
        self.play(*[Create(line) for line in grid], *[FadeIn(n) for n in names], run_time=0.3)
        self.hold_until(32.87)
        self.play(FadeIn(h1[0]), FadeIn(h1[1]), run_time=0.3)
        self.hold_until(34.11)
        self.play(FadeIn(value("10 ms", col1, row1), shift=UP * 0.15), run_time=0.3)
        self.hold_until(35.0)
        self.play(FadeIn(value("~42 min", col1, row2), shift=UP * 0.15), run_time=0.3)
        self.hold_until(36.46)
        self.play(FadeIn(h2[0]), FadeIn(h2[1]), run_time=0.3)
        self.hold_until(37.75)
        self.play(FadeIn(value("10 s", col2, row1), shift=UP * 0.15), run_time=0.3)
        self.hold_until(39.2)
        self.play(FadeIn(value("~79 years", col2, row2, 52), scale=0.85), run_time=0.45)
        self.clear(42.55, 0.4)

    # 43-56: same task, nested loop vs a set.
    def fix(self) -> None:
        self.hold_until(43.2)
        head = self.title("Prove no duplicates")
        self.play(FadeIn(head, shift=UP * 0.2), run_time=0.35)
        nested = CodeBlock(["for i in range(n):", "    for j in range(i + 1, n):", "        if a[i] == a[j]:",
                            "            return True"], 2.6, size=28)
        one_pass = CodeBlock(["seen = set()", "for x in a:", "    if x in seen:", "        return True",
                              "    seen.add(x)"], -1.65, size=28)
        self.hold_until(44.05)
        self.play(FadeIn(nested), run_time=0.4)
        self.hold_until(45.33)
        pairs = right(label("n(n-1)/2 pairs: O(n²)", 32, COLORS["textSecondary"]), 0.85)
        self.play(*nested.focus(0, 1), FadeIn(pairs), run_time=0.4)
        self.hold_until(47.7)
        self.play(*[line.animate.set_opacity(0.3) for line in nested.lines], FadeIn(one_pass), run_time=0.4)
        self.hold_until(48.2)
        self.play(*one_pass.focus(0, 4), run_time=0.3)
        self.hold_until(49.95)
        self.play(*one_pass.focus(2), run_time=0.3)
        self.hold_until(52.4)
        self.play(*one_pass.all_bright(), FadeIn(right(label("avg O(n)", 56), -3.95), shift=UP * 0.15),
                  FadeIn(left(label("2n modeled ops", 40, COLORS["textSecondary"]), -3.95), shift=UP * 0.15), run_time=0.35)
        self.clear(55.55, 0.4)

    # 56-64: same answer, years become seconds; the closing question runs into the end card.
    def close(self) -> None:
        self.hold_until(56.15)
        same = label("SAME DUPLICATE CHECK", 60).move_to(UP * 3.9)
        self.play(FadeIn(same, shift=UP * 0.2), run_time=0.35)
        self.hold_until(57.36)
        years = label("~79 years", 80, COLORS["textSecondary"], width=6.6).move_to(UP * 1.7)
        self.play(FadeIn(years), run_time=0.3)
        self.hold_until(58.0)
        drop = Arrow([0, 0.75, 0], [0, -0.05, 0], color=COLORS["textPrimary"], buff=0, stroke_width=5)
        seconds = label("10 seconds", 96, width=6.6).move_to(DOWN * 1.2)
        self.play(Create(drop), FadeIn(seconds, shift=UP * 0.2), run_time=0.45)
        model = label("hypothetical equal-cost operations", 29, COLORS["textSecondary"]).move_to(DOWN * 2.35)
        self.play(FadeIn(model), run_time=0.25)
        self.hold_until(59.3)
        ask = [label("Which method would", 48).move_to(DOWN * 3.2), label("you choose?", 48).move_to(DOWN * 3.95)]
        self.play(*[FadeIn(line, shift=UP * 0.2) for line in ask], run_time=0.4)
        self.hold_until(64.0)
