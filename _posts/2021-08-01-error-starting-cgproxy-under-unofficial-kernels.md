---
title: 非官方内核下启动cgproxy出错
categories: [linux,tool]
comments: true
math: false
---

<a data-fancybox="gallery" href="https://cdn.jsdelivr.net/gh/riveronvenus/blog-pic/img/kernels-cgproxy/image01.png"><img src="https://cdn.jsdelivr.net/gh/riveronvenus/blog-pic/img/kernels-cgproxy/image01.png">

 * TOC
{:toc}
# 前言

前段时间我一直在尝试不同的内核，想以此来提高电脑的性能。官方支持的内核中我使用过[linux-zen](https://archlinux.org/packages/?name=linux-zen){:target="blank"}, 非官方支持的内核中我使用过[linux-ck](https://aur.archlinux.org/packages/linux-ck/){:target="blank"}, [linux-lqx](https://aur.archlinux.org/packages/linux-lqx/){:target="blank"}, [linux-xanmod](https://aur.archlinux.org/packages/linux-xanmod/){:target="blank"}, [linux-xanmod-cacule](https://aur.archlinux.org/packages/linux-xanmod-cacule/){:target="blank"}, [linux-cacule](https://aur.archlinux.org/packages/?K=linux-cacule){:target="blank"}。其中，使用linux-zen, linux-ck时cgproxy正常，而使用其它几个内核时启动却出错，导致无法使用。

# 出错

在Arch Linux下我一直使用[qv2ray](https://github.com/Qv2ray/Qv2ray){:target="blank"} + [cgproxy](https://github.com/springzfx/cgproxy){:target="blank"}来使用代理，非常好用，在这里我不一一赘述了。查看出错时的服务状态`systemctl status cgproxy.service`:

```
● cgproxy.service - cgproxy service
     Loaded: loaded (/usr/lib/systemd/system/cgproxy.service; enabled; vendor preset: disabled)
     Active: active (running)
   Main PID: 472 (cgproxy)
      Tasks: 2 (limit: 9255)
     Memory: 5.4M
        CPU: 115ms
     CGroup: /system.slice/cgproxy.service
             └─472 /usr/bin/cgproxy --daemon --execsnoop

cgproxyd[472]: info: socketserver thread started
cgproxyd[472]: info: loading /usr/lib/cgproxy/libexecsnoop.so
cgproxyd[472]: info: dlsym startThread func success
cgproxyd[472]: libbpf: elf: skipping unrecognized data section(10) .eh_frame
cgproxyd[472]: libbpf: elf: skipping relo section(11) .rel.eh_frame for section(10) .eh_frame
cgproxyd[472]: libbpf: failed to determine tracepoint 'syscalls/sys_enter_execve' perf event ID: No such file or directory
cgproxyd[472]: libbpf: prog 'syscall_enter_execve': failed to create tracepoint 'syscalls/sys_enter_execve' perf event: No such file or directory
cgproxyd[472]: failed to attach BPF programs
cgproxyd[472]: error: execsnoop thread timeout, maybe failed
```

经过分析已有信息和对比各个内核的config以及最后测试，确定了是这些内核直接或间接禁用了**CONFIG_FTRACE_SYSCALLS**造成的。

# 解决

（最后更新时间 2021-08-20，由于内核更新较快，且PKGBUILD和config也会有所改变，所以以下方法可能过时，仅供参考）

编译内核时在config中启用*CONFIG_FTRACE_SYSCALLS*或*CONFIG_FTRACE*即可解决。

- ~~对于linux-cacule系列的内核，将其PKGBUILD中禁用*CONFIG_FTRACE*的语句`scripts/config --disable CONFIG_FTRACE`注释掉或删掉以启用*CONFIG_FTRACE_SYSCALLS*~~
- (2021-08-20更新) 对于linux-cacule系列内核，在其PKGBUILD中加入两条语句`scripts/config --enable CONFIG_FTRACE`和 `scripts/config --enable CONFIG_FTRACE_SYSCALLS`以启用*CONFIG_FTRACE_SYSCALLS*
- 对于linux-lqx, 在其PKGBUILD中加入语句`scripts/config --enable CONFIG_FTRACE_SYSCALLS`以启用*CONFIG_FTRACE_SYSCALLS*
- 对于linux-xanmod系列内核，在其PKGBUILD中加入两条语句`scripts/config --enable CONFIG_FTRACE`和 `scripts/config --enable CONFIG_FTRACE_SYSCALLS`以启用*CONFIG_FTRACE_SYSCALLS*

# 最后

就我而言，不知道是不是心理作用，相对于默认内核感觉使用这些内核在系统响应能力上有一些提升，其次在编译内核时会快一点。
