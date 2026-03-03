#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s]*youtube[^\s]*", re.IGNORECASE)
TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")


def get_clipboard() -> str:
    return subprocess.check_output(["pbpaste"]).decode("utf-8", errors="ignore").strip()


def derive_desc(chunk: str, url: str) -> tuple[str, str]:
    lines = [l.strip() for l in chunk.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if url in line:
            core = line.replace(url, "").strip(" -，,。;；:：")
            prev_line = lines[i - 1] if i - 1 >= 0 else ""
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            desc = core or prev_line or next_line
            tm = TIME_RE.search(line) or TIME_RE.search(prev_line) or TIME_RE.search(next_line)
            return desc, (tm.group(0) if tm else "")
    tm = TIME_RE.search(chunk)
    return "", (tm.group(0) if tm else "")


def extract_items(chunks: list[str], dedup=True):
    items = []
    seen = set()
    for idx, c in enumerate(chunks, 1):
        urls = URL_RE.findall(c)
        for u in urls:
            key = u.strip()
            if dedup and key in seen:
                continue
            seen.add(key)
            desc, tm = derive_desc(c, key)
            items.append({
                "index": idx,
                "time": tm,
                "description": desc,
                "url": key,
            })
    return items


def to_markdown(date_str: str, items: list[dict]) -> str:
    out = [f"# 风向标 YouTube 汇总（{date_str}）", ""]
    if not items:
        out.append("未采集到包含 youtube 的结果。")
        return "\n".join(out)

    for i, it in enumerate(items, 1):
        t = f"[{it['time']}] " if it['time'] else ""
        out.append(f"{i}. {t}{it['description'] or '（描述缺失）'}")
        out.append(f"   - {it['url']}")
    return "\n".join(out)


def main():
    today = dt.datetime.now().date()
    yday = today - dt.timedelta(days=1)

    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=str(yday), help="汇总日期标记（默认昨天，YYYY-MM-DD）")
    ap.add_argument("--keep-duplicates", action="store_true")
    args = ap.parse_args()

    base = Path(__file__).resolve().parent
    out_dir = base / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_file = out_dir / f"raw-{args.date}.txt"
    md_file = out_dir / f"summary-{args.date}.md"

    print("\n=== 采集开始 ===")
    print("每次在微信复制一屏搜索结果后，回终端按回车采集。")
    print("输入 q 然后回车结束。\n")

    chunks = []
    last = None
    while True:
        cmd = input("回车采集 / q结束 > ").strip().lower()
        if cmd == "q":
            break
        clip = get_clipboard()
        if not clip:
            print("剪贴板为空，跳过。")
            continue
        if clip == last:
            print("和上次相同，跳过。")
            continue
        chunks.append(clip)
        last = clip
        print(f"已采集 {len(chunks)} 段。")

    raw_file.write_text("\n\n===== CHUNK =====\n\n".join(chunks), encoding="utf-8")

    items = extract_items(chunks, dedup=not args.keep_duplicates)
    md = to_markdown(args.date, items)
    md_file.write_text(md, encoding="utf-8")

    print("\n=== 完成 ===")
    print(f"原始文件: {raw_file}")
    print(f"汇总文件: {md_file}")
    print(f"提取条数: {len(items)}")


if __name__ == "__main__":
    main()
