---
name: youtube-av-separator
description: Download a YouTube video, evaluate whether audio quality is acceptable, then separate into muted video and standalone audio files. Use when users send YouTube links and ask to split video/audio only if audio quality is good enough.
---

# youtube-av-separator

## Workflow

1. Validate dependencies: `yt-dlp`, `ffmpeg`, `ffprobe`.
2. Run `scripts/youtube_split.py` with the YouTube URL.
3. Check `quality_passed` in JSON output.
4. If passed, return output file paths for:
   - `video_no_audio.mp4`
   - `audio.<format>`
5. If not passed, report the reason and do not claim split success.

## Command

```bash
python3 scripts/youtube-av-separator/scripts/youtube_split.py "<youtube_url>" --out "./tmp/youtube-split"
```

Common options:

- `--min-bitrate 128`
- `--min-duration 30`
- `--audio-format mp3|m4a|wav|flac`

## Quality policy

Read `references/quality-rules.md` when user asks to tune quality thresholds (music vs podcast vs low-quality sources).

## Response template

- If pass: "音频质量达标，已完成分离" + file paths + key metrics.
- If fail: "音频质量不达标，未执行分离" + failed reasons + metrics.
