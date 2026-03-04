# Scrapling 能力接入说明（团队版）

日期：2026-03-04

## 已完成

我这边已经在本地工作区完成了 Scrapling 能力的基础接入：

- 新建虚拟环境：`/Users/min/.openclaw/workspace/.venv`
- 已安装：
  - `scrapling`（核心解析能力）
  - `scrapling[fetchers]`（HTTP/动态抓取依赖）
- 新增一键脚本：`scripts/setup_scrapling.sh`

## 一键安装（给团队）

### 1) 最小能力（推荐先用）
```bash
bash scripts/setup_scrapling.sh
```
- 用于：HTML 解析、选择器抽取、文本提取
- 优点：轻量、快、稳定

### 2) 全量能力（含 AI/MCP/Shell/浏览器）
```bash
bash scripts/setup_scrapling.sh --full
```
- 用于：反爬场景、浏览器动态页面、MCP/CLI 等完整能力
- 注意：安装包体积大，耗时明显更长

## 快速验证

### A. 解析器验证（不依赖网络）
```bash
source .venv/bin/activate
python - <<'PY'
from scrapling.parser import Selector
html = '<html><body><h1>Hello</h1><p class="x">world</p></body></html>'
s = Selector(html)
print(s.css('h1::text').get())
print(s.css('.x::text').get())
PY
```

### B. Fetcher 验证（联网抓取）
```bash
source .venv/bin/activate
python - <<'PY'
from scrapling.fetchers import Fetcher
p = Fetcher.get('https://example.com')
print(p.css('title::text').get())
PY
```

## 当前环境问题（已识别）

在本机执行 Fetcher 联网验证时出现证书链错误：

- `curl: (60) SSL certificate problem: unable to get local issuer certificate`

这不是 Scrapling 本身问题，是本机 Python/curl CA 证书链问题。常见修复路径：

1. 更新系统证书与 Python 证书链
2. 使用 certifi CA 包并显式指定
3. 在受控内网场景配置企业 CA

> 不建议在生产里用 `verify=False` 规避。

## 团队落地建议（直接执行）

1. 先全员统一走最小能力（解析器）
2. 只有需要动态/反爬的同学再开 `--full`
3. 把证书链检查加到环境自检脚本里（CI 启动前校验）
4. 抓取策略合规：遵守 ToS、robots 与隐私合规要求
