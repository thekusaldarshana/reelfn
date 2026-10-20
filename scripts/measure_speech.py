"""Print where each narrated beat starts/ends and where the pauses are, so the
scene can be timed to the real voice instead of guessed.

Usage: .venv-audio/bin/python scripts/measure_speech.py output/audio/<name>-mix [--min-pause 0.2]
Also prints a suggested duration per beat (speech + 0.12 lead + 0.27 tail + 0.8 visual pad).
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

mix = Path(sys.argv[1])
min_pause = float(sys.argv[sys.argv.index("--min-pause") + 1]) if "--min-pause" in sys.argv else 0.2
manifest = json.loads((mix / "audio-manifest.json").read_text())
samples, rate = sf.read(mix / "narration.wav")
envelope = np.convolve(np.abs(samples), np.ones(int(0.03 * rate)) / int(0.03 * rate), "same")
silent = envelope < 0.004
pauses, i = [], 0
while i < len(silent):
    if silent[i]:
        j = i
        while j < len(silent) and silent[j]:
            j += 1
        if (j - i) / rate >= min_pause:
            pauses.append((i / rate, j / rate))
        i = j
    else:
        i += 1
for beat in manifest["beats"]:
    start, end = beat["start"], beat["start"] + beat["speechSeconds"]
    inside = [f"{a:.2f}-{b:.2f}" for a, b in pauses if start <= a <= end]
    print(f"{beat['id']:<10} speech {start:6.2f}-{end:6.2f}  suggested duration {beat['speechSeconds'] + 0.12 + 0.27 + 0.8:5.1f}s  pauses: {', '.join(inside)}")
print(f"total {manifest['durationSeconds']}s; keep the last narration end <= total - end-card seconds")
