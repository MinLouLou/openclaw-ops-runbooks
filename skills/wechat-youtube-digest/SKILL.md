---
name: wechat-youtube-digest
description: Parse exported WeChat group chat text and generate a daily summary of messages containing YouTube links with nearby Chinese descriptions. Use when user wants daily/dated collection from WeChat logs but raw logs are already available as text.
---

# WeChat YouTube Digest

## Workflow

1. Ask for exported chat log text/file for a target date.
2. Run `scripts/parse_wechat_youtube.py` with `--date YYYY-MM-DD`.
3. Return grouped summary:
   - sender
   - time
   - description text near link
   - youtube url
4. Deduplicate by URL while preserving first occurrence.

## Script

Run:

```bash
python3 scripts/parse_wechat_youtube.py --input <log.txt> --date 2026-03-02
```

Optional:

- `--json` output machine-readable JSON
- `--keep-duplicates` keep all repeated URLs

## Notes

- This skill does **not** read WeChat desktop UI directly.
- It works on exported/copied logs.
