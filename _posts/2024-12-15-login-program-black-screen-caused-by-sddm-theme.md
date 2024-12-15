---
title: SDDM 主题导致登录程序黑屏
categories: [linux]
comments: true
---

这天我打开电脑发现开机后屏幕黑屏，只有鼠标光标可见，登录界面没有显示。看着唯一的光标我开始思考上次做了什么——想不起来了～

我尝试在终端中执行 `startplasma-wayland`，发现能够正常进入桌面。这表明桌面环境本身是正常的，问题可能出在登录管理器上。

开始查看日志，发现 sddm 在加载主题的时候有问题。

<a data-fancybox="image" href="https://image.zhui.dev/file/1734183422289_image.png"><img src="https://image.zhui.dev/file/1734183422289_image.png">

看了下配置文件，的确配置了「plasma-chili」

<a data-fancybox="image" href="https://image.zhui.dev/file/1734183307596_image.png"><img src="https://image.zhui.dev/file/1734183307596_image.png">

思考，我什么时候把「微风」改了:thinking:

改回 Current=breeze 重启，熟悉的「微风」回来了。应该是因为「[plasma-chili](http://store.kde.org/p/1214121/)」是基于 plasma5 做的主题，导致了这个问题。

