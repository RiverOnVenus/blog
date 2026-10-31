---
title: 用 GitHub Actions 自建 Arch 软件源
description: 把 PKGBUILD 仓库接到 GitHub Actions，构建好的包发到 Release，当软件源用。
ogImage: "https://zhui.dev/images/posts/personal-arch-repo-with-github-actions/og.jpg"
pubDatetime: 2026-10-31T00:00:00+08:00
tags:
  - linux
  - github-actions
---

## Table of contents

## 为什么建自己的源

AUR 出过几起投毒事件，攻击者批量接管孤儿包，在 PKGBUILD 里加 post-install hook，安装时从网上拉一段脚本执行，另外 AUR 上有些包的打包质量一般，本地改了后用着没问题，但 AUR 版本一更新，改动就被盖掉了。干脆建一个自己的源，都用 Pacman 管理。得益于 AI，我可以方便的管理这些包。

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

`aur-packages.txt` 是 AUR 白名单。不在名单里的目录照样构建、照样进自己的源，只是不会上传到 AUR。这些包大多是从 AUR 或 [portable-arch](https://github.com/Kraftland/portable-arch) 搬过来的 fork。目的是让这些包由我的 CI 里的 PKGBUILD 构建，从我的源更新，统一用 Pacman 管理。

## 一次 push 做什么

`.github/workflows/push_aur.yml` 分四段。

```
generate-matrix → preflight → build（每个包一个 job）→ publish-repo
```

**generate-matrix** 决定构建哪些目录。默认只构建这次 push 动过的。

```bash
git diff --name-only "$BEFORE" "$GITHUB_SHA" | cut -d/ -f1 | sort -u
```

手动触发且 `packages` 留空时构建全部。改 `aur-packages.txt` 时，新增的行也要构建，否则新包永远到不了 AUR，所以这一步单独算一次白名单的差集。只改 `.nvchecker.toml` 不触发构建。

**preflight** 用推 AUR 的同一把 SSH key 跑 `list-repos`，确认白名单里的包确实在自己名下。新名字在 AUR 上不存在是允许的，第一次 push 会创建。这个检查本身很简单，能在构建几十个包之前拦下“推不上去”的错误。

**build** 是一个 matrix，一个包一个 job，`fail-fast: false`。构建用 [ouuan/pkgbuild-action](https://github.com/ouuan/pkgbuild-action)，它在 archlinux 容器里用 paru 装依赖，卸掉 paru 再跑 `makepkg -s`，AUR 上的 makedepends 也能装上。容器里用的是非 root 用户，省了在构建脚本里切用户的麻烦。

带 epoch 的包文件名里有冒号（`pkgname-1:2.0-1-x86_64.pkg.tar.zst`），工作流会先把冒号换成下划线再往下传。版本号来自包内的 `.PKGINFO`，文件名只是存储位置，pacman 照常比较版本，升级不受影响。

白名单里的包还会多一步。clone AUR 仓库，清空，把目录里的文件拷进去，用这个目录最后一次 commit 的信息当提交信息，push。所以 AUR 上的提交记录和这个仓库是对应的。

**publish-repo** 在 archlinux 容器里跑，条件是 `always() && !cancelled()`，矩阵生成成功就会执行。某个包构建失败，其他包和数据库照样发布。

## 把产物变成 pacman 源

Release 的 asset 单独存储，不占 git 历史，单文件上限 2 GiB，适合放这种体积大的文件。

publish-repo 做四件事。下载本次所有 artifact，拉取 Release 里现有的 `zhui-arch.db`，合并进数据库，然后上传并清理旧文件。

有几条规则。

- **数据库是合并的，不是重建的。** 每次只构建动过的包，如果 `repo-add` 从空库开始，源里剩下的包就全没了。所以每次先下载旧 db，把新包加进去。
- **先传包，最后传数据库。** 反过来的话，pacman 可能在新包上传完成前从 db 里看到新版本，然后 404。
- **目录删了，源里也要删。** 发布时扫描所有 PKGBUILD 拿到当前 pkgname，和 db 里的条目对比，多出来的 `repo-remove`，再删掉 Release 上没被引用的 asset。删 asset 之前会确认数据库能读、有内容，否则直接失败，不会按空列表把 Release 清空。
- **db 在 Release 上是个普通文件。** `repo-add` 生成 `zhui-arch.db.tar.gz` 和一个指向它的 `zhui-arch.db` 符号链接。GitHub Release 上传时把链接当普通文件存，下载回来会先改名回 `.tar.gz` 再用。

## 添加源

`/etc/pacman.conf` 加一段。

```ini
[zhui-arch]
SigLevel = Optional TrustAll
Server = https://github.com/RiverOnVenus/AUR-packages/releases/download/zhui-arch
```

然后 `pacman -Syu`.

## 自动更新检查

VCS 包的版本由 `pkgver()` 算出来，不重新构建就不知道上游有没有新提交。`devel.yml` 每周日跑一次，找出所有带 `pkgver()` 的非 `-bin` 包，用 `workflow_dispatch` 触发一次构建。少数 `-bin` 包虽然也有 `pkgver()`，但它只是从下载的产物里读版本，重建等于再下一遍。

普通包用 nvchecker。每个非 VCS 包旁边放一个 `.nvchecker.toml`，`versions.yml` 隔天跑一次 `pkgctl version check`，把落后的包汇总到一个 issue。

配置的原则是优先查原始上游，比如项目的 git tag、GitHub release 或 PyPI。只有上游没有可解析版本时，才退回查 AUR 同名包的版本号。这时 AUR 只是版本信号，怎么打包还是按这里的规则。

issue 只是列表，不会自动改包。

发版太勤的包（有的几十分钟一个版本）写进 `rolling-packages.txt`，照常检查、照常列出来，但不会让 issue 一直开着。

## 几个注意的点

1. concurrency 会吞掉排队的 run。连着推两次，第二次 push 会把还在排队的第一次运行取消。有一次一个还没开始的 run 就被后来的 push 顶掉了，只能重新 dispatch。现在构建和版本检查用不同的 concurrency group。

2. 容器里是 root。publish-repo 和 versions.yml 都在 `archlinux:base-devel` 容器里跑，而 makepkg 拒绝以 root 运行，`makepkg --printsrcinfo` 用不了。读 pkgname 只能 `source PKGBUILD`。

3. artifact 只留 3 天。构建产物只是用来中转的，Release 才是长期存储，旧版本的包会从 Release 里清掉。
