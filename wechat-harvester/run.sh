#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/output"

# Try to activate WeChat and prefill search keyword
osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
tell application "WeChat" to activate
delay 0.5
tell application "System Events"
  keystroke "f" using command down
  delay 0.2
  keystroke "youtube"
  key code 36
end tell
APPLESCRIPT

echo "微信已尝试激活并搜索 youtube。"
echo "请确保你已进入目标群（如【深海圈】风向标小组）并看到搜索结果。"

python3 "$DIR/harvest.py" "$@"
