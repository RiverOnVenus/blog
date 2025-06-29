---
title: 在复现 GPU bug 时，触发了 Btrfs bug
categories: [linux,btrfs,amd]
comments: true
---

* TOC
{:toc}
## 起因

这次算是运气不好，得记一下。起因是更新了 linux-firmware-amdgpu 20250613.12fe085f-6，重启后黑屏。因为有 amdgpu 固件更新，怀疑是独显输出的问题，于是把 DP 线拔了，换成了 HDMI，果然正常进入桌面。想着复现确认一下，又把 DP 接回去。当看到这次开机不是黑屏，而是被扔到 emergency shell 时，我意识到不对劲。

## 经过

首先映入眼帘的是一些 kp 信息，后面紧跟着 2 个 error, 一个是 / 挂载不上，一个是 amdgpu drm error，后者原本临时降级就行，但现在只能进 live 看下 / 为什么挂载不上。

<figure class="fancy-figure">
  <a data-fancybox="rescue" href="https://image.zhui.dev/file/1751176716020_kp.jpg">
    <img src="https://image.zhui.dev/file/1751176716020_kp.jpg" alt="Kernel Panic">
  </a>
  <figcaption>Kernel Panic</figcaption>
</figure>

进入 live 后手动挂载 /，仍然无法挂载，用 journalctl -k --grep=BRTFS 可以看到有 open_ctree failed.

<figure class="fancy-figure">
  <a data-fancybox="rescue" href="https://image.zhui.dev/file/1751177521997_btrfs-error-01.jpg">
    <img src="https://image.zhui.dev/file/1751177521997_btrfs-error-01.jpg" alt="journalctl -k --grep=BRTFS">
  </a>
  <figcaption>journalctl -k --grep=BRTFS</figcaption>
</figure>
btrfs check 看起来是正常的。

<figure class="fancy-figure">
  <a data-fancybox="rescue" href="https://image.zhui.dev/file/1751178066902_btrfs-check.jpg">
    <img src="https://image.zhui.dev/file/1751178066902_btrfs-check.jpg" alt="btrfs check">
  </a>
  <figcaption>btrfs check</figcaption>
</figure>

虽然网上搜到了一些相关案例和解决方法，但作为 btrfs 新手的我没有贸然尝试，怕把现场弄得更糟糕，于是在群里问了下，群友让给完整的 log，不要过滤。

<figure class="fancy-figure">
  <a data-fancybox="rescue" href="https://image.zhui.dev/file/1751177973461_btrfs-error-02.jpg">
    <img src="https://image.zhui.dev/file/1751177973461_btrfs-error-02.jpg" alt="journalctl -k">
  </a>
  <figcaption>journalctl -k</figcaption>
</figure>

<figure class="fancy-figure">
  <a data-fancybox="rescue" href="https://image.zhui.dev/file/1751177973365_btrfs-error-03.jpg">
    <img src="https://image.zhui.dev/file/1751177973365_btrfs-error-03.jpg" alt="journalctl -k">
  </a>
  <figcaption>journalctl -k</figcaption>
</figure>
经过一些尝试未果后，有群友指出问题出在 replay log 的过程中，所以实在不行可以尝试 zero log.

在`sudo btrfs rescue zero-log /dev/nvme0n1p2`后果然可以挂载了。进 live 后降级 amdgpu 固件，黑屏也临时解决了。最后确认了磁盘 check, scrub 都没问题。

## 缘由

更新固件后重启黑屏的原因是，arch 上 backport 了这笔 [commit](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/commit/?id=a26e413e7481d12ab5a53f77e0cdde2d5be937d8), rx 9000 系列的显卡会有影响，现在已经修复了。

被扔到 emergency shell 的原因是触发了 btrfs log replay bug，导致 / 挂载不上。zero log 可解决，这是后来看到这几天有其他群友也遇到相同问题，以及看到这笔修复 [commit ](https://github.com/torvalds/linux/commit/2dcf838cf5c2f0f4501edaa1680fcad03618d760)才确认的。在 v6.15.4-arch2 中也修复了。

## 结束

事后回顾这次问题时，发现在 btrfs 文档里有提到：

> One can determine whether **zero-log** is needed according to the kernel backtrace:
>
> ```
> ? replay_one_dir_item+0xb5/0xb5 [btrfs]
> ? walk_log_tree+0x9c/0x19d [btrfs]
> ? btrfs_read_fs_root_no_radix+0x169/0x1a1 [btrfs]
> ? btrfs_recover_log_trees+0x195/0x29c [btrfs]
> ? replay_one_dir_item+0xb5/0xb5 [btrfs]
> ? btree_read_extent_buffer_pages+0x76/0xbc [btrfs]
> ? open_ctree+0xff6/0x132c [btrfs]
> ```
>
> If the errors are like above, then **zero-log** should be used to clear the log and the filesystem may be mounted normally again. The keywords to look for are ‘open_ctree’ which says that it’s during mount and function names that contain *replay*, *recover* or *log_tree*.

还是得多看文档啊。
