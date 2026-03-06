# OpenClaw 线上自愈方案（systemd timer + 自动重启 + Feishu 告警）

> 适用场景：OpenClaw 在 Linux 服务器上偶发不回复、gateway 异常关闭（1006）、OOM（heap out of memory）导致反复重启。

## 1. 目标

- 自动巡检（每 5 分钟）
- 自动自愈（服务挂掉/OOM 自动重启）
- 自动告警（重启后推送到 Feishu）
- 降低误重启（不做激进 probe，避免 warm-up 抖动误判）

---

## 2. 一键安装（推荐）

> 将下面命令整段复制到服务器执行。

```bash
bash -lc '
set -euo pipefail

TARGET_FEISHU_USER="user:ou_e481122a42020a60c2642eb868e07984"
HEAP_MB="3072"

mkdir -p /root/bin ~/.config/systemd/user/openclaw-gateway.service.d

cat > /root/bin/openclaw-healthcheck.sh <<EOF
#!/usr/bin/env bash
set -euo pipefail

TS="\$(date "+%F %T")"
STATE="\$(systemctl --user is-active openclaw-gateway 2>/dev/null || true)"
LOG="\$(journalctl --user -u openclaw-gateway -n 120 --no-pager 2>/dev/null || true)"

notify() {
  local msg="\$1"
  openclaw message send --channel feishu --target "${TARGET_FEISHU_USER}" --message "\$msg" >/dev/null 2>&1 || true
}

if [[ "\$STATE" != "active" ]]; then
  systemctl --user restart openclaw-gateway || true
  echo "\$TS [heal] reason=inactive action=restarted"
  notify "⚠️ OpenClaw 自愈触发：reason=inactive，已自动重启 gateway（\$TS）"
  exit 0
fi

if echo "\$LOG" | grep -Eqi "heap out of memory|FATAL ERROR|status=6/ABRT|core-dump"; then
  systemctl --user restart openclaw-gateway || true
  echo "\$TS [heal] reason=oom_or_core_dump action=restarted"
  notify "⚠️ OpenClaw 自愈触发：reason=oom_or_core_dump，已自动重启 gateway（\$TS）"
  exit 0
fi

echo "\$TS [ok] healthy"
EOF
chmod +x /root/bin/openclaw-healthcheck.sh

cat > ~/.config/systemd/user/openclaw-gateway.service.d/override.conf <<EOF
[Service]
Environment=NODE_OPTIONS=--max-old-space-size=${HEAP_MB}
EOF

cat > ~/.config/systemd/user/openclaw-healthcheck.service <<EOF
[Unit]
Description=OpenClaw Healthcheck and Auto-Heal

[Service]
Type=oneshot
ExecStart=/root/bin/openclaw-healthcheck.sh
EOF

cat > ~/.config/systemd/user/openclaw-healthcheck.timer <<EOF
[Unit]
Description=Run OpenClaw Healthcheck every 5 minutes

[Timer]
OnCalendar=*:0/5
Persistent=true
AccuracySec=30s
Unit=openclaw-healthcheck.service

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user restart openclaw-gateway
systemctl --user disable --now openclaw-healthcheck.timer >/dev/null 2>&1 || true
systemctl --user enable --now openclaw-healthcheck.timer
systemctl --user start openclaw-healthcheck.service

echo "=== timer ==="
systemctl --user status openclaw-healthcheck.timer --no-pager -l | sed -n "1,25p"
echo "=== service logs ==="
journalctl --user -u openclaw-healthcheck.service -n 20 --no-pager
'
```

---

## 3. 验收标准

执行：

```bash
systemctl --user status openclaw-healthcheck.timer --no-pager -l
systemctl --user list-timers --all | grep openclaw-healthcheck
journalctl --user -u openclaw-healthcheck.service -n 20 --no-pager
```

通过标准：

- timer 为 `active (waiting)`
- `Trigger` 有具体时间（不是 `n/a`）
- healthcheck 日志出现 `[ok] healthy` 或明确的 `[heal] ...`（不连续误触发）

---

## 4. 常见故障与处理

### 4.1 `Trigger: n/a` / `active (elapsed)`

说明 timer 规则未生效。用 `OnCalendar` 版重写 timer（见上文一键脚本，已修复此坑）。

### 4.2 持续 `gateway_probe_failed` 重启循环

原因通常是 probe 策略过激。当前脚本已改为**保守策略**：只在 `inactive` 或 `OOM/core-dump` 时重启。

### 4.3 `gateway closed (1006)`

优先检查：

```bash
systemctl --user status openclaw-gateway --no-pager -l
journalctl --user -u openclaw-gateway -n 120 --no-pager
```

如果包含 `heap out of memory`，确认 `NODE_OPTIONS=--max-old-space-size=3072` 已生效。

---

## 5. 安全建议（强烈建议）

当前线上常见风险：

1. `plugins.allow` 为空，会自动加载非内置插件
2. `channels.feishu.groupPolicy="open"`，群内注入风险较高

建议：

- 为 `plugins.allow` 设置白名单
- 将群策略改为 `allowlist`
- 对 runtime / fs / web 工具做最小权限

---

## 6. 运维速查命令

```bash
# 网关状态
openclaw gateway status

# 总状态
openclaw status

# 网关日志
journalctl --user -u openclaw-gateway -n 120 --no-pager

# 自愈任务日志
journalctl --user -u openclaw-healthcheck.service -n 50 --no-pager

# 定时器状态
systemctl --user status openclaw-healthcheck.timer --no-pager -l
```

---

## 7. 版本记录

- 文档版本：v1.0
- 适配 OpenClaw：2026.3.2+
- 场景复盘：OOM + pairing 未放行导致“看似在线但不回复”
