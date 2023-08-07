---
title: 在 Arch Linux 上使用 Cloudflare WARP+
categories: [tool]
comments: true
---

这里说的 WARP+ 属于 WARP+ Limited，流量是有限的，通过推广获得免费的服务，但是通过 Warp+ Bot 可以获得 24.59PB 流量，也可以说是 Unlimited 了。而真正的 WARP+ Unlimited 属于付费服务。

关于它们的区别：[What is the difference between WARP, WARP+, and WARP+ Unlimited?](https://support.cloudflarewarp.com/hc/en-us/articles/360025731113-What-is-the-difference-between-WARP-WARP-and-WARP-Unlimited-){:target="blank"}

# 安装

从 AUR 上或者信得过的第三方仓库安装         

```
➜ paru -Ss cloudflare-warp-bin
cachyos/cloudflare-warp-bin 2023.7.40-1 [0B 49.98MiB] [Installed]
    Cloudflare Warp Client
aur/cloudflare-warp-bin 2023.7.40-1 [+41 ~3.15] [Installed]
    Cloudflare Warp Client
```

# 使用

先启动 warp-svc server，第一次使用需要先注册，因为默认是全局代理，可以选择设置为代理模式，然后连接，最后设置保持连接。

```
➜ sudo systemctl start warp-svc.service // 启动服务

➜ warp-cli register // 注册
Success

➜ warp-cli set-mode proxy // 默认端口是 40000, 127.0.0.1:40000
Success

➜ warp-cli connect // 连接
Success

➜ warp-cli enable-always-on // 保持连接
Success
```

查看帐户信息可以看到 Account type: Free，此时并不是 WARP+，而是 WARP

```
➜ warp-cli account 
Account type: Free
Device ID: 39646a03-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Public key: 98dab3d77a9124e3daf49c49b0c3e5cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Account ID: a00434b2258xxxxxxxxxxxxxxxxxxxxx
License: MU0K1p87-xxxxxxxx-xxxxxxxx
```

需要去 [Warp+ Bot](https://t.me/generatewarpplusbot){:target="blank"} 获得 WARP+ License Key，然后设置 License Key

```
❯ warp-cli set-license 5Uj13un8-xxxxxxxx-xxxxxxxx // 得到的 License Key
Success
```

这时查看帐户信息，可以看到属于 WARP+ Limited，有 24598562000000000 B = 24.5986 PB 流量配额，根本用不完。

```
➜ warp-cli account                               
Account type: Limited
Device ID: 39646a03-xxxx-xxxx-xxxx-xxxxxxxx
Public key: db108bb0a524e193f9499b546fb8b0e77xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Account ID: c388075baaff4909b6xxxxxxxxxxxxxx
License: 5Uj13un8-xxxxxxxx-xxxxxxxx
Role: Child
Quota: 24598562000000000
Premium Data: 24598562000000000
```

查看一下 ip 信息

```
➜ curl ipinfo.io -x socks5://127.0.0.1:40000
{
  "ip": "104.28.xxx.xxx",
  "city": "Fremont",
  "region": "California",
  "country": "US",
  "loc": "xx.5483,-xxx.9886",
  "org": "AS13335 Cloudflare, Inc.",
  "postal": "94536",
  "timezone": "America/Los_Angeles",
  "readme": "https://ipinfo.io/missingauth"
}
```

更多命令`warp-cli -h`

# 使用体验

起初我主要用来看视频，因为买的节点太贵了，消耗不起 : ( ，现在基本一直用 WARP+ ，只有在它访问不了某些服务或速度不行时才用节点。速度大多数时候是很快的，看视频绰绰有余，当然也有很慢的时候。在 win 和 android 上也在用 ，在 android 上几乎是 24h 挂着，因为它启动后会一直运行，除非手动关闭，偶尔会被杀掉。WARP+ 帮我省了一大笔钱 :D
