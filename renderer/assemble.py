"""Build and probe a captioned, branded audiovisual preview from reviewed inputs.

Branding (caption colours and font, watermark, end card) comes from renderer/brand.py, so the
same pipeline produces an unbranded video, a text-branded one, or one with your own logo.
"""

import argparse
import json
import subprocess
import wave
from pathlib import Path

from brand import load_brand
from media_inspection import inspect_media, sha256


ROOT = Path(__file__).resolve().parents[1]


def pcm_rms(path: Path) -> float:
    import math
    import struct

    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2 or wav.getnchannels() != 1:
            raise ValueError(f"Expected mono PCM16 WAV: {path}")
        data = wav.readframes(wav.getnframes())
    samples = struct.iter_unpack("<h", data)
    squares = (sample[0] * sample[0] for sample in samples)
    return math.sqrt(sum(squares) / (len(data) // 2)) / 32768


def ass_colour(hex_colour: str) -> str:
    """#RRGGBB -> libass &HAABBGGRR (opaque)."""
    value = hex_colour.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Colours must be #RRGGBB, got {hex_colour}")
    return f"&H00{value[4:6]}{value[2:4]}{value[0:2]}".upper()


def text_mark(text: str, font_path: Path, colour: str, size: int, max_width: int, out: Path) -> Path:
    """Rasterise a text wordmark to a transparent PNG (used when no logo image is supplied)."""
    from PIL import Image, ImageDraw, ImageFont

    while True:
        font = ImageFont.truetype(str(font_path), size)
        try:
            font.set_variation_by_name("Bold")
        except (OSError, ValueError):
            pass  # not a variable font; use it as is
        left, top, right, bottom = font.getbbox(text)
        if right - left <= max_width or size <= 8:
            break
        size -= 2
    image = Image.new("RGBA", (right - left + 8, bottom - top + 8), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((4 - left, 4 - top), text, font=font, fill=colour)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    return out


def mark_input(mark: dict, brand: dict, out: Path, text_size: int, max_width: int) -> tuple[Path | None, str]:
    """Return (PNG path, ffmpeg filter that prepares it) for a watermark or end card, or (None, '')."""
    if mark["kind"] == "none":
        return None, ""
    key = ",colorkey=0x000000:0.08:0.02" if mark.get("keyOutBlack") else ""
    if mark["kind"] == "image":
        width = int(mark["width"])
        if not 32 <= width <= 540:
            raise ValueError("Logo and watermark widths must be between 32 and 540 pixels")
        return mark["path"], f"scale=w={width}:h={width * 2}:force_original_aspect_ratio=decrease,format=rgba{key}"
    png = text_mark(mark["text"], brand["fontPath"], brand["colors"]["textPrimary"], text_size, max_width, out)
    return png, "format=rgba"


def assemble(video: Path, audio: Path, captions: Path, output: Path, ffmpeg: str, ffprobe: str,
             end_card_seconds: float | None = None) -> None:
    for path in (video, audio, captions):
        if not path.is_file():
            raise FileNotFoundError(path)
    audio_manifest_path = audio.parent / "audio-manifest.json"
    audio_manifest = json.loads(audio_manifest_path.read_text(encoding="utf-8"))
    placeholder = audio_manifest.get("provider") == "placeholder"
    for name, minimum_rms in (("narration", 0.01), ("music", 0.002), ("effects", 0.001), ("mix", 0.01)):
        track = audio.parent / f"{name}.wav"
        recorded = audio_manifest["files"].get(name)
        if not recorded or not track.is_file() or sha256(track) != recorded["sha256"]:
            raise ValueError(f"Required {name} audio track is missing or changed")
        if pcm_rms(track) < minimum_rms and not (placeholder and name in ("narration", "mix")):
            raise ValueError(f"Required {name} audio track is too quiet")
    if sha256(audio) != audio_manifest["files"]["mix"]["sha256"]:
        raise ValueError("Mix hash does not match the audio manifest")
    output.parent.mkdir(parents=True, exist_ok=True)

    brand = load_brand()
    colours = brand["colors"]
    duration = float(audio_manifest["durationSeconds"])
    end_card = brand["endCard"]
    if end_card_seconds is None:
        end_card_seconds = float(end_card.get("seconds", 0))
    if end_card["kind"] == "none":
        end_card_seconds = 0.0
    if end_card_seconds < 0 or end_card_seconds >= duration:
        raise ValueError("End card length is outside the media duration")
    hide_at = duration - end_card_seconds

    # Run from ROOT so both paths in the subtitle filter are relative and work
    # the same way on Windows, macOS and Linux (no drive-letter escaping in FFmpeg).
    try:
        subtitle_path = captions.resolve().relative_to(ROOT).as_posix()
        font_dir = brand["fontPath"].parent.resolve().relative_to(ROOT).as_posix()
    except ValueError as error:
        raise ValueError("Captions and the brand font must live inside the reelfn folder") from error
    caption_margin_v = int(brand["captions"]["marginV"])
    if not 0 <= caption_margin_v <= 100:
        raise ValueError("Caption margin must be between 0 and 100")
    filter_graph = (
        f"[0:v]subtitles={subtitle_path}:fontsdir={font_dir}:"
        f"force_style='FontName={brand['font']['family']},FontSize={int(brand['captions']['fontSize'])},"
        f"PrimaryColour={ass_colour(colours['textPrimary'])},OutlineColour={ass_colour(colours['background'])},"
        f"BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV={caption_margin_v}'[base]"
    )

    inputs: list[str] = []
    cache = output.parent / "brand-cache"
    watermark = brand["watermark"]
    watermark_png, watermark_prep = mark_input(watermark, brand, cache / "watermark.png", 18, 200)
    if watermark_png:
        opacity = float(watermark["opacity"])
        if not 0.0 < opacity <= 1.0:
            raise ValueError("Watermark opacity must be between zero and one")
        index = 2 + len(inputs) // 6
        inputs += ["-loop", "1", "-framerate", "30", "-i", str(watermark_png)]
        filter_graph += (
            f";[{index}:v]{watermark_prep},colorchannelmixer=aa={opacity:.3f}[mark]"
            f";[base][mark]overlay=x=W-w-{int(watermark['insetX'])}:y={int(watermark['insetY'])}"
            f":enable='lt(t,{hide_at:.3f})'[branded]"
        )
    else:
        filter_graph += ";[base]null[branded]"
    end_png = None
    if end_card_seconds > 0:
        end_png, end_prep = mark_input(end_card, brand, cache / "end-card.png", 64, 460)
        index = 2 + len(inputs) // 6
        inputs += ["-loop", "1", "-framerate", "30", "-i", str(end_png)]
        background = colours["background"].lstrip("#")
        filter_graph += (
            f";[branded]drawbox=x=0:y=0:w=iw:h=ih:color=0x{background}:t=fill:enable='gte(t,{hide_at:.3f})'[endbase]"
            f";[{index}:v]{end_prep},fade=t=in:st={hide_at:.3f}:d=0.55:alpha=1[endlogo]"
            f";[endbase][endlogo]overlay=x=(W-w)/2:y=(H-h)/2:enable='gte(t,{hide_at:.3f})'[v]"
        )
    else:
        filter_graph += ";[branded]null[v]"

    subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(video), "-i", str(audio), *inputs,
            "-filter_complex", filter_graph, "-map", "[v]", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", str(duration), "-movflags", "+faststart", str(output),
        ],
        cwd=ROOT,
        check=True,
    )
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate", "-show_entries", "format=duration", "-of", "json", str(output)],
        capture_output=True,
        text=True,
        check=True,
    )
    media = json.loads(probe.stdout)
    streams = media["streams"]
    picture = next((stream for stream in streams if stream["codec_type"] == "video"), None)
    sound = next((stream for stream in streams if stream["codec_type"] == "audio"), None)
    if (
        not picture or not sound
        or picture.get("codec_name") != "h264" or sound.get("codec_name") != "aac"
        or picture.get("width") != 540 or picture.get("height") != 960
        or picture.get("r_frame_rate") != "30/1" or sound.get("sample_rate") != "48000"
        or abs(float(media["format"]["duration"]) - duration) > 0.05
    ):
        raise ValueError(f"Media probe failed: {media}")
    inspection = inspect_media(output, ffmpeg, ffprobe)
    manifest = {
        "videoSha256": sha256(video),
        "audioSha256": sha256(audio),
        "captionsSha256": sha256(captions),
        "brandSha256": {path.relative_to(ROOT).as_posix(): sha256(path) for path in brand["sources"]},
        "watermark": watermark["kind"],
        "watermarkSha256": sha256(watermark_png) if watermark_png else None,
        "endCard": end_card["kind"] if end_card_seconds > 0 else "none",
        "endCardSha256": sha256(end_png) if end_png else None,
        "endCardSeconds": end_card_seconds,
        "voiceProvider": audio_manifest.get("provider"),
        "audioManifestSha256": sha256(audio_manifest_path),
        "outputSha256": sha256(output),
        "inspectionSha256": sha256(output.with_name(output.stem + "-inspection.json")),
        "contactSheetSha256": inspection["contactSheetSha256"],
        "probe": media,
        "status": "placeholder voice: preview only, do not publish" if placeholder
        else "preview; visual, science, rights, and narration review still required",
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Assembled captioned audiovisual preview: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--end-card-seconds", type=float, default=None,
                        help="Override the brand's end card length (0 disables it)")
    args = parser.parse_args()
    assemble(args.video, args.audio, args.captions, args.out, args.ffmpeg, args.ffprobe, args.end_card_seconds)
