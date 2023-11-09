---
title: 玩机之初
categories: [misc]
comments: true
---

今年年初，用了几年的手机坏了 :frowning_face:

正好红米 K60 发布，在 K50 Ultra 和 K60 之间纠结了会儿，最后选了 K60。

到手后开始接触了刷机，小米手机相关的刷机资源和教程还挺多。

了解一些知识后开始解 BL 锁，不得不说等待的 7 天过得真慢 :neutral_face:

等待的时候开始选要用的 ROM，原来手机 ROM 有这么多，最后选择了 Xiaomi.eu WEEKLY ROM :blush:

BL 解锁完成，EU 刷入完成。

又到了经典的二选一，Root 有两种方式，一种是 Magisk，一种是 KernelSU，最后选择了 Magisk Delta.

Xiaomi.eu ROM 里有现成的 boot.img，不用手动提取了。

刷 boot 时，不知道是

```bash
fastboot flash boot boot.img
```

还是

```bash
fastboot flash boot_ab boot.img
```

在 ROM 的脚本 `linux_fastboot_first_install_with_data_format.sh` 里发现了这行

```bash
$fastboot flash boot_ab images/boot.img
```

于是采用了 boot_ab 的方式刷入。

后面每周 ROM 更新都要

1. 下载 ROM
2. 刷入 ROM
3. 修补 boot.img
4. 刷入 boot.img

虽然不麻烦，但是有些麻烦。所以后来不是每周都更新，一是看心情，二是看更新了什么内容。

到今天，已经用了三个多月了，Root 后没有遇见什么奇奇怪怪的问题，指纹人脸也没有掉，Root 隐藏得也很好。倒是刷了一些奇奇怪怪的模块，模块数量从少变多再变少。<span class="spoiler" >另外，听说刷机得在中午刷。</span>

