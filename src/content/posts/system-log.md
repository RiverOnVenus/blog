---
title: 系统：你对我做了什么？！
description: 最后更新时间：Wed Oct 8 05:21:22 PM CST 2025 前言 过去在笔记本上用 Arch 四年，陆陆续续装了一些优化用的软件，改了不少配置文件，但时间一长我已经忘了都动过哪些地方，有些东西可能早就不适用了。
  所以这次在新装的台式机上，我打算把所有和系统优化、维护有关的操作记录下来，包括安装的软件、做
pubDatetime: 2025-03-16T00:00:00+08:00
tags:
- linux
- kde
---

*最后更新时间：Wed Oct  8 05:21:22 PM CST 2025*


## Table of contents

## 前言

过去在笔记本上用 Arch 四年，陆陆续续装了一些优化用的软件，改了不少配置文件，但时间一长我已经忘了都动过哪些地方，有些东西可能早就不适用了。

所以这次在新装的台式机上，我打算把所有和系统优化、维护有关的操作记录下来，包括安装的软件、做的配置，方便以后查阅，也避免重复踩坑。这份记录会持续更新。

## 文件系统

首先是文件系统和分区。这次我在 SSD 上用了 Btrfs 作为根文件系统，HDD 上用了 XFS 做数据盘。之前一直用的是 EXT4，其实馋 Btrfs 很久了。虽然还没完全搞明白 Btrfs，但透明压缩、子卷和对 SSD 友好的特性已经让我很满意了。XFS 放在 HDD 上用来存数据，性能也不错，比较省心。

```shell
NAME        FSTYPE FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
sda                                                                                
└─sda1      xfs                6dda4ef6-5539-425b-9e17-0a374910721b    2.2T    39% /mnt/data
zram0       swap   1     zram0 81a25874-1132-4b4a-aba9-ee63778ea6f0                [SWAP]
nvme0n1                                                                            
├─nvme0n1p1 vfat   FAT32       A4FB-3831                               1.7G    17% /boot
└─nvme0n1p2 btrfs              a0b762a5-a99d-4d46-81d8-b10aa8620fa4  431.2G    53% /game
                                                                                   /home
                                                                                   /
```

### 挂载参数

透明压缩等级很难找一个完美的平衡点，对 @ @home 子卷用默认的。kernel 6.15 上 zstd 支持负的压缩等级，对 @game 子卷用了 compress-force=zstd:-9

```text
# /dev/nvme0n1p2
UUID=a0b762a5-a99d-4d46-81d8-b10aa8620fa4       /               btrfs           rw,relatime,ssd,discard=async,compress=zstd:3,space_cache=v2,subvol=/@  0 0

UUID=a0b762a5-a99d-4d46-81d8-b10aa8620fa4       /home           btrfs           rw,relatime,ssd,discard=async,compress=zstd:3,space_cache=v2,subvol=/@home      0 0

UUID=a0b762a5-a99d-4d46-81d8-b10aa8620fa4       /game           btrfs           rw,relatime,ssd,discard=async,compress-force=zstd:-9,space_cache=v2,subvol=/@game       0 0

# /dev/nvme0n1p1
UUID=A4FB-3831          /boot           vfat            rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro   0 2

# /dev/sda1
UUID=6dda4ef6-5539-425b-9e17-0a374910721b       /mnt/data       xfs             rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota        0 2
```

<figure>
  <img src="https://image.zhui.dev/file/nvmessd.png" alt="Btrfs (compress-force=zstd:3) 在 NVMe SSD 的读写速度测试" loading="lazy" decoding="async" />
  <figcaption>Btrfs (compress-force=zstd:3) 在 NVMe SSD 的读写速度测试</figcaption>
</figure>

<figure>
  <img src="https://image.zhui.dev/file/hdd.png" alt="XFS 在 HDD 的读写速度测试" loading="lazy" decoding="async" />
  <figcaption>XFS 在 HDD 的读写速度测试</figcaption>
</figure>

<p>### Btrfs 相关</p>

btrfs-progs

```shell
sudo pacman -S btrfs-progs
```

btrfs scrub

```shell
sudo systemctl enable btrfs-scrub@-.timer
sudo systemctl start btrfs-scrub@-.timer
```

btrfs-assistant

```shell
sudo pacman -S btrfs-assistant
```

btrfs balance

```shell
sudo btrfs balance start --bg /
sudo btrfs balance status /
```

查看使用情况

```shell
sudo btrfs fi us /
```

### Xfs 相关

 xfsprogs

```shell
sudo pacman -S xfsprogs
```

检查碎片程度

```shell
sudo xfs_db -c frag -r /dev/sda1
```

进行碎片整理

```shell
sudo xfs_fsr /dev/sda1
```

xfs_info

```shell
sudo xfs_info /mnt/data
```

## 内存相关

### Zram

```shell
sudo pacman -S zram-generator
```

配置在`/etc/systemd/zram-generator.conf`

```ini
[zram0]
zram-size = ram
compression-algorithm = lz4
```

添加 zswap.enabled=0 到内核参数

### Earlyoom

```shell
sudo pacman -S earlyoom
sudo systemctl enable --now earlyoom
```

### Sysctl

在`/etc/sysctl.d/99-sysctl.conf`

```ini
# 32G Ram + Zram(lz4) + Nvme SSD

# Contains, as bytes, the number of pages at which a process which is
# generating disk writes will itself start writing out dirty data.
vm.dirty_bytes = 536870912    # 512MB

# Contains, as bytes, the number of pages at which the background kernel
# flusher threads will start writing out dirty data.
vm.dirty_background_bytes = 134217728  # 128MB

# Decreasing the virtual file system (VFS) cache parameter value
# may improve system responsiveness (default 100)
vm.vfs_cache_pressure = 50

# The sysctl swappiness parameter determines the kernel's preference for pushing anonymous pages or page cache to disk in memory-starved situations.
# A low value causes the kernel to prefer freeing up open files (page cache), a high value causes the kernel to try to use swap space,
# For in-memory swap, like zram or zswap, as well as hybrid setups that have swap on faster devices than the filesystem, values beyond 100 can be considered.
vm.swappiness = 150

# page-cluster controls the number of pages up to which consecutive pages are read in from swap in a single attempt.
# This is the swap counterpart to page cache readahead. The mentioned consecutivity is not in terms of virtual/physical addresses,
# but consecutive on swap space - that means they were swapped out together. (Default is 3)
# increase this value to 1 or 2 if you are using physical swap (1 if ssd, 2 if hdd)
vm.page-cluster = 0
```

## 性能相关

### 电源管理

```shell
sudo pacman -S profile-sync-daemon
sudo systemctl enable --now power-profiles-daemon.service
```

### 添加 CachyOS znver4 仓库

混用仓库有风险。

```ini
[cachyos-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[cachyos-core-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[cachyos-extra-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist

[archlinuxcn]
Include = /etc/pacman.d/archlinuxcn-mirrorlist

[arch4edu]
Server = https://mirrors.tuna.tsinghua.edu.cn/arch4edu/$arch

[chaotic-aur]
Include = /etc/pacman.d/chaotic-mirrorlist
```

### 编译优化

配置了`~/.makepkg.conf`

```bash
CFLAGS="-march=native -mtune=native -O2 -pipe -fno-plt -fexceptions \
        -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security \
        -fstack-clash-protection -fcf-protection \
        -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer"
CXXFLAGS="$CFLAGS -Wp,-D_GLIBCXX_ASSERTIONS"
RUSTFLAGS="-C opt-level=3 -C target-cpu=native -C link-arg=-z -C link-arg=pack-relative-relocs"
MAKEFLAGS="-j$(nproc) -l$(nproc)"
```

### Ananicy-cpp

```shell
sudo pacman -S ananicy-cpp cachyos-ananicy-rules-git
systemctl enable --now ananicy-cpp.service
```

### Proton-CachyOS

```shell
sudo pacman -S proton-cachyos
```

### Ntsync

```shell
❯ cat /etc/modules-load.d/ntsync.conf
ntsync
```

## 网络相关

### SmartDNS 接管 DNS

`/etc/smartdns/smartdns.conf` 配置：

```shell
# bind [::]:53
bind 127.0.0.1:53
bind [::1]:53

force-qtype-SOA 65

conf-file /etc/smartdns/accelerated-domains.china.smartdns.conf
conf-file /etc/smartdns/apple.china.smartdns.conf
conf-file /etc/smartdns/google.china.smartdns.conf

log-level info
cache-persist yes
cache-file /tmp/smartdns.cache
prefetch-domain yes
serve-expired yes
speed-check-mode tcp:443,ping

server-https https://223.5.5.5/dns-query -bootstrap-dns -exclude-default-group
server-https https://223.6.6.6/dns-query -group china -exclude-default-group
server-https https://1.12.12.12/dns-query -group china -exclude-default-group
server-https https://120.53.53.53/dns-query -group china -exclude-default-group
server-https https://1.1.1.1/dns-query
server-https https://1.0.0.1/dns-query
server-https https://185.222.222.222/dns-query
server-https https://45.11.45.11/dns-query
server-https https://8.8.8.8/dns-query
server-https https://8.8.4.4/dns-query
```

`/etc/resolv.conf` 配置：

```ini
# Managed by SmartDNS
nameserver 127.0.0.1
nameserver ::1
```

smartdns 作为 daed 上游：

```shell
#dns
upstream {
  smartdns: 'tcp+udp://127.0.0.1:53'
}

#routing:
pname(smartdns) && l4proto(udp) && dport(53) -> must_direct
dip(223.5.5.5, 223.6.6.6, 1.12.12.12, 120.53.53.53) -> direct
dip(8.8.8.8, 8.8.4.4, 1.1.1.1, 1.0.0.1, 185.222.222.222, 45.11.45.11) -> proxy
```

smartdns 默认配置 `bind [::]:53` 会导致 waydroid 的 `dnsmasq` 无法绑定：

```text
dnsmasq: failed to create listening socket for 192.168.240.1: Address already in use
Failed to setup waydroid-net.
Failed to setup waydroid-net.
(645133) [22:13:00] ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(645133) [22:13:00] NOTE: The failed command's output is above the ^^^ line in the log file: /var/lib/waydroid/waydroid.log
(645205) [22:13:00] org.freedesktop.DBus.Python.RuntimeError: Traceback (most recent call last):
  File "/usr/lib/python3.13/site-packages/dbus/service.py", line 712, in _message_cb
    retval = candidate_method(self, *args, **keywords)
  File "/usr/lib/waydroid/tools/actions/container_manager.py", line 31, in Start
    do_start(self.args, session)
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/waydroid/tools/actions/container_manager.py", line 138, in do_start
    tools.helpers.run.user(args, command)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/usr/lib/waydroid/tools/helpers/run.py", line 58, in user
    return tools.helpers.run_core.core(args, msg, cmd, working_dir, output,
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                     output_return, check, sudo)
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/waydroid/tools/helpers/run_core.py", line 343, in core
    check_return_code(args, code, log_message)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/waydroid/tools/helpers/run_core.py", line 219, in check_return_code
    raise RuntimeError("Command failed: " + log_message)
RuntimeError: Command failed: % /usr/lib/waydroid/data/scripts/waydroid-net.sh start

(645205) [22:13:00] RuntimeError: Command failed: % /usr/lib/waydroid/data/scripts/waydroid-net.sh start
(645259) [22:13:02] WayDroid session is stopped
```

需要修改为只在本机回环地址监听：

```shell
# bind [::]:53
bind 127.0.0.1:53
bind [::1]:53
...
```

## 备份相关

### Snapper 配置

@ @home 配置一致。

```ini
# subvolume to snapshot
SUBVOLUME="/"

# filesystem type
FSTYPE="btrfs"


# btrfs qgroup for space aware cleanup algorithms
QGROUP=""


# fraction or absolute size of the filesystems space the snapshots may use
SPACE_LIMIT="0.2"

# fraction or absolute size of the filesystems space that should be free
FREE_LIMIT="0.3"


# users and groups allowed to work with config
ALLOW_USERS="zhui"
ALLOW_GROUPS=""

# sync users and groups from ALLOW_USERS and ALLOW_GROUPS to .snapshots
# directory
SYNC_ACL="no"


# start comparing pre- and post-snapshot in background after creating
# post-snapshot
BACKGROUND_COMPARISON="yes"


# run daily number cleanup
NUMBER_CLEANUP="yes"

# limit for number cleanup
NUMBER_MIN_AGE="3600"
NUMBER_LIMIT="3"
NUMBER_LIMIT_IMPORTANT="1"


# create hourly snapshots
TIMELINE_CREATE="yes"

# cleanup hourly snapshots after some time
TIMELINE_CLEANUP="yes"

# limits for timeline cleanup
TIMELINE_MIN_AGE="1800"
TIMELINE_LIMIT_HOURLY="1"
TIMELINE_LIMIT_DAILY="2"
TIMELINE_LIMIT_WEEKLY="0"
TIMELINE_LIMIT_MONTHLY="0"
TIMELINE_LIMIT_QUARTERLY="0"
TIMELINE_LIMIT_YEARLY="0"


# cleanup empty pre-post-pairs
EMPTY_PRE_POST_CLEANUP="yes"

# limits for empty pre-post-pair cleanup
EMPTY_PRE_POST_MIN_AGE="3600"
```

用 snapper-timeline.timer 和 snap-pac 创建快照，配合 btrfs-assistant 管理。

```shell
sudo pacman -S snap-pac
sudo systemctl enable --now snapper-timeline.timer
sudo systemctl enable --now snapper-cleanup.timer
```

降低快照创建/清理频率。

```shell
sudo systemctl edit snapper-timeline.timer
sudo systemctl edit snapper-cleanup.timer
```

```ini
➜ cat /etc/systemd/system/snapper-timeline.timer.d/override.conf
[Timer]
OnCalendar=
OnBootSec=257m
OnUnitActiveSec=257m

➜ cat /etc/systemd/system/snapper-cleanup.timer.d/override.conf 
[Timer]
OnBootSec=
OnUnitActiveSec=
OnBootSec=10m
RandomizedDelaySec=17m
OnUnitActiveSec=1d
Persistent=true
```

## 沙盒相关

### Flatpak 管理 Steam

为了避免 steam 里一些游戏扫盘、在 home 拉屎，用 flatpak 管理，配合 @game 子卷进行隔离。

```shell
flatpak --user remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak --user install flathub com.valvesoftware.Steam
```

### Portable-arch

有一些写好的可以直接用，编辑 `/etc/paru.conf` ,添加：

```ini
[portable]
Url = https://github.com/Kraftland/portable-arch.git
Depth = 10
```

用法见 [Kraftland/portable-arch](https://github.com/Kraftland/portable-arch).

## 杂项

### 禁止鼠标唤醒

为了避免鼠标唤醒系统，配置了`/etc/udev/rules.d/logitech-unifying.rules`

```ini
ACTION=="add|change", SUBSYSTEM=="usb", DRIVERS=="usb", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c53f", ATTR{power/wakeup}="disabled"
```

### 定时清理包

```shell
sudo pacman -S pacman-contrib
sudo systemctl enable --now paccache.timer
```

### Wayland 混成器设置为 KWin

配置了`/etc/sddm.conf.d/10-wayland.conf`

```ini
[General]

DisplayServer=wayland

GreeterEnvironment=QT_WAYLAND_SHELL_INTEGRATION=layer-shell


[Wayland]

CompositorCommand=kwin_wayland --drm --no-lockscreen --no-global-shortcuts --locale1
```

### Fontconfig

- 参考 [Fontconfig 和 Noto Color Emoji 和抗锯齿](https://sh.alynx.one/posts/Fontconfig-NotoColorEmoji-Antialias/)

- 额外装了 [ttf-jigmo](https://kamichikoichi.github.io/jigmo/)

- [字体试验页](https://web.archive.org/web/20250226125025/https://ctext.org/font-test-page/zhs)

### 禁止 Discover 检查更新自启动

```shell
cp /etc/xdg/autostart/org.kde.discover.notifier.desktop ~/.config/autostart/
```

添加 Hidden=true 到文件末尾。

### 内存条光污染

[OpenRGB](https://gitlab.com/CalcProgrammer1/OpenRGB) 可以手动控制，配了 `/etc/systemd/system/openrgb-sleep.service` 睡眠/唤醒时触发。

```ini
[Unit]
Description=OpenRGB Sleep Control (Suspend/Resume)
Before=sleep.target
StopWhenUnneeded=true

[Service]
Type=oneshot
ExecStart=/usr/bin/openrgb --device "ENE DRAM" --mode off
ExecStopPost=/usr/bin/openrgb --device "ENE DRAM" --mode Rainbow
RemainAfterExit=yes

[Install]
WantedBy=sleep.target
```

### Sudo 超时设置

默认是每个终端都需要输入密码，且超时时间是 5 分钟，不太方便。

`sudo visudo -f /etc/sudoers.d/99-sudo-timeout` 写入下面两行，`sudo visudo -c` 检查有 "bad permissions, should be mode 0440", 需要 `sudo chmod 0440 /etc/sudoers.d/99-sudo-timeout`.

```ini
Defaults timestamp_type=global
Defaults timestamp_timeout=30
```

### 关 VSync 开 Adaptive-Sync

在游戏里关闭 vsync, 在显示器 osd 菜单中开启 adaptive-sync.

开启 adaptive-sync 后，kde 系统设置 -> 显示和监视器 -> 显示器配置 界面会多一个 adaptive-sync 选项。

### Rainy 75 键盘改键

无论使用 VIA 还是官方网页，都需要满足以下两点：

1.给设备临时权限，日志`chrome://device-log`中若出现：

```shell
HIDEvent[10:17:15] Failed to open '/dev/hidraw14': FILE_ERROR_ACCESS_DENIED
HIDEvent[10:17:15] Access denied opening device read-write, trying read-only.
```

执行：`sudo chmod a+rw /dev/hidraw14`

2.启用 WebHID 权限，在 Chromium 中打开：`chrome://flags/#enable-experimental-web-platform-features`设为 **Enabled**，然后重启浏览器。