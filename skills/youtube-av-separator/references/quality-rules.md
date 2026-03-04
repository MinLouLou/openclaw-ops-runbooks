# Audio quality rules

Use these default thresholds unless user says otherwise:

- Minimum bitrate: 128 kbps
- Minimum duration: 30 seconds

Quick interpretation:

- `>=192 kbps`: great for music/voice
- `128-191 kbps`: acceptable for most spoken content
- `<128 kbps`: usually too compressed

Override policy:

- For podcasts/talk videos: allow 96 kbps if the source itself is low quality.
- For music extraction: keep minimum at 192 kbps.
