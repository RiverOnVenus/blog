---
title: NVIDIA 导致系统挂起失败
categories: [linux,nvidia]
comments: true
---

* TOC
{:toc}
## 现象

`systemctl suspend` 后系统立即被唤醒。

## 日志

```
Jun 23 14:09:26 venus systemd[1]: Starting System Suspend...
Jun 23 14:09:26 venus systemd-sleep[2537]: User sessions remain unfrozen on explicit request ($SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=0).
Jun 23 14:09:26 venus systemd-sleep[2537]: This is not recommended, and might result in unexpected behavior, particularly
Jun 23 14:09:26 venus systemd-sleep[2537]: in suspend-then-hibernate operations or setups with encrypted home directories.
Jun 23 14:09:26 venus systemd-sleep[2537]: Performing sleep operation 'suspend'...
Jun 23 14:09:28 venus systemd-sleep[2537]: Failed to put system to sleep. System resumed again: Input/output error
Jun 23 14:09:28 venus systemd[1]: systemd-suspend.service: Main process exited, code=exited, status=1/FAILURE
Jun 23 14:09:28 venus systemd[1]: systemd-suspend.service: Failed with result 'exit-code'.
Jun 23 14:09:28 venus systemd[1]: Failed to start System Suspend.
```

```
[   95.430308] nvidia 0000:01:00.0: PM: pci_pm_suspend(): nv_pmops_suspend+0x0/0x30 [nvidia] returns -5
[   95.430918] nvidia 0000:01:00.0: PM: dpm_run_callback(): pci_pm_suspend+0x0/0x1b0 returns -5
[   95.430924] nvidia 0000:01:00.0: PM: failed to suspend async: error -5
[   97.195357] nvidia 0000:01:00.0: PM: pci_pm_suspend(): nv_pmops_suspend+0x0/0x30 [nvidia] returns -5
[   97.195930] nvidia 0000:01:00.0: PM: dpm_run_callback(): pci_pm_suspend+0x0/0x1b0 returns -5
[   97.195934] nvidia 0000:01:00.0: PM: failed to suspend async: error -5
```

## 解决

### “错误的”方法

在看到是 nvidia 导致的问题时，我立即想的是先禁用掉它，于是安装了 [envycontrol](https://github.com/bayasdev/envycontrol) 切到 integrated 模式，有效。

但这不是正确的解决方法，所以卸载 envycontrol 并删除它的残留配置文件。

### 正确的方法:pushpin:

通过日志找到了 [Wakeup_triggers#NVIDIA_drivers](https://wiki.archlinux.org/title/Power_management/Wakeup_triggers#NVIDIA_drivers), 一模一样的日志，抄一抄 wiki 的解决方法。

先添加内核模块参数：`NVreg_PreserveVideoMemoryAllocations=1`

再启用相关服务：

```
sudo systemctl enable nvidia-suspend.service
sudo systemctl enable nvidia-hibernate.service
sudo systemctl enable nvidia-resume.service
```

重启后挂起成功。

## 参考

1. [https://wiki.archlinux.org/title/Power_management/Wakeup_triggers#NVIDIA_drivers](https://wiki.archlinux.org/title/Power_management/Wakeup_triggers#NVIDIA_drivers)
2. [https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#Preserve_video_memory_after_suspend](https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#Preserve_video_memory_after_suspend)
