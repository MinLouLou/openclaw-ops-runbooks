# WeChat Fixed-Path RPA（Mac）

这是“固定点击路径”方案：按配置坐标自动点微信并采集搜索结果。

## 先决条件

1. 给终端/运行器授权：
   - 系统设置 → 隐私与安全性 → **辅助功能**
   - 系统设置 → 隐私与安全性 → **输入监控**（建议）
2. 微信窗口保持前台可见，分辨率固定（避免坐标漂移）。

## 文件

- `config.example.json`：坐标模板
- `mouse_pos.py`：读取当前鼠标坐标（用于标定）
- `rpa_capture.py`：执行自动点击与采集

## 标定步骤（一次即可）

1. 复制模板：

```bash
cp config.example.json config.json
```

2. 运行坐标读取器：

```bash
/usr/bin/python3 mouse_pos.py
```

3. 把鼠标放到对应控件上，记下坐标，填入 `config.json`（按固定路径）：
   - `chat_search_box`：微信主界面搜索框（用于搜群名）
   - `group_chat_item`：聊天列表里目标群的位置（优先点击这个，跳过“搜群名”）
   - `chat_result_first_item`：群搜索结果第一条（作为兜底）
   - `top_right_more_btn`：群聊天窗口右上角三个点
   - `find_chat_content_btn`：菜单里的“查找聊天内容”
   - `inchat_search_box`：查找聊天内容的输入框（输入 youtube）
   - `result_first_item`：搜索结果第一条
   - `result_next_item`：下一条（用于计算行距）

## 运行

```bash
/usr/bin/python3 rpa_capture.py --config config.json --group "【深海圈】风向标小组" --keyword youtube --max-items 120

仅验证前两步（打开微信+进入群）：

```bash
/usr/bin/python3 rpa_capture.py --config config.json --group "【深海圈】风向标小组" --until-step 2

若微信不在默认路径，可加：

```bash
/usr/bin/python3 rpa_capture.py --config config.json --group "【深海圈】风向标小组" --until-step 2 --app-path "/Applications/WeChat.app"
```
```
```

输出：
- `../output/rpa-raw-YYYY-MM-DD.txt`

## 说明

- 采集方式：逐条点击结果 + `⌘C` 读剪贴板。
- 若某条复制失败，会跳过继续。
- 你说的“固定路径”就是靠坐标配置实现的。