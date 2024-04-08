---
title: 在 Arch Linux 上使用 Cloudflare WARP+
categories: [linux,tool]
comments: true
---

WARP+ 是 Cloudflare 提供的一项网络加速服务，用于改善互联网连接的速度和安全性。WARP+ 旨在通过优化网络路径，减少延迟，并提供更快的网络连接体验。

这里说的 WARP+ 属于 WARP+ Limited，流量是有限的，通过推广获得免费的服务，但是通过 Warp+ Bot 可以获得 24.59PB 流量，也可以说是 Unlimited 了。而真正的 WARP+ Unlimited 属于付费服务。

关于它们的区别：[What is the difference between WARP, WARP+, and WARP+ Unlimited?](https://support.cloudflarewarp.com/hc/en-us/articles/360025731113-What-is-the-difference-between-WARP-WARP-and-WARP-Unlimited-){:target="blank"}

## 安装

从 AUR 上或者信得过的第三方仓库安装  

```
➜ paru -Ss cloudflare-warp-bin
cachyos/cloudflare-warp-bin 2023.7.40-1 [0B 49.98MiB] [Installed]
    Cloudflare Warp Client
aur/cloudflare-warp-bin 2023.7.40-1 [+41 ~3.15] [Installed]
    Cloudflare Warp Client
```

## 使用

### WARP

只需要 3 个命令就能使用 WARP，先启动 `warp-svc.server`，第一次使用时需要 `register` 进行身份验证，然后 `connect` 将启用客户端，创建从设备到 Cloudflare 网络的 WireGuard 隧道。

```
➜ sudo systemctl start warp-svc.service // 启动服务

➜ warp-cli register // 进行身份验证
Success

➜ warp-cli connect // 连接
Success
```

此时查看帐户信息可以看到 `Account type: Free`

```
➜ warp-cli account
Account type: Free
...
```

通过 cloudflare trace 看到 `warp=on`

```
➜ curl https://www.cloudflare.com/cdn-cgi/trace/
...
warp=on
...
```

至此 WARP 就可以使用了。

### WARP+

使用  WARP+ 需要去 [Warp+ Bot](https://t.me/generatewarpplusbot){:target="blank"} 获得 **License Key**，然后 `set-license`使用 Key

```
❯ warp-cli set-license xxxxxxxx-xxxxxxxx-xxxxxxxx // 得到的 License Key
Success
```

这时查看帐户信息，可以看到 `Account type: Limited`，有 **24598562000000000 B = 24.5986 PB** 流量配额，根本用不完。

```
➜ warp-cli account                    
Account type: Limited
...
Quota: 24598562000000000
Premium Data: 24598562000000000
```

通过 cloudflare trace 看到 `warp=plus`

```
➜ curl https://www.cloudflare.com/cdn-cgi/trace/
...
warp=plus
...
```

至此 WARP+ 就可以使用了。

### MODE

mode 有多种，根据需求设置

```
➜ warp-cli set-mode -h
Set the mode

Usage: warp-cli set-mode <MODE>

Arguments:
  <MODE>  [possible values: warp, doh, warp+doh, dot, warp+dot, proxy, tunnel_only]

Options:
  -h, --help  Print help
```

我需要 `proxy` 模式

```
➜ warp-cli set-mode proxy // 默认端口是 40000, 127.0.0.1:40000
Success
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

更多命令`warp-cli --help`

## 使用体验

日用勉强，更适合备用。

## 参考资料

1. [https://developers.cloudflare.com/warp-client/get-started/linux/](https://developers.cloudflare.com/warp-client/get-started/linux/){:target="blank"}
