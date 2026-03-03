#!/usr/bin/env python3
import re
import json
import argparse
from pathlib import Path

YOUTUBE_RE = re.compile(r"https?://[^\s]*youtube[^\s]*", re.IGNORECASE)
TIME_LINE_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<sender>[^:：]+)[:：]\s*(?P<msg>.*)$")


def parse_lines(lines, target_date, keep_duplicates=False):
    rows = []
    seen = set()
    for line in lines:
        m = TIME_LINE_RE.match(line.strip())
        if not m:
            continue
        if m.group('date') != target_date:
            continue
        msg = m.group('msg')
        links = YOUTUBE_RE.findall(msg)
        if not links:
            continue
        for link in links:
            key = link.strip()
            if (not keep_duplicates) and key in seen:
                continue
            seen.add(key)
            desc = msg.replace(link, '').strip(' -，,。;；:：')
            rows.append({
                'date': m.group('date'),
                'time': m.group('time'),
                'sender': m.group('sender').strip(),
                'description': desc,
                'url': key
            })
    return rows


def to_markdown(rows):
    if not rows:
        return "未发现符合条件的 YouTube 消息。"
    out = ["# WeChat YouTube 汇总", ""]
    for i, r in enumerate(rows, 1):
        out.append(f"{i}. [{r['time']}] {r['sender']}")
        out.append(f"   - 描述：{r['description'] or '（无）'}")
        out.append(f"   - 链接：{r['url']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--date', required=True, help='YYYY-MM-DD')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--keep-duplicates', action='store_true')
    args = ap.parse_args()

    text = Path(args.input).read_text(encoding='utf-8', errors='ignore')
    rows = parse_lines(text.splitlines(), args.date, args.keep_duplicates)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(rows))


if __name__ == '__main__':
    main()
