---
title: 使用 Modprobed-db 减少内核编译时间
description: 用 Modprobed-db 精简内核配置，能省不少编译时间。
pubDatetime: 2022-05-07T00:00:00+08:00
tags:
  - linux
  - tool
  - kernel
---

<img src="/images/posts/modprobed-db/image01.jpg" loading="lazy" decoding="async" />

> Photo by <a href="https://unsplash.com/@aronvisuals?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Aron Visuals</a> on <a href="https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>

自从开始尝试自定义内核，便陷入其中。在内核方面，我是业余的，仅仅是在内核中打上一些我想使用的补丁以及简单修改一些配置。每当主线内核发布或有新的补丁时，我就会重新编译内核。就我的笔记本电脑来说，每次编译内核都会花费一个多小时的时间，而当我使用了 Modprobed-db 后，编译时间显著减少了。

## Table of contents

## Modprobed-db 是什么？

Modprobed-db 用于记录系统已加载的内核模块。随后，[make localmodconfig](https://www.kernel.org/doc/html/latest/admin-guide/README.html?highlight=localmodconfig#configuring-the-kernel) 会根据当前的 config 和这份模块列表生成新的 config，并禁用不需要的模块。这样就得到了一个属于你的、精简的内核。

## 如何使用它呢？

### 安装和初始化配置

> 项目地址：**[graysky2/modprobed-db](https://github.com/graysky2/modprobed-db)**

对于 Arch Linux，安装 [modprobed-db](https://aur.archlinux.org/packages/modprobed-db)。

安装完后首先运行`modprobed-db`，它会创建 Modprobed-db 配置文件 `$XDG_CONFIG_HOME/modprobed-db.conf`。

在 `~/.config/modprobed-db.conf` 中，可以添加你想忽略的模块。一些由其它软件包提供的模块需要添加进去，如 Nvidia。

默认配置中包括了一些常见的、需要被忽略的模块：

```shell
IGNORE=(nvidia nvidia_drm nvidia_modeset nvidia_uvm vboxdrv vboxnetadp vboxnetflt vboxpci lirc_dev lirc_i2c osscore oss_hdaudio oss_usb tp_smapi thinkpad_ec zavl znvpair zunicode zcommon zpios zfs spl splat)
```

### 填充数据库

配置好 `modprobed-db.conf` 后，运行`modprobed-db store`，它会探测到当前加载的模块，并创建 Modprobed-db 数据库文件 `$XDG_CONFIG_HOME/modprobed.db`，数据库文件是一个文本文件，其内容就是被探测到的模块列表。这个数据库文件可以积累，每次运行`modprobed-db store`都会记录之前未出现过的模块。使用`modprobed-db list`可以显示当前数据库文件中的模块。

刚开始收集时，最好先使用发行版提供的完整内核或自己的保底内核一段时间。已经精简过的内核可能根本不包含某些模块，系统就无法加载它们，`store` 也无从记录。

#### 自动更新数据库

启用：

```shell
systemctl --user enable --now modprobed-db
```

当前 Arch 包的定时器每隔 6 小时运行一次`modprobed-db store`。不同发行版或版本的 unit 配置可能不同，最好在本机确认实际的触发时间。

[Service] 和 [Timer] 可以用下面命令查看：

```shell
systemctl --user status modprobed-db
systemctl --user list-timers
```

#### 手动编辑数据库

使用自动定期数据库更新或手动运行`modprobed-db store`并不是万无一失的。

- 有些模块在两次定期数据库更新之间被加载然后卸载，可能不会被捕获。
- 有些模块在启动时使用，不被 modprobed-db 捕获（如 efivarfs），它们需要被手动添加到 modprobed.db 文件中。

前面提到过，modprobed.db 数据库文件是一个简单的文本文件，每行包含一个内核模块名称：它可以被手动编辑以添加/删除一个模块，可以将自己要用的模块加入其中。在手动编辑后运行一次`modprobed-db store`，这些模块会自动重新排序。

下面是一些常用的模块，如果你的数据库中没有，可以对照着手动添加。

```shell
ntfs3
ext4
fat
vfat
loop
isofs
cifs
efivarfs
usb_storage
usbhid
bridge
```

在完善数据库后，就可以使用 Modprobed-db 来构建内核了。

### 使用 Modprobed-db 构建内核

对于[传统编译内核](https://wiki.archlinux.org/title/Kernel/Traditional_compilation)的方式，在配置好 `.config` 后运行`make LSMOD=$HOME/.config/modprobed.db localmodconfig`就行。

如果使用 Arch 官方内核的 [PKGBUILD](https://github.com/archlinux/svntogit-packages/blob/packages/linux/trunk/PKGBUILD) 构建内核，对 PKGBUILD 做以下更改：

```shell
...
  echo "Setting config..."
  cp ../config .config
  make olddefconfig

  make LSMOD=$HOME/.config/modprobed.db localmodconfig

  diff -u ../config .config || :

  make -s kernelrelease > version
  echo "Prepared $pkgbase version $(<version)"
 ...
```

## 那么，它减少了多少编译时间？

我的笔记本电脑 CPU 是 Intel Core i5-8250U (8) @ 1.6GHz，4 核 8 线程。

编译的内核是主线的 5.17.5，config 是 Arch Linux 默认内核的 config。

使用 gcc 编译需要 55m35s，使用 clang 编译同时启用 FULL LTO 需要 1h21m57s；在使用 Modprobed-db 后，使用 gcc 编译需要 11m50s，使用 clang 编译同时启用 FULL LTO 需要 24m11s。

<img src="/images/posts/modprobed-db/image02.jpeg" loading="lazy" decoding="async" />

为什么时间减少了这么多呢？因为一个正常的内核大概有 5000 多个模块，而 modprobed-db 数据库中就 200 个模块。

<img src="/images/posts/modprobed-db/image03.png" loading="lazy" decoding="async" />

内核构建大部分时间花费在了模块上，而其中许多模块也用不到。

## 一些经验和建议

如果使用 dkms 需要将对应模块放入到忽略模块列表中，如 bbswitch，acpi_call 等。

将需要加载内核模块的程序都运行一下，以及插入 USB 等设备，然后运行`modprobed-db store`完善数据库。

在完整内核上使用一段时间 Modprobed-db 后，再用它编译内核。把日常会用到的程序都运行一遍，也别漏掉休眠唤醒、蓝牙、VPN、手柄、移动硬盘等不常用设备和功能。

日常只需要运行`modprobed-db store`。不要把`modprobed-db rebuild`当成清理数据库的命令：它会尝试加载数据库中的模块，然后再重建数据库，需要 root 权限，也可能在当前会话加载大量模块。

若要重新得到最小的个人模块列表，先备份并移走旧的`modprobed.db`，重启系统，然后运行一次`modprobed-db store`。重启前运行`store`没有意义，因为`rebuild`加载的模块仍会留在当前内核中。

使用 Modprobed-db 构建最小内核是有风险的，记得选择一个稳定的内核备用。

## 参考资料

1. [https://wiki.archlinux.org/title/Modprobed-db](https://wiki.archlinux.org/title/Modprobed-db)
1. man 8 modprobed-db
