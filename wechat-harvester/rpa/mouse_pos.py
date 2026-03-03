#!/usr/bin/env python3
from AppKit import NSEvent
import time

print('移动鼠标到目标位置，Ctrl+C 退出')
while True:
    p = NSEvent.mouseLocation()
    # AppKit 原点在左下，直接给绝对坐标用于 CGEvent
    print(f'X={int(p.x)} Y={int(p.y)}', end='\r', flush=True)
    time.sleep(0.08)
