---
title: 换到 KernelSU 啦
categories: [misc]
comments: true
---

 六月初从 Magisk Delta 换到了 KernelSU, 因为要用某个 app 但过不了 root 检测，于是想到了 KernelSU, 结果真能过啊，EU 完美过 Play Integrity 和 SafetyNet.  另外 KernelSU 的 **root profile** 很棒。

使用 KernelSU 一个月的感受：相见恨晚。

没想到今晚 Magisk Delta 更到 v26.1 了，更没想到作者说 : "Switched to KernelSU on my primary device. Still use Magisk on secondary device."

~~EU 以前不需要模块就能过 Play Integrity 和 SafetyNet, 现在需要安装 fix 模块才行。~~

----

> - SafetyNet passed by default without ROOT (Google Pay)
> - Play Store Certified

昨天从 MIUI14.0.23.9.18.DEV ---> HyperOS1.0.23.12.04.DEV 发现 EU 又内置了解决方法（内置了一个 XiaomiEUModule.apk），不需要额外的模块了。如果 Google 又更新了验证方法，且 EU ROM 还没更新时，可以下载最新的 [XiaomiEUModule.apk](https://sourceforge.net/projects/xiaomi-eu-multilang-miui-roms/files/xiaomi.eu/Xiaomi.eu-app/){:target="blank"} 解决。

