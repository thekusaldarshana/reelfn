"""Original, deterministic music and sound cues (no sample files, so no rights to clear)."""

import hashlib
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_tone(track: np.ndarray, rate: int, at: float, frequencies: tuple[float, ...], length: float, gain: float) -> None:
    count = int(rate * length)
    start = int(round(rate * at))
    if start + count > len(track):
        raise ValueError(f"Sound cue at {at}s exceeds the episode duration")
    time = np.arange(count, dtype=np.float64) / rate
    envelope = (1 - np.exp(-time * 90)) * np.exp(-time * 14)
    sound = sum(np.sin(2 * np.pi * frequency * time) for frequency in frequencies) / len(frequencies)
    track[start : start + count] += (gain * envelope * sound).astype(np.float32)


def make_music(length: int, rate: int, speech_spans: list[tuple[float, float]]) -> np.ndarray:
    """Original, deterministic four-chord bed with a soft plucked pulse."""
    music = np.zeros(length, dtype=np.float32)
    duration = length / rate
    # Dm7, G7, Cmaj7, Am7. MIDI notes make the score independent of sound files.
    base_chords = ((50, 57, 60, 65), (55, 59, 62, 65), (48, 55, 59, 64), (45, 52, 55, 60))
    chords = base_chords * (2 if duration >= 60 else 1)
    chord_seconds = duration / len(chords)
    for chord_index, chord in enumerate(chords):
        start_time = chord_index * chord_seconds
        start = int(round(start_time * rate))
        end = min(length, int(round((start_time + chord_seconds + 0.8) * rate)))
        t = np.arange(end - start, dtype=np.float64) / rate
        attack = np.minimum(1.0, t / 0.8)
        release = np.minimum(1.0, np.maximum(0.0, (chord_seconds + 0.8 - t) / 0.8))
        envelope = attack * release
        for note in chord:
            frequency = 440.0 * 2 ** ((note - 69) / 12)
            music[start:end] += (0.004 * envelope * (np.sin(2 * np.pi * frequency * t) + 0.16 * np.sin(4 * np.pi * frequency * t))).astype(np.float32)
        # A low root keeps the pulse felt without competing with speech.
        root = 440.0 * 2 ** ((chord[0] - 12 - 69) / 12)
        music[start:end] += (0.005 * envelope * np.sin(2 * np.pi * root * t)).astype(np.float32)

    for beat_index, at in enumerate(np.arange(0, duration, 0.625)):
        chord = chords[min(int(at / chord_seconds), len(chords) - 1)]
        note = chord[beat_index % len(chord)] + 12
        frequency = 440.0 * 2 ** ((note - 69) / 12)
        start = int(round(at * rate))
        count = min(int(rate * 0.28), length - start)
        t = np.arange(count, dtype=np.float64) / rate
        pluck = (1 - np.exp(-t * 120)) * np.exp(-t * 13)
        music[start : start + count] += (0.012 * pluck * np.sin(2 * np.pi * frequency * t)).astype(np.float32)

    # Keep the instrumental bed lower during spoken words, with smooth edges.
    gain = np.ones(length, dtype=np.float32)
    ramp = int(0.18 * rate)
    for start_seconds, end_seconds in speech_spans:
        start = max(0, int(start_seconds * rate))
        end = min(length, int(end_seconds * rate))
        gain[start:end] = np.minimum(gain[start:end], 0.38)
        before = max(0, start - ramp)
        if before < start:
            gain[before:start] = np.minimum(gain[before:start], np.linspace(1, 0.38, start - before, dtype=np.float32))
        after = min(length, end + ramp)
        if end < after:
            gain[end:after] = np.minimum(gain[end:after], np.linspace(0.38, 1, after - end, dtype=np.float32))
    return music * gain * 3.0


def make_timed_effects(length: int, rate: int, cues: list[float]) -> np.ndarray:
    """Soft two-note cues at the given times (by default, every beat change)."""
    effects = np.zeros(length, dtype=np.float32)
    for index, at in enumerate(cues):
        if not isinstance(at, (int, float)) or at < 0 or at + 0.35 > length / rate:
            raise ValueError(f"Invalid sound cue time: {at}")
        frequencies = (523.25, 783.99) if index % 2 == 0 else (659.25, 987.77)
        add_tone(effects, rate, float(at), frequencies, 0.28, 0.055)
    return effects * 1.6
