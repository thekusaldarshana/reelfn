"""Make approximate, short reading captions from a timed narration manifest."""

import argparse
import json
from pathlib import Path

from sound import sha256


def stamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def chunks(words: list[str]) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    for word in words:
        if current and (len(current) >= 5 or len(" ".join(current + [word])) > 27):
            result.append(current)
            current = []
        current.append(word)
    if current:
        result.append(current)
    return result


def build(episode_path: Path, audio_manifest_path: Path, output_path: Path) -> None:
    episode = json.loads(episode_path.read_text(encoding="utf-8"))
    manifest = json.loads(audio_manifest_path.read_text(encoding="utf-8"))
    if manifest["episodeSha256"] != sha256(episode_path):
        raise ValueError("Audio was generated from a different episode revision")
    timings = {item["id"]: item for item in manifest["beats"]}
    lines = []
    index = 1
    for beat in episode["beats"]:
        timing = timings[beat["id"]]
        groups = chunks(beat["narration"].split())
        total_words = sum(len(group) for group in groups)
        cursor = float(timing["start"])
        end = cursor + float(timing["speechSeconds"])
        for group_index, group in enumerate(groups):
            next_time = end if group_index == len(groups) - 1 else cursor + float(timing["speechSeconds"]) * len(group) / total_words
            # Distribute by cumulative word share, rather than repeatedly using
            # the full duration from the current cursor.
            if group_index < len(groups) - 1:
                words_so_far = sum(len(part) for part in groups[: group_index + 1])
                next_time = float(timing["start"]) + float(timing["speechSeconds"]) * words_so_far / total_words
            lines.extend((str(index), f"{stamp(cursor)} --> {stamp(next_time)}", " ".join(group), ""))
            cursor = next_time
            index += 1
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    (output_path.parent / "caption-manifest.json").write_text(
        json.dumps({
            "episodeSha256": sha256(episode_path),
            "audioManifestSha256": sha256(audio_manifest_path),
            "srtSha256": sha256(output_path),
            "timingMethod": "word-proportional approximation; human sync review required",
            "cueCount": index - 1,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {index - 1} caption cues: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", type=Path, required=True)
    parser.add_argument("--audio-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.episode, args.audio_manifest, args.out)
