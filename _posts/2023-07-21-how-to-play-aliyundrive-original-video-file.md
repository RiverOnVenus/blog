---
title: 如何播放阿里云盘原始视频文件
categories: [tool]
comments: true
---

原始视频文件清晰度有 1080p/2k/4k , 但在阿里云盘官方软件没会员只有 480p ，这谁受得了？为了能播放最高清晰度的视频我找到了[阿里云盘小白羊版](https://github.com/liupan1890/aliyunpan){:target="blank"}，通过 mpv 等播放器能够播放原始清晰度。最近发现原版没人维护，有些 bug 很难受，又找到了 [fork 版1](https://github.com/odomu/aliyunpan){:target="blank"}和 [fork 版2](https://github.com/gaozhangmin/aliyunpan){:target="blank"}.

虽然小白羊版在电脑上能播放原始文件的清晰度，但是手机上却没找到这种工具。

直到遇到了 [alist](https://github.com/alist-org/alist){:target="blank"} -- A file list program that supports multiple storages, powered by Gin and Solidjs. / 一个支持多存储的文件列表程序，使用 Gin 和 Solidjs。

在本地启动后，家里任何一台设备都能访问，简直太棒啦，结束了 2k 屏看 480p 的日子。

家里部署好了，又想在外面也能用上，在外面用的话那不是得整一台服务器，虽然内网穿透也可以，但我试过了，有点卡，而且长时间出门我习惯给电脑睡眠/关机。

算了，先这样吧。

------

用了一段时间后，我发现在手机上跑 alist 更舒服，可以完美解决我的所有问题，家里/外面都能用了，还省了服务器的钱。

当然，alist 的功能不止于此。
