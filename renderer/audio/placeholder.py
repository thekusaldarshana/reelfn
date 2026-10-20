"""Placeholder narration: silent beat WAVs timed at a typical speaking pace.

Use it to try the whole pipeline (render, captions, assembly) without an API key, or to rough out
timing before spending real TTS quota. The final video is marked as a placeholder and must not be
published: it has music, sound cues and captions, but no voice.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from sound import sha256

RATE = 24000
WORDS_PER_SECOND = 2.1  # measured narration pace is about 1.9-2.2 words per second


def main(episode_path: Path, out_dir: Path) -> None:
    episode = json.loads(episode_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for beat in episode["beats"]:
        allowed = float(beat["duration"]) - 0.27
        seconds = min(len(beat["narration"].split()) / WORDS_PER_SECOND, allowed)
        path = out_dir / f"{beat['id']}.wav"
        sf.write(path, np.zeros(max(1, int(seconds * RATE)), dtype=np.float32), RATE, subtype="PCM_16")
        files.append({"id": beat["id"], "path": str(path), "sha256": sha256(path),
                      "inputSha256": hashlib.sha256(beat["narration"].encode()).hexdigest()})
    manifest = {"provider": "placeholder", "model": "none", "voice": "none", "episodeSha256": sha256(episode_path),
                "complete": True, "files": files}
    (out_dir / "provider-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(files)} silent placeholder beats (no voice; preview only): {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    main(args.episode, args.out)
