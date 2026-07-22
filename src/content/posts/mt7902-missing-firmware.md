---
title: MT7902 固件缺失导致 Suspend 失败
description: 被垃圾网卡背刺了。
pubDatetime: 2026-07-22T00:25:51+08:00
tags:
  - linux
---

## Table of contents

## 又黑了

（我为什么要说又:D

最近 `systemctl suspend` 之后，键盘能唤醒，但显示器黑屏、GPU 灯常亮，只能强制重启。

看了眼日志，全是 amdgpu 的报错。显卡是 RX 9070 GRE，我想可能是 Kernel 升级后 drm 又有 bug 了。

## 不是 AMD 的锅

再仔细看日志 suspend 的第一个错误不是 amdgpu：

```text
PM: suspend entry (deep)
mt7921e 0000:0a:00.0: Message 00020007 (seq 2) timeout
mt7921e 0000:0a:00.0: PM: pci_pm_suspend(): mt7921_pci_suspend [mt7921e] returns -110
mt7921e 0000:0a:00.0: PM: dpm_run_callback(): pci_pm_suspend returns -110
mt7921e 0000:0a:00.0: PM: failed to suspend async: error -110
PM: Some devices failed to suspend, or early wake event detected
```

`mt7921e` 是 MT7902 无线网卡的驱动。suspend 超时后系统中断挂起，AMDGPU 在回滚恢复的时候才崩的：

```text
amdgpu 0000:03:00.0: SMU is resuming...
amdgpu 0000:03:00.0: SMU: No response msg_reg: 6 resp_reg: 0
amdgpu 0000:03:00.0: Failed to enable requested dpm features!
amdgpu 0000:03:00.0: Failed to setup smc hw!
amdgpu 0000:03:00.0: resume of IP block <smu> failed -62
amdgpu 0000:03:00.0: amdgpu_device_ip_resume failed (-62).
amdgpu 0000:03:00.0: PM: failed to resume async: error -62
```

系统退到 s2idle 又试了一次，结果更惨，GPU 直接进了 MODE1 reset 然后恢复失败：

```text
PM: suspend exit
PM: suspend entry (s2idle)

amdgpu 0000:03:00.0: suspend of IP block <smu> failed -22
amdgpu 0000:03:00.0: SMU: No response msg_reg: e resp_reg: 0
amdgpu 0000:03:00.0: resume of IP block <smu> failed -62
amdgpu 0000:03:00.0: GPU pre asic reset failed with err, -22
amdgpu 0000:03:00.0: MODE1 reset
amdgpu 0000:03:00.0: GPU Recovery Failed: -62
```

既然怀疑 mt7921e，直接卸载驱动试试：

```bash
sudo modprobe -r mt7921e
systemctl suspend
```

恢复正常。看来就是它了。

因为 MT7902 驱动之前没进主线，有个 [mt7902_temp](https://github.com/OnlineLearningTutorials/mt7902_temp)，但是编译不过，就一直用的是有线网，所以从来没留意过无线。看了一下：

```text
❯ ip link
lo
eno1
dae0
```

没有 wlp。rfkill 也没任何输出。但 lspci 显示驱动确实绑定上了：

```text
0a:00.0 Network controller: MEDIATEK Corp. MT7902
    Kernel driver in use: mt7921e
```

驱动绑定了但没初始化出无线接口。翻启动日志：

```text
mt7921e 0000:0a:00.0: enabling device (0000 -> 0002)
mt7921e 0000:0a:00.0: Direct firmware load for mediatek/WIFI_RAM_CODE_MT7902_1.bin failed with error -2
mt7921e 0000:0a:00.0: ASIC revision: 79020000
mt7921e 0000:0a:00.0: Direct firmware load for mediatek/WIFI_MT7902_patch_mcu_1_1_hdr.bin failed with error -2
mt7921e 0000:0a:00.0: hardware init failed
```

蓝牙也是：

```text
bluetooth hci0: Direct firmware load for mediatek/BT_RAM_CODE_MT7902_1_1_hdr.bin failed with error -2
Bluetooth: hci0: Failed to load firmware file (-2)
```

`-2` ENOENT，固件文件压根不存在。

想起来之前`linux-firmware`拆包后，一直没装 `linux-firmware-mediatek`。升到 7.1 内核之后，驱动能认出设备了，但固件包没跟上：

```bash
sudo pacman -S linux-firmware-mediatek
```

重启后：

```text
mt7921e 0000:0a:00.0: enabling device (0000 -> 0002)
mt7921e 0000:0a:00.0: ASIC revision: 79020000
mt7921e 0000:0a:00.0: HW/SW Version: ...
mt7921e 0000:0a:00.0: WM Firmware Version: ...
wlp10s0: renamed from wlan0
```

固件加载成功。

再 suspend 一次：

```text
PM: suspend entry (deep)

amdgpu 0000:03:00.0: MODE1 reset

ACPI: PM: Low-level resume complete

amdgpu 0000:0e:00.0: SMU is resumed successfully!

amdgpu 0000:03:00.0: SMU is resumed successfully!

PM: suspend exit
```

干净了。

## 网卡使用体验

网卡使用体验极差。。。
