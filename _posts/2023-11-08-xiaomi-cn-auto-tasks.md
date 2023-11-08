---
title: 小米社区自动签到/任务
categories: [misc]
comments: true
---

今天[小米社区](https://www.xiaomi.cn/){:target="blank"}对 Bootloader 解锁权限发布了公告：要求通过《解锁资格答题测试》，社区成长等级达到 5 段；完成实名认证，才能申请解锁，申请一次有效期只有一年，每年最多支持三台设备解锁，解锁等待期为 72 小时。

试着去答了一下《解锁资格答题测试》，很简单，90 多分，都是一些常识和常用命令，但是我社区等级才 2 级，小米社区升级太慢了，又经常忘记签到做任务，于是找到了 [miui-auto-tasks](https://github.com/0-8-4/miui-auto-tasks){:target="blank"} - 一个自动化完成小米社区任务的脚本。照着它的 [wiki](https://github.com/0-8-4/miui-auto-tasks/wiki){:target="blank"} 配置，功能全开（~~用就不要怕~~）

```yaml
accounts:
  - uid: xxxxxxxxx
    # 账户ID 非账户用户名或手机号
    password: xxxxxxxxxxxxxxxxxxxxxxxxx
    # 账户密码或其MD5哈希
    user-agent: 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'
    # 登录社区时所用浏览器的 User-Agent
    # 可在此工具查看：https://tool.chinaz.com/useragent
    
    # 功能开关
    check-in: true
    # 社区成长值签到，启用功能意味着你愿意自行承担相关风险
    browse-user-page: true
    # 社区浏览个人主页10秒，启用功能意味着你愿意自行承担相关风险
    browse-post: true
    # 社区浏览帖子10秒，启用功能意味着你愿意自行承担相关风险
    thumb-up: true
    # 点赞帖子，启用功能意味着你愿意自行承担相关风险
    browse-specialpage: true
    # 社区在活动期间可能会出现限时的“浏览指定专题页”任务，启用功能意味着你愿意自行承担相关风险
    board-follow: true
    # 社区可能会出现限时的“加入圈子”任务，启用功能意味着你愿意自行承担相关风险
    carrot-pull: true
    # 社区拔萝卜，启用功能意味着你愿意自行承担相关风险

# 若有多个账户，按照以下模板进行修改，使用时删除前端 #注释
#  - uid: 100001
#    password: abc123
#    user-agent: 'Mozilla/5.0 (Android 11; Mobile; rv:95.0) Gecko/95.0 Firefox/95.0'
#    check-in: false
#    browse-user-page: false
#    browse-post: false
#    thumb-up: false
#    browse-specialpage: false
#    board-follow: false
#    carrot-pull: false
ONEPUSH:
  notifier: telegram
  params:
    title:
    markdown: false
    token:
    userid:

logging: false
# 归档日志到本地文件
version: v1.6.0
# config 文件版本号，debug用

```

用 systemd timer 让它每天执行，先在 `/etc/systemd/user/` 创建一个 [Service] 执行 python 程序，

```bash
[Unit]
Description=MIUI Auto Tasks

[Service]
Type=oneshot
ExecStart=%h/venv/bin/python %h/pytools/miui-auto-tasks/miuitask.py
```

再创建一个 [Timer] 定时执行，

```bash
[Unit]
Description=Run MIUI Auto Tasks Every Day

[Timer]
OnBootSec=3min
OnCalendar=*-*-* 12:00:00
RandomizedDelaySec=10min
Persistent=true
Unit=miui-auto-tasks.service

[Install]
WantedBy=timers.target
```

用 `systemctl --user enable --now` 跑起来，根据我使用电脑的习惯，应该每天都能跑一遍。

参考资料：

1. [https://wiki.archlinux.org/title/Systemd](https://wiki.archlinux.org/title/Systemd){:target="blank"}
2. [https://wiki.archlinux.org/title/Systemd/Timers](https://wiki.archlinux.org/title/Systemd/Timers){:target="blank"}
