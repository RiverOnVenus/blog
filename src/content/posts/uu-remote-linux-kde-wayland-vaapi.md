---
title: 我的远程桌面方案
description: 在 Arch Linux + KDE Wayland 上用 UU 远程做被控端，记录 AUR 打包、VAAPI 硬编、无人值守重启和一次信令卡死的排查。
pubDatetime: 2026-10-18T18:30:00+08:00
modDatetime: 2026-10-24T14:22:00+08:00
tags:
  - linux
  - wayland
  - remote
---

## Table of contents

## 背景

我需要从手机和外面的电脑连回家里的 Arch 桌面。试过一些远程客户端，UU 体验最好，但是没有官方的 Linux 版，最近发现 [uu-remote-linux](https://github.com/VallierDev/uu-remote-linux)，体验还不错。

我的环境：

- Arch Linux，KDE Plasma Wayland
- Ryzen 5 9600X + RX 9070 GRE
- 桌面分辨率 2560×1440

我把它打包到了 AUR：[uu-remote-linux](https://aur.archlinux.org/packages/uu-remote-linux)。

## 安装

```bash
paru -S uu-remote-linux
```

包默认用 `--features wayland,portal` 构建，同时覆盖：

- X11
- Hyprland / wlroots（`wayland`）
- KDE Plasma Wayland、GNOME Wayland（`portal`）

KDE Wayland 直接用就行，不需要单独编译。其他环境如果只想保留部分后端，可以参考上游 README 改构建参数自己编。

包里还有：

- `uuremote-server`：被控端
- `uuremote-viewer`：实验性的 Linux 控制端
- systemd user unit `uuremote-native.service`
- `/dev/uinput` 的 udev 规则
- 桌面图标和 `.desktop` 文件

## 登录和 service

可以直接用桌面图标进入，也可以命令启动扫码登录：

```bash
uuremote-server login
```

用手机上的 UU 远程 App 扫码确认。凭证保存在 `~/.config/uuremote/config.json`，权限 0600。

然后启用 user service：

```bash
systemctl --user enable --now uuremote-native.service
```

这个 unit 挂在 `graphical-session.target` 上，这样它会等 graphical session 和 `DISPLAY` / `WAYLAND_DISPLAY` 就绪后再启动。之前用 `default.target` 时遇到过一次重启后 service 启动过早的问题：

```text
Desktop connection unavailable: x11_init failed with code -1
```

原因是 KDE 还没把显示环境导入 systemd user session，主机选了 X11 后端。改成 `graphical-session.target` 后就没再出现。

要看主窗口的话：

```bash
uuremote-server show
```

或者直接用桌面图标。关闭窗口只是隐藏，不会停止 service。

## 在 Wayland 下采集屏幕和注入输入

KDE Wayland 下，屏幕采集走 xdg-desktop-portal。第一次连接会弹出屏幕共享授权，同意之后会记住。

键鼠默认走 uinput（内核虚拟设备）。包的 udev 规则会给当前登录用户 `/dev/uinput` 的 `uaccess` 权限。如果节点已经存在，可以手动触发一次：

```bash
sudo udevadm trigger --name-match=uinput
```

需要强制指定输入后端时：

```bash
UU_INPUT_BACKEND=uinput   # 或 native
```

Wayland 下 uinput 的按键符号比 portal 原生输入更完整，尤其是需要输入下划线、组合键的时候。

## AMD VAAPI 硬编

默认逻辑是：检测到 NVIDIA 驱动就用 NVENC，否则用 CPU（libx264 / libx265）。AMD 的 VAAPI 是显式选项，不需要重新编译。

创建 drop-in：

```ini
# ~/.config/systemd/user/uuremote-native.service.d/vaapi.conf
[Service]
Environment=UU_VIDEO_ENCODER=vaapi
# 可选，默认就是 /dev/dri/renderD128
# Environment=UU_VAAPI_DEVICE=/dev/dri/renderD128
```

改完后重载并重启：

```bash
systemctl --user daemon-reload
systemctl --user restart uuremote-native.service
```

验证：

```bash
journalctl --user -u uuremote-native.service -f | grep 'Desktop encoder'
```

成功的话日志里会有：

```text
Desktop encoder: ... encoder=hevc_vaapi pix_fmt=nv12
```

`UU_VAAPI_DEVICE` 不是必须的，不写时程序默认用 `/dev/dri/renderD128`。但 `renderD128` 对应哪块 GPU 因机器而异，我这里是 RX 9070 GRE，其他机器可能是核显。单 GPU 通常不用写这一行，多 GPU 可以先看映射：

```bash
ls -l /dev/dri/by-path/
vainfo --display drm --device /dev/dri/renderD128
```

`vainfo` 在 `libva-utils` 包里。

AMD VAAPI 上游还没有完整验证，如果出现花屏、卡顿或码率异常，删掉这个 drop-in 就能回到 CPU。v0.2.9 之后还可以加：

```ini
Environment=UU_VAAPI_BUFFER_MS=250
```

用来加大 VAAPI 的编码缓冲，缓解高分辨率关键帧发糊，默认关闭。

## 无人值守重启

前提是 `uuremote-native.service` 是一个 systemd user service。重启后如果停在 Plasma Login Manager 登录界面，没有 user session，service 不会启动，远程桌面也就无从谈起。

所以要开 autologin。编辑：

```ini
# /etc/plasmalogin.conf.d/autologin.conf
[Autologin]
User=youruser
Session=plasma.desktop
Relogin=false
```

`Relogin=false` 保证注销后回到登录界面，不会马上又自动登录。

autologin 之后会话是解锁的，所以在启动后自动锁屏：

```sh
# ~/.local/bin/lock-on-start
#!/bin/sh
if [ "$(cut -d. -f1 /proc/uptime)" -lt 180 ]; then
    sleep 5
    sid="${XDG_SESSION_ID:-}"
    if [ -n "$sid" ]; then
        loginctl lock-session "$sid"
    else
        loginctl lock-session
    fi
fi
```

```ini
# ~/.config/autostart/lock-on-start.desktop
[Desktop Entry]
Name=Lock on Start
Type=Application
Terminal=false
StartupNotify=false
X-KDE-AutostartPhase=2
Exec=/home/youruser/.local/bin/lock-on-start
```

脚本只在开机三分钟内锁屏，手动登录不会被强制锁。

然后在手机客户端开启：

控制中心 → 安全 → 自动解锁被控端

输入 Linux 用户的登录密码。主机会通过 PAM 验证，解锁已有的 KDE 锁屏，然后恢复画面和输入。

### KWallet 的小问题

autologin 没有登录密码可以交给 PAM，KWallet 不会被自动解锁。开机后会出现一次 KWallet 密码库弹窗：

```text
ksecretd: Using kwallet without parent window!
```

点取消不影响远程桌面，只是依赖钱包的应用暂时拿不到密钥。可以接受每次开机点一下，也可以把钱包关闭。给钱包设空密码虽然省事，但任何以该用户身份运行的进程都能读取，不建议。

## 一次 15 小时的失联

10 月 23 日晚上 10 点后，控制端一直显示设备离线。机器没有关机，SSH、DNS、外网都正常，`uuremote-server` 进程也还在。

问题在信令连接上：

```bash
$ ss -tnp | grep uuremote
CLOSE-WAIT 82967 0 192.168.1.x:48048 <signaling>:443 users:(("uuremote-server",...))
```

只剩一条 `CLOSE-WAIT`，接收队列积压了 82967 字节。日志从 21:58 之后完全静默，没有断线重连，也没有 `Signaling heartbeat lost`。

时间线：

- 21:55 本机的透明代理 `honk-core` 重启，重建网络命名空间，已建立的连接被打断
- 21:57:52 主机处理 `released` 事件，`PeerConnection::close().await` 没有返回
- 21:57:57 ICE 变成 disconnected，21:58:22 变成 failed
- 之后 64 格的信令事件队列被填满，读协程阻塞在 `event_sender.send().await`，同一个 `select!` 里的心跳截止时间再也轮不到

上游从 v0.1.19 起就有心跳超时检测，但它只在读循环回到 `select!` 时才有效。读协程一旦卡在循环体里的 `await`，检测等于不存在。这是失联持续 15 小时的原因。

## 修复

给上游提了 PR [#104](https://github.com/VallierDev/uu-remote-linux/pull/104)：

- 独立的看门狗任务，按最后收到数据的时间判断，不再依赖读循环是否被调度
- 事件投递、pong、控制包和 WebSocket 写入都加超时或 `try_send`
- `PeerConnection::close()` 加 5 秒超时，避免一个坏掉的 peer 卡住主循环
- 回归测试：事件消费者不读队列时，仍然能关掉死连接

## 兜底：健康检查 timer

看门狗处理信令层。进程整体卡死或退出，仍然需要另一层兜底。这里用 systemd user timer，每 5 分钟检查一次，异常就重启服务。

不需要 root。`uuremote-native.service` 是 user service，`systemctl --user`、`journalctl --user` 和 `ss -tnp` 看自己的进程都不需要提权。只有想让 timer 在没登录时也运行，才需要 `loginctl enable-linger`。

`~/.local/bin/uu-remote-health`：

```bash
#!/usr/bin/env bash
set -u
unit=uuremote-native.service

restart() {
    logger -t uu-remote-health "restarting $unit: $1"
    systemctl --user restart "$unit"
}

has_estab() {
    ss -tnp 2>/dev/null | awk '/uuremote-server/ && $1=="ESTAB" {f=1} END {exit !f}'
}

systemctl --user is-active --quiet "$unit" || { restart "inactive"; exit 0; }

# 已知的卡死形态：半关闭且接收队列有积压
if ss -tnp 2>/dev/null | awk '/uuremote-server/ && $1=="CLOSE-WAIT" && $2>0 {f=1} END {exit !f}'; then
    restart "CLOSE-WAIT with unread data"
    exit 0
fi

# 正常重连会短暂没有 ESTAB，等 10 秒再确认
if ! has_estab; then
    sleep 10
    has_estab || restart "no established signaling connection"
fi
```

```ini
# ~/.config/systemd/user/uu-remote-health.service
[Unit]
Description=UU Remote liveness check

[Service]
Type=oneshot
ExecStart=%h/.local/bin/uu-remote-health
```

```ini
# ~/.config/systemd/user/uu-remote-health.timer
[Unit]
Description=Check UU Remote every 5 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min
AccuracySec=30s

[Install]
WantedBy=timers.target
```

启用：

```bash
chmod +x ~/.local/bin/uu-remote-health
systemctl --user daemon-reload
systemctl --user enable --now uu-remote-health.timer
```

间隔选 5 分钟，是因为心跳每 3 分钟写一条日志，重连凭证每 5 分钟刷新一次；没有 ESTAB 时脚本会等 10 秒再确认，避开正常重连的几秒空窗。

## iOS 画质档位

> **v0.2.10 已修复。** 直接升级即可，下面的本地补丁不再需要。修复原因和验证结果见本节末尾。

主机支持全部画质档位：1M、2M、8M、20M、自动和自定义。桌面客户端的超清/原画切换正常。

但在 iPhone（iOS 26.6.2，UU 远程 4.42.0）上，连接这台 Linux 主机时，「超清」和「原画」按钮可见，点击没有任何反应，主机也收不到 quality=3/4 的请求。同一个账号连接官方 Windows 被控端时，这些按钮可以正常切换。

上游 issue 在这里：[#49 iPhone 端超清/原画按钮可见但点击无反应](https://github.com/VallierDev/uu-remote-linux/issues/49)。

v0.2.10 之前的绕过方法是主机侧强制档位，需要自己打个本地补丁，AUR 包里没有。补丁加在 `src/capture_setting.rs` 的 `apply_rpc()` 里，位置在 `next.fps = next.fps.clamp(MIN_FPS, MAX_FPS);` 之前：

```diff
--- a/src/capture_setting.rs
+++ b/src/capture_setting.rs
@@ -169,6 +169,19 @@
     } else {
         return None;
     }
+    // Local override for clients that hide the high-bitrate presets.
+    if let Ok(value) = std::env::var("UU_FORCE_QUALITY") {
+        if let Ok(quality) = value.parse::<u64>() {
+            if (1..=6).contains(&quality) { next.quality = quality; }
+        }
+    }
+    if next.quality == QUALITY_CUSTOM {
+        if let Ok(value) = std::env::var("UU_FORCE_BITRATE") {
+            if let Ok(mbps) = value.parse::<u32>() {
+                if mbps > 0 { next.custom_mbps = mbps; }
+            }
+        }
+    }
     next.fps = next.fps.clamp(MIN_FPS, MAX_FPS);
```

用 `UU_FORCE_QUALITY` 指定档位，3 是超清 8M，4 是原画 20M。自定义码率用 6 配合 `UU_FORCE_BITRATE`：

```ini
[Service]
Environment=UU_FORCE_QUALITY=4
# Environment=UU_FORCE_QUALITY=6
# Environment=UU_FORCE_BITRATE=30
```

重新构建后，用 systemd drop-in 把 `ExecStart` 指向本地二进制。客户端里保存的档位会继续生效，所以日常使用暂时不受影响。

### 修复

上游在 [#49](https://github.com/VallierDev/uu-remote-linux/issues/49) 里定位到了原因。主机发给控制端的设备能力（`forward_setting` 里的 `device_capability`）是扁平结构，官方 Windows 被控端用的是 `data.device_capability` 嵌套格式，`type` 也放在 `data` 里。iPhone 解析不了这条消息，就把画质和真彩锁在默认值。Mac 客户端不依赖它，所以一直正常。

v0.2.10 按官方格式发送设备能力，包含编码器真实支持的 4:4:4，并补发了 `sender_para_info`。升级后实测 iPhone 上超清、原画都能切换，主机日志能看到 quality=3/4 和对应的码率：

```text
quality=3 → max_kbps=8000
quality=4 → max_kbps=20000
```
