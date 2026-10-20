"""Create a reproducible visual review artifact using FFmpeg, without PyAV.

This reports technical facts and samples frames. It deliberately does not infer
that a dark frame, an intentional hold, or a readable caption is visually good.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_media(video: Path, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe") -> dict:
    video = video.resolve(strict=True)
    if not video.is_file():
        raise ValueError(f"Not a media file: {video}")

    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate",
         "-show_entries", "format=duration", "-of", "json", str(video)],
        check=True, capture_output=True, text=True,
    )
    media = json.loads(probe.stdout)
    picture = next((item for item in media.get("streams", []) if item.get("codec_type") == "video"), None)
    sound = next((item for item in media.get("streams", []) if item.get("codec_type") == "audio"), None)
    duration = float(media["format"]["duration"])
    if not picture or duration <= 0:
        raise ValueError("Media must have a positive duration and video stream")

    # Twelve equally spaced samples expose scene progression in one glance.
    # The review sheet is an aid, never evidence that every intermediate frame is sound.
    sample_count = 12
    interval = duration / sample_count
    sheet = video.with_name(video.stem + "-contact-sheet.png")
    report_path = video.with_name(video.stem + "-inspection.json")
    filter_graph = (
        f"fps=1/{interval:.9f},scale=270:480:flags=lanczos,"
        "tile=4x3:padding=4:margin=4:color=0x121212"
    )
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
         "-an", "-vf", filter_graph, "-frames:v", "1", "-update", "1", str(sheet)],
        check=True,
    )
    if not sheet.is_file() or sheet.stat().st_size == 0:
        raise ValueError("FFmpeg did not create a contact sheet")

    expected_format = (
        picture.get("codec_name") == "h264"
        and picture.get("width") == 540
        and picture.get("height") == 960
        and picture.get("r_frame_rate") == "30/1"
        and sound is not None
        and sound.get("codec_name") == "aac"
        and sound.get("sample_rate") == "48000"
    )
    report = {
        "schemaVersion": 1,
        "mediaSha256": sha256(video),
        "contactSheetFile": sheet.name,
        "contactSheetSha256": sha256(sheet),
        "sampling": {"count": sample_count, "intervalSeconds": interval, "method": "ffmpeg-fps-tile"},
        "technicalChecks": {"instagramPreviewFormat": "pass" if expected_format else "fail"},
        "probe": media,
        "reviewState": "unreviewed",
        "reviewRequired": ["visual continuity", "caption timing and readability", "science and visual agreement", "audio playback", "rights"],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not expected_format:
        raise ValueError(f"Media format failed; see {report_path}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    report = inspect_media(args.video, args.ffmpeg, args.ffprobe)
    print(json.dumps({"mediaSha256": report["mediaSha256"], "reviewState": report["reviewState"],
                      "contactSheetFile": report["contactSheetFile"]}))
