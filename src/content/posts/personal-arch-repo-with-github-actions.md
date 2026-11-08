---
title: 用 GitHub Actions 自建 Arch 软件源
description: 把 PKGBUILD 仓库接到 GitHub Actions，构建好的包发到 Release，当软件源用。
ogImage: "https://zhui.dev/images/posts/personal-arch-repo-with-github-actions/og.jpg"
pubDatetime: 2026-10-31T00:00:00+08:00
modDatetime: 2026-11-08T17:13:58+08:00
tags:
  - linux
  - github-actions
---

## Table of contents

## 为什么建自己的源

AUR 出过几起投毒事件。攻击者批量接管孤儿包，在 PKGBUILD 的 post-install hook 里从网上拉脚本执行。还有些包打包质量一般，本地改完用着没问题，但 AUR 一更新，改动就被盖掉了。干脆建一个自己的源，所有包都交给 pacman 管。得益于 AI，我可以方便地管理这些包。

## 仓库结构

每个包一个目录，目录名就是 pkgname。

```
AUR-packages/
├── aur-packages.txt
├── magpie-bin/
│   ├── PKGBUILD
│   └── .nvchecker.toml
└── uu-remote-linux/
    ├── PKGBUILD
    ├── .nvchecker.toml
    ├── 60-uu-remote-linux-uinput.rules
    └── uuremote-native.service
```

`aur-packages.txt` 是 AUR 白名单。不在名单里的目录照样构建、照样进自己的源，只是不会上传到 AUR。这些包大多是从 AUR 或 [portable-arch](https://github.com/Kraftland/portable-arch) 搬过来的 fork。目的是让这些包由我的 CI 里的 PKGBUILD 构建，从我的源更新。

## 一次 push 做什么

`.github/workflows/push_aur.yml` 分五段。

```
generate-matrix → preflight（有 AUR 包时）→ build（每个包一个 job）→ push-aur → publish-repo
```

**generate-matrix** 决定这次构建哪些目录。它不和这次 push 的父提交比较，而是通过 Actions API 找到上一次完全成功的 `push_aur.yml` run，再和那次 run 的 `head_sha` 做 diff。

```bash
# base 取自上一次完全成功的 push run
git diff --name-only "$base" "$GITHUB_SHA" | grep -v '/\.nvchecker\.toml$' | cut -d/ -f1 | sort -u
```

这样构建失败的包、因为 concurrency 没排上的 run，都会在下一次 push 时补上。代价是只要还有一个包失败，自上次成功以来改过的其他目录也会在每次 push 时跟着重建。找不到成功记录，或者那条记录不在当前历史里，就构建全部。当前 commit 比上次成功的还旧时直接跳过，避免重跑旧 run 把更早的包发布出去。

手动触发且 `packages` 留空时构建全部。改 `aur-packages.txt` 时，新增的行也要构建，否则新包永远到不了 AUR，所以这一步单独算一次白名单的差集。只改 `.nvchecker.toml` 不触发构建。

**preflight** 用推 AUR 的同一把 SSH key 跑 `list-repos`，确认白名单里的包确实在自己名下。新名字在 AUR 上不存在是允许的，第一次 push 会创建。它只在本次有包要推时运行，和 build 并行，失败也只挡住后面的 `push-aur`，个人仓库的构建和发布照常进行。AUR 临时出问题时，源不会跟着停更。

**build** 是一个 matrix，一个包一个 job，`fail-fast: false`。构建在 `archlinux:base-devel` 容器里跑，用的是仓库内的 `.github/scripts/build-package.sh`。容器以 root 启动，脚本另建一个 `builder` 用户来跑 `makepkg` 和 `paru`，两者都拒绝以 root 运行。依赖先查官方源，再查 `zhui-arch` 的 Release，最后才落到 AUR。`paru` 从 archlinuxcn 临时装上，装完依赖就删掉，其他包不会从 archlinuxcn 混进来。构建结束会跑一遍 `namcap`，警告写进 job 日志。

带 epoch 的包文件名里有冒号（`pkgname-1:2.0-1-x86_64.pkg.tar.zst`），工作流会把文件名里所有非 `[A-Za-z0-9._-]` 的字符换成下划线再往下传，不只是冒号。版本号来自包内的 `.PKGINFO`，文件名只是存储位置，pacman 照常比较版本，升级不受影响。

白名单里的包还有一段独立的 `push-aur`，跑在单独的 VM 上。每个包先确认自己的构建产物存在，没构建成功就跳过。`.SRCINFO` 在装 SSH key 之前生成，`makepkg --printsrcinfo` 只从提交的 PKGBUILD 读元数据，不跑 `pkgver()`，所以 VCS 包只有打包本身变化时才会上 AUR。之后才 clone AUR 仓库，清空，把目录里的文件拷进去，删掉 `.nvchecker.toml`，用这个目录最后一次 commit 的信息当提交信息，push。AUR 上的提交记录因此和这个仓库对应。同时最多推四个包，AUR 对并发 SSH 连接比较敏感。

**publish-repo** 在 archlinux 容器里跑，条件是 `always() && !cancelled()`，矩阵生成成功就会执行。某个包构建失败，其他包和数据库照样发布。一个包都没构建成功时也会执行，用来处理目录删除和白名单变化。

## 把产物变成 pacman 源

Release 的 asset 单独存储，不占 git 历史，单文件上限 2 GiB，适合放这种体积大的文件。

publish-repo 做四件事。下载本次所有 artifact，拉取 Release 里现有的 `zhui-arch.db` 和 `zhui-arch.files`，合并进数据库，然后上传并清理旧文件。下载回来的 db 会先检查是不是有效归档、里面有没有包条目，否则直接失败，避免用半截文件覆盖 Release 上的版本。

有几条规则。

- **数据库是合并的，不是重建的。** 每次只构建动过的包，如果 `repo-add` 从空库开始，源里剩下的包就全没了。所以每次先下载旧 db，把新包加进去。
- **先传包，最后传数据库。** 反过来的话，pacman 可能在新包上传完成前从 db 里看到新版本，然后 404。
- **目录删了，源里也要删。** 发布时扫描所有 PKGBUILD 拿到当前 pkgname，和 db 里的条目对比，多出来的 `repo-remove`，再删掉 Release 上没被引用的 asset。删 asset 之前会确认数据库能读、有内容，否则直接失败，不会按空列表把 Release 清空。
- **db 和 files 在 Release 上都是普通文件。** `repo-add` 生成 `zhui-arch.db.tar.gz` 和指向它的 `zhui-arch.db` 符号链接，files 同理。GitHub Release 上传时把链接当普通文件存，下载回来会先改名回 `.tar.gz` 再用。

## 添加源

`/etc/pacman.conf` 加一段。

```ini
[zhui-arch]
SigLevel = Optional TrustAll
Server = https://github.com/RiverOnVenus/AUR-packages/releases/download/zhui-arch
```

然后 `pacman -Syu`.

## 自动更新检查

VCS 包的版本由 `pkgver()` 算出来，不重新构建就不知道上游有没有新提交。`devel.yml` 每天 12:00 UTC（北京时间 20:00）跑一次，找出所有带 `pkgver()` 的非 `-bin` 包，用 `workflow_dispatch` 触发一次构建。少数 `-bin` 包虽然也有 `pkgver()`，但它只是从下载的产物里读版本，重建等于再下一遍。dispatch 碰到 Actions API 的临时错误会重试五次。

普通包用 nvchecker。每个非 VCS 包旁边放一个 `.nvchecker.toml`，`versions.yml` 每天 00:00 UTC（北京时间 08:00）跑一次 `pkgctl version check`，把落后的包汇总到一个 issue。issue 只是列表，不会自动改包。某个非 VCS 包没配 `.nvchecker.toml`，或者检查本身出错，run 会直接失败，漏检不会悄悄过去。

配置的原则是优先查原始上游，比如项目的 git tag、GitHub release 或 PyPI。只有上游没有可解析版本时，才退回查 AUR 同名包的版本号。这时 AUR 只是版本信号，怎么打包还是按这里的规则。

发版太勤的包（有的几十分钟一个版本）写进 `rolling-packages.txt`，照常检查、照常列出来，但不会让 issue 一直开着。

## 几个注意的点

1. concurrency 会吞掉排队的 run。连着推两次，第二次 push 会把还在排队的第一次运行取消。有一次一个还没开始的 run 就被后来的 push 顶掉了。现在不用手动重新 dispatch，下一次 push 会从上次成功的点开始，把漏掉的目录补上。

2. 容器里是 root。publish-repo 和 versions.yml 都在 `archlinux:base-devel` 容器里跑，而 `makepkg` 拒绝以 root 运行。构建脚本另建 `builder` 用户，`push-aur` 生成 `.SRCINFO` 时用 `docker run --user`，需要跑 `makepkg` 的地方都没有直接以 root 执行。

3. artifact 只留 3 天。构建产物只是用来中转的，Release 才是长期存储，旧版本的包会从 Release 里清掉。
