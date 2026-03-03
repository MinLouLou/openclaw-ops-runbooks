#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import subprocess
import time
from pathlib import Path

from AppKit import NSPasteboard, NSStringPboardType
from Quartz.CoreGraphics import (
    CGEventCreateMouseEvent,
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetIntegerValueField,
    CGEventSetFlags,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventMouseMoved,
    kCGEventScrollWheel,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
    kCGKeyboardEventAutorepeat,
)

KEYCODE = {
    'v': 9,
    'c': 8,
    'a': 0,
    'f': 3,
    'return': 36,
}
CMD_FLAG = 0x100000


def activate_wechat():
    # Step 1: always launch WeChat first, then wait until it's frontmost.
    subprocess.run(["open", "-a", "/Applications/WeChat.app"], check=False)
    time.sleep(1.0)

    for _ in range(6):
        subprocess.run(["osascript", "-e", 'tell application "WeChat" to activate'], check=False)
        time.sleep(0.5)
        front = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "System Events" to get name of first application process whose frontmost is true'
        ]).decode("utf-8", errors="ignore").strip()
        if "WeChat" in front or "微信" in front:
            return

    raise RuntimeError("无法将微信置前：请先手动打开 WeChat 并授予辅助功能权限")


def move_and_click(x, y):
    evt = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, evt)
    time.sleep(0.03)
    down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, (x, y), kCGMouseButtonLeft)
    up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def key_tap(key, cmd=False):
    code = KEYCODE[key]
    down = CGEventCreateKeyboardEvent(None, code, True)
    up = CGEventCreateKeyboardEvent(None, code, False)
    if cmd:
        CGEventSetFlags(down, CMD_FLAG)
        CGEventSetFlags(up, CMD_FLAG)
    CGEventSetIntegerValueField(down, kCGKeyboardEventAutorepeat, 0)
    CGEventSetIntegerValueField(up, kCGKeyboardEventAutorepeat, 0)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def set_clipboard(text: str):
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setString_forType_(text, NSStringPboardType)


def get_clipboard() -> str:
    pb = NSPasteboard.generalPasteboard()
    s = pb.stringForType_(NSStringPboardType)
    return (s or '').strip()


def paste_text(text: str):
    set_clipboard(text)
    time.sleep(0.05)
    key_tap('v', cmd=True)


def select_all_and_paste(text: str):
    key_tap('a', cmd=True)
    time.sleep(0.04)
    paste_text(text)


def scroll(pixels: int):
    evt = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (0, 0), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, evt)
    wheel = CGEventCreateMouseEvent(None, kCGEventScrollWheel, (0, 0), kCGMouseButtonLeft)
    # fallback: use osascript for reliable scroll simulation
    direction = "-1" if pixels < 0 else "1"
    lines = str(max(1, abs(pixels)//80))
    subprocess.run(["osascript", "-e", f'tell application "System Events" to key code 125'], check=False)
    # keep simple: down key once after block; real scroll is app-specific


def run(cfg, group, keyword, max_items, until_step=999):
    c = cfg['coords']
    d_click = cfg.get('click_delay_ms', 220) / 1000
    d_copy = cfg.get('copy_delay_ms', 250) / 1000
    scroll_every = int(cfg.get('scroll_every', 8))

    activate_wechat()

    # 1-2) 先尝试直接点击聊天列表中的目标群（你指定固定坐标）
    if 'group_chat_item' in c:
        move_and_click(*c['group_chat_item'])
        time.sleep(0.8)
    else:
        # fallback: 搜群名 -> 点第一条结果
        move_and_click(*c['chat_search_box'])
        time.sleep(d_click)
        select_all_and_paste(group)
        time.sleep(d_click)
        if 'chat_result_first_item' in c:
            move_and_click(*c['chat_result_first_item'])
            time.sleep(0.8)
        else:
            key_tap('return')
            time.sleep(0.8)

    if until_step <= 2:
        return []

    # 3) 点击右上角三个点
    if 'top_right_more_btn' in c:
        move_and_click(*c['top_right_more_btn'])
        time.sleep(d_click)

    # 4) 点击“查找聊天内容”
    if 'find_chat_content_btn' in c:
        move_and_click(*c['find_chat_content_btn'])
        time.sleep(0.6)

    # 5) 在聊天搜索框输入 keyword
    move_and_click(*c['inchat_search_box'])
    time.sleep(d_click)
    select_all_and_paste(keyword)
    time.sleep(d_click)
    key_tap('return')
    time.sleep(0.8)

    x1, y1 = c['result_first_item']
    x2, y2 = c['result_next_item']
    row_h = max(20, abs(y2 - y1))

    captured = []
    seen = set()

    for i in range(max_items):
        y = y1 + (i % scroll_every) * row_h
        move_and_click(x1, y)
        time.sleep(d_click)
        key_tap('c', cmd=True)
        time.sleep(d_copy)
        txt = get_clipboard()
        if txt and txt not in seen:
            seen.add(txt)
            captured.append(txt)

        if (i + 1) % scroll_every == 0:
            # 尽量推动列表继续向下：按一次下方向键
            subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 125'], check=False)
            time.sleep(0.25)

    return captured


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--group', required=True)
    ap.add_argument('--keyword', default='youtube')
    ap.add_argument('--max-items', type=int, default=120)
    ap.add_argument('--until-step', type=int, default=999, help='仅执行到某一步后停止（如 2）')
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    out_dir = Path(__file__).resolve().parent.parent / 'output'
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = str(dt.date.today())
    raw_file = out_dir / f'rpa-raw-{date_str}.txt'

    rows = run(cfg, args.group, args.keyword, args.max_items, args.until_step)
    raw_file.write_text('\n\n===== ITEM =====\n\n'.join(rows), encoding='utf-8')

    print(f'采集完成，条数: {len(rows)}')
    print(f'文件: {raw_file}')


if __name__ == '__main__':
    main()
