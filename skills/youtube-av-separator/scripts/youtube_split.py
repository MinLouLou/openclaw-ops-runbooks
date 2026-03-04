#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout


def check_bin(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing dependency: {name}")


def ffprobe_audio(path: Path):
    out = run([
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=bit_rate,sample_rate,channels,codec_name",
        "-show_entries", "format=duration",
        "-of", "json", str(path)
    ])
    data = json.loads(out)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    bit_rate = stream.get("bit_rate")
    if bit_rate is None:
        bit_rate = fmt.get("bit_rate")

    return {
        "codec": stream.get("codec_name"),
        "sample_rate": int(stream.get("sample_rate")) if stream.get("sample_rate") else None,
        "channels": stream.get("channels"),
        "bit_rate_kbps": round(int(bit_rate) / 1000, 2) if bit_rate else None,
        "duration_sec": round(float(fmt.get("duration", 0)), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Download YouTube video and split video/audio if audio quality is acceptable")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--out", default="./output", help="Output directory")
    parser.add_argument("--min-bitrate", type=float, default=128.0, help="Minimum audio bitrate (kbps)")
    parser.add_argument("--min-duration", type=float, default=30.0, help="Minimum duration in seconds")
    parser.add_argument("--audio-format", default="mp3", choices=["mp3", "m4a", "wav", "flac"], help="Audio export format")
    args = parser.parse_args()

    for b in ["yt-dlp", "ffmpeg", "ffprobe"]:
        check_bin(b)

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    source_video = out_dir / "source.mp4"
    source_audio = out_dir / "source_audio.m4a"

    # Download best mp4 video and best m4a audio separately for deterministic output.
    run([
        "yt-dlp",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4",
        "-o", str(source_video),
        args.url,
    ])

    run([
        "yt-dlp",
        "-f", "ba[ext=m4a]/ba/bestaudio",
        "-o", str(source_audio),
        args.url,
    ])

    metrics = ffprobe_audio(source_audio)

    passed = True
    reasons = []
    if metrics["bit_rate_kbps"] is None or metrics["bit_rate_kbps"] < args.min_bitrate:
        passed = False
        reasons.append(f"bitrate<{args.min_bitrate}kbps")
    if metrics["duration_sec"] < args.min_duration:
        passed = False
        reasons.append(f"duration<{args.min_duration}s")

    result = {
        "url": args.url,
        "output_dir": str(out_dir),
        "audio_metrics": metrics,
        "thresholds": {
            "min_bitrate_kbps": args.min_bitrate,
            "min_duration_sec": args.min_duration,
        },
        "quality_passed": passed,
        "reasons": reasons,
    }

    if passed:
        final_audio = out_dir / f"audio.{args.audio_format}"
        final_video = out_dir / "video_no_audio.mp4"

        # Export clean audio
        run([
            "ffmpeg", "-y", "-i", str(source_audio),
            str(final_audio),
        ])

        # Strip audio track from video
        run([
            "ffmpeg", "-y", "-i", str(source_video),
            "-an", "-c:v", "copy", str(final_video),
        ])

        result["outputs"] = {
            "video_no_audio": str(final_video),
            "audio": str(final_audio),
            "source_video": str(source_video),
            "source_audio": str(source_audio),
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 20)


if __name__ == "__main__":
    main()
