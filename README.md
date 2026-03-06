# openclaw-ops-runbooks

OpenClaw 线上运维与自愈方案仓库。

## 内容

- `docs/openclaw-self-healing-runbook.md`  
  OpenClaw 线上自愈方案（systemd timer + 自动重启 + Feishu 告警）

## 适用场景

- 机器人偶发不回复
- gateway 1006 异常关闭
- `heap out of memory` 导致服务重启
- 需要自动巡检与自愈

## 快速开始

1. 阅读运行手册：`docs/openclaw-self-healing-runbook.md`
2. 按文档执行一键安装脚本
3. 用验收命令检查 timer 与 healthcheck 状态

## 维护建议

- 每周检查一次 `journalctl --user -u openclaw-healthcheck.service`
- 每次升级 OpenClaw 后复验 timer 与 gateway
- 生产环境建议开启插件白名单和 Feishu sender 白名单

---

如果你在使用中遇到异常，可先按 runbook 的“故障速查卡”排查。