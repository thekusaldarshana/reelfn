"""Offline narration with Kokoro (experimental). Writes beat WAVs in the same format as gemini.mjs.

Install with `npm run setup -- --local-voice`, then download the two model files described in
renderer/audio/MODELS.md into .tools/kokoro/. Choose it with "voice": {"provider": "kokoro", "voice": "af_sarah"}
in brand/brand.json.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import soundfile as sf

from sound import ROOT, sha256

sys.path.insert(0, str(ROOT / "renderer"))
from brand import load_brand  # noqa: E402

MODEL_DIR = ROOT / ".tools" / "kokoro"


def main(episode_path: Path, out_dir: Path) -> None:
    try:
        from kokoro_onnx import Kokoro
    except ImportError as error:
        raise SystemExit("Kokoro is not installed. Run: npm run setup -- --local-voice") from error
    model, voices = MODEL_DIR / "kokoro-v1.0.onnx", MODEL_DIR / "voices-v1.0.bin"
    if not model.is_file() or not voices.is_file():
        raise SystemExit(f"Kokoro model files are missing from {MODEL_DIR}. See renderer/audio/MODELS.md")
    profile = load_brand()["voice"]
    voice = profile.get("voice") if profile.get("provider") == "kokoro" else "af_sarah"
    kokoro = Kokoro(str(model), str(voices))
    if voice not in kokoro.get_voices():
        raise SystemExit(f"Unknown Kokoro voice '{voice}'. Available: {', '.join(sorted(kokoro.get_voices()))}")
    episode = json.loads(episode_path.read_text(encoding="utf-8"))
    language = "en-us" if episode.get("language", "en").startswith("en") else episode["language"]
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for beat in episode["beats"]:
        speed = float(beat.get("delivery", {}).get("localSpeed", 1.08))
        samples, rate = kokoro.create(beat["narration"], voice=voice, speed=speed, lang=language)
        if rate != 24000:
            raise ValueError(f"Expected 24000Hz from Kokoro, got {rate}Hz")
        path = out_dir / f"{beat['id']}.wav"
        sf.write(path, samples, rate, subtype="PCM_16")
        files.append({"id": beat["id"], "path": str(path), "sha256": sha256(path),
                      "inputSha256": hashlib.sha256(f"{voice}|{speed}|{beat['narration']}".encode()).hexdigest()})
        print(f"Saved {beat['id']} local voice audio")
    manifest = {"provider": "kokoro-onnx", "model": "kokoro-v1.0", "voice": voice, "episodeSha256": sha256(episode_path),
                "modelSha256": sha256(model), "voicesSha256": sha256(voices), "complete": True, "files": files}
    (out_dir / "provider-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    main(args.episode, args.out)
