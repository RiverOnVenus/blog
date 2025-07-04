---
title: Arch Linux 的双显卡配置
categories: [linux,nvidia]
comments: true
---

<a data-fancybox="gallery" href="../assets/img/post/optimus/image01.jpg"><img src="../assets/img/post/optimus/image01.jpg">

> Photo by [Anna Jiménez Calaf](https://unsplash.com/@annajimenez?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)  

* TOC
{:toc}
*最后更新时间：Sun Jun 23 12:45:39 PM CST 2024*

## PRIME render offload

正在用的方案。

如果没有特殊需求，使用 NVIDIA 官方的方案 PRIME render offload 是明智的选择，详情见[官方文档](http://download.nvidia.com/XFree86/Linux-x86_64/525.53/README/primerenderoffload.html) 和 [ArchWiki](https://wiki.archlinux.org/title/PRIME#PRIME_render_offload)。

使用后两种方案大多是为了极致的续航。

> 使用 NVIDIA PRIME 时，N 卡处于待机状态，即使不在上面运行任何应用程序，它也会继续消耗电能。由于 N 卡会自动降频，因此耗电量相对较低，但仍比仅用核显时高很多。

## optimus-manager

之前用的方案，配置也许已经过时。

开始之前，请确定已经按照 [ArchWiki](https://wiki.archlinux.org/title/NVIDIA) 安装好了相应驱动。

> 项目地址： [Askannz/optimus-manager]( https://github.com/Askannz/optimus-manager)

optimus-manager 有三个模式：

- Integrated--仅用核显
- Nvidia--仅用独显
- Hybrid--Nvidia offload

Hybrid 配合 Nvidia-prime 使用

```bash
pacman -S nvidia-prime
```

> Hybrid 模式文档 [Nvidia GPU offloading for "hybrid" mode](https://github.com/Askannz/optimus-manager/wiki/Nvidia-GPU-offloading-for-%22hybrid%22-mode)

**安装**

[项目安装文档](https://github.com/Askannz/optimus-manager#installation)

使用 optimus-manager 需要配置正确的电源管理才能切换模式，在我的笔记本电脑上用的 [bbswitch](https://github.com/Bumblebee-Project/bbswitch)。

```bash
pacman -S optimus-manager bbswitch
```

> 注意：bbswitch 很久没更新了，在较新的笔记本电脑上可能没用，甚至产生一些其它问题。且 bbswitch 只是 optimus-manager 项目的电源管理方案 [A guide  to power management options](https://github.com/Askannz/optimus-manager/wiki/A-guide--to-power-management-options)之一，所以请根据电脑环境选择合理的方案。

**配置**

[项目配置文档](https://github.com/Askannz/optimus-manager/#configuration)

主配置文件位于`/etc/optimus-manager/optimus-manager.conf`

这是我的配置：

```
[intel]
DRI=3
accel=
driver=modesetting
modeset=yes
tearfree=

[nvidia]
DPI=96
PAT=yes
allow_external_gpus=yes
dynamic_power_management=no
ignore_abi=yes
modeset=yes
options=triple_buffer

[optimus]
auto_logout=yes
pci_power_control=no
pci_remove=no
pci_reset=no
startup_auto_battery_mode=integrated
startup_auto_extpower_mode=hybrid
startup_mode=auto
switching=bbswitch
```

启动系统时，根据是否接通电源自动选择模式。使用电池为 Integrated 模式，N 卡被禁，提高了续航。接通电源为 Hybrid 模式，使用`prime-run`命令指定应用程序使用 N 卡。

也可以手动切换：

- `optimus-manager --switch nvidia` 切换到 Nvidia
- `optimus-manager --switch integrated` 切换到核显并关闭 Nvidia 的电源
- `optimus-manager --switch hybrid` 切换到 Nvidia offload

> 注意：切换模式会自动注销（用户态切换），所以请确保你已经保存你的工作，并关闭所有的应用程序。

安装配置完成后需要重启系统，重启系统前请认真阅读项目 [README](https://github.com/Askannz/optimus-manager/blob/master/README.md) 和 [Wiki](https://github.com/Askannz/optimus-manager/wiki)，确保配置没有问题再重启系统。做好修复系统的准备。

重启后，使用`systemctl status optimus-manager.service`命令查看服务状态，使用`optimus-manager --status`命令查看当前模式。

**可选安装**

[optimus-manager-qt](https://github.com/Shatur/optimus-manager-qt)，使用 AUR 助手安装。

## envycontrol

> 项目地址：[bayasdev/envycontrol](https://github.com/bayasdev/envycontrol)

安装

```
paru -S envycontrol
```

使用

```
sudo envycontrol -s <MODE>
```

可选安装

[optimus-gpu-switcher](https://github.com/enielrodriguez/optimus-gpu-switcher)

## 参考资料

1. [https://github.com/Askannz/optimus-manager](https://github.com/Askannz/optimus-manager)
1. [https://github.com/bayasdev/envycontrol](https://github.com/bayasdev/envycontrol)
