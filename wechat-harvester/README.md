# wechat-harvester

用于在 **Mac 微信客户端** 无导出能力时，半自动采集“群内 YouTube 分享”并生成汇总。

## 使用

```bash
cd /Users/min/.openclaw/workspace/wechat-harvester
./run.sh
```

## 过程

1. 脚本会尝试激活微信并搜索 `youtube`。
2. 你在目标群（如【深海圈】风向标小组）里，把搜索结果按屏复制。
3. 每复制一次，回到终端按回车采集一次；输入 `q` 结束。
4. 自动生成：
   - `output/raw-YYYY-MM-DD.txt`（原始采集）
   - `output/summary-YYYY-MM-DD.md`（去重汇总）

## 说明

- 依赖：macOS 自带 `pbpaste` + `osascript`。
- 无需微信导出权限。
- 这是一种“复制即采集”的折中方案，稳定性高于纯 UI 点按。
