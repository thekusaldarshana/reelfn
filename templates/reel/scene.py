"""Scene for the "__SLUG__" reel. Replace the sections with your own animation.

Workflow: generate and measure the narration first (npm run reel -- voice __SLUG__, then mix), then put the measured
times in CUES. Every cue is an absolute time in seconds in the final video; hold_until() raises if a
previous animation ran past it. Keep the last animation <= total - end-card seconds (default 2).
"""

from manim import DOWN, UP, FadeIn, ValueTracker, linear

from reel_kit import COLORS, CodeBlock, ReelScene, counter, label

CUES = {"code": 1.5, "count": 2.0, "question": 30.0, "end": 42.0}  # replace with measured times; "end" = durationSeconds


class __CLASS__(ReelScene):
    def construct(self) -> None:
        self.camera.background_color = COLORS["background"]
        # The first frame must already show the situation (no title card): add, don't animate, at t=0.
        title = self.title("Your hook, as a situation")
        self.add(title)

        self.hold_until(CUES["code"])
        block = CodeBlock(["for item in items:", "    handle(item)"], 2.9)
        self.play(FadeIn(block), run_time=0.3)

        steps = ValueTracker(0)
        number = counter(steps, 1.5, 40, " steps")
        self.hold_until(CUES["count"])
        self.play(FadeIn(number), run_time=0.3)  # fade a counter in BEFORE animating its tracker, never in the same play
        self.play(steps.animate(run_time=1.2, rate_func=linear).set_value(1_000))

        self.hold_until(CUES["question"])
        ask = label("Closing question?", 48).move_to(DOWN * 3.2)
        self.play(FadeIn(ask, shift=UP * 0.2), run_time=0.4)
        self.hold_until(CUES["end"])  # total episode length
