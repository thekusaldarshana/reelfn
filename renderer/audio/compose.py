"""Place provider-generated beat WAVs, music, and cues on the episode timeline."""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from sound import make_music, make_timed_effects, sha256


def load_beat(path: Path, rate: int, allowed_seconds: float, ffmpeg: str, temp_parent: Path) -> tuple[np.ndarray, float]:
    samples, actual_rate = sf.read(path, dtype="float32")
    if actual_rate != rate or samples.ndim != 1:
        raise ValueError(f"{path} must be mono {rate}Hz WAV")
    ratio = (len(samples) / rate) / allowed_seconds
    if ratio > 1.0:
        if ratio > 1.15:
            raise ValueError(f"{path} needs {ratio:.2f}x time compression, above the 1.15x review limit")
        speed = ratio * 1.01
        faster = temp_parent / f"_stretched_{path.stem}.wav"
        subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-filter:a", f"atempo={speed:.6f}", str(faster)],
            check=True,
        )
        samples, actual_rate = sf.read(faster, dtype="float32")
        faster.unlink()
        if actual_rate != rate:
            raise ValueError("FFmpeg changed the sample rate")
        if len(samples) / rate > allowed_seconds:
            raise ValueError(f"{path} still overruns after bounded time compression")
        return samples, speed
    return samples, 1.0


def compose(episode_path: Path, provider_dir: Path, out_dir: Path, ffmpeg: str) -> None:
    episode = json.loads(episode_path.read_text(encoding="utf-8"))
    provider = json.loads((provider_dir / "provider-manifest.json").read_text(encoding="utf-8"))
    if provider.get("complete") is not True:
        raise ValueError("Provider audio is incomplete; resume TTS before composing")
    if provider["episodeSha256"] != sha256(episode_path):
        raise ValueError("The TTS audio was generated from a different episode revision")
    out_dir.mkdir(parents=True, exist_ok=True)
    rate = 24000
    duration = float(episode["durationSeconds"])
    length = int(round(duration * rate))
    narration = np.zeros(length, dtype=np.float32)
    placements = []
    spans = []
    for beat in episode["beats"]:
        source = provider_dir / f"{beat['id']}.wav"
        expected = next((entry for entry in provider["files"] if entry["id"] == beat["id"]), None)
        if expected is None or sha256(source) != expected["sha256"]:
            raise ValueError(f"Missing or changed provider audio for {beat['id']}")
        allowed = float(beat["duration"]) - 0.27
        samples, speed = load_beat(source, rate, allowed, ffmpeg, out_dir)
        start = int(round((float(beat["start"]) + 0.12) * rate))
        end = start + len(samples)
        if end > length or np.any(narration[start:end]):
            raise ValueError(f"Narration overlaps or exceeds the episode for {beat['id']}")
        narration[start:end] = samples
        spans.append((start / rate, end / rate))
        placements.append({"id": beat["id"], "start": start / rate, "speechSeconds": len(samples) / rate, "tempoFactor": speed})

    music = make_music(length, rate, spans)
    # One soft cue where each beat (and so each idea) changes.
    effects = make_timed_effects(length, rate, [float(beat["start"]) for beat in episode["beats"]])
    mix = narration + music + effects
    peak = float(np.max(np.abs(mix)))
    if peak == 0:
        raise ValueError("Audio mix is silent")
    if peak > 0.92:
        scale = 0.92 / peak
        narration *= scale
        music *= scale
        effects *= scale
        mix *= scale
    files = {}
    for name, samples in (("narration", narration), ("music", music), ("effects", effects), ("mix", mix)):
        path = out_dir / f"{name}.wav"
        sf.write(path, samples, rate, subtype="PCM_16")
        files[name] = {"path": str(path), "sha256": sha256(path)}
    manifest = {
        "episodeSlug": episode["slug"],
        "episodeSha256": sha256(episode_path),
        "providerManifestSha256": sha256(provider_dir / "provider-manifest.json"),
        "provider": provider["provider"],
        "model": provider["model"],
        "voice": provider["voice"],
        "durationSeconds": duration,
        "sampleRate": rate,
        "beats": placements,
        "files": files,
    }
    (out_dir / "audio-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Composed {duration:.1f}s narrator, music, and effects: {out_dir / 'mix.wav'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", type=Path, required=True)
    parser.add_argument("--provider-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    compose(args.episode, args.provider_dir, args.out, args.ffmpeg)
