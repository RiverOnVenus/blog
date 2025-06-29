---
title: 玩机之初
categories: [android]
comments: true
---

今年年初，用了几年的手机坏了，正好红米 K60 发布，在 K50 Ultra 和 K60 之间纠结了会儿，最后选了 K60。

到手后开始接触了刷机，小米手机相关的刷机资源和教程还挺多。

了解一些知识后开始解 BL 锁，不得不说等待的 7 天过得真慢，等待的时候开始选要用的 ROM，原来手机 ROM 有这么多，最后选择了 Xiaomi.eu WEEKLY ROM.

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

----

 六月初从 Magisk Delta 换到了 KernelSU.

----

前几天从 MIUI14.0.23.9.18.DEV ---> HyperOS1.0.23.12.04.DEV 发现 EU 又内置了过设备完整性`MEETS_DEVICE_INTEGRITY`的方法（内置了一个 [XiaomiEUModule.apk](https://sourceforge.net/projects/xiaomi-eu-multilang-miui-roms/files/xiaomi.eu/Xiaomi.eu-app/)），不需要额外的模块了。
