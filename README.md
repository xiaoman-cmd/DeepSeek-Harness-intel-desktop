# DeepSeek Harness — Intel (x86_64) macOS 桌面端构建仓库

> Unofficial, self-built Intel-mac DMG of the DeepSeek Harness desktop app.

本仓库提供在 **Intel Mac（x86_64）** 上构建的
[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
桌面端（Electron）**未签名** DMG 产物，以及完整的本机构建过程记录，方便同架构用户直接下载使用或自行复现。

## 下载

| 文件 | 架构 | 大小 | 说明 |
| --- | --- | --- | --- |
| `DeepSeek Harness-0.2.1-rc.2-x64.dmg` | x86_64 (Intel) | ~394 MB | Git LFS 存储，未签名 / 未公证 |

**SHA-256：** `496670a570be1139da4d13760bd979ed97a36d2dee800a4492dfd65e2bafa50b`

## 使用方法

1. 下载 DMG（Git LFS 文件：克隆后需 `git lfs pull`，或直接在仓库页面下载）。
2. 双击挂载，把 `DeepSeek Harness.app` 拖到「应用程序」。
3. 首次打开需清除隔离属性（从网络下载的 app 带 quarantine 标记，Gatekeeper 会拦截未签名应用）：
   ```bash
   xattr -cr /Applications/DeepSeek\ Harness.app
   ```
4. 双击启动。系统会提示「无法验证开发者」——这是未签名应用的正常提示，确认 / 右键打开即可运行。

## ⚠️ 重要声明

- **非官方构建**：本仓库与 deepseek-ai 官方无关。官方未提供 Intel 版桌面客户端，此产物由用户在本地（Intel Mac, macOS 13.1, Xcode CLT clang 11.0.3）自行构建。
- **未签名 / 未公证**：应用仅做 ad-hoc 签名（`codesign -dvv` 显示 `Signature=adhoc`），**没有** Apple 开发者证书，也**未经过** Apple 公证（notarization）。Gatekeeper 的「无法验证开发者」提示属预期行为。
- **风险自负**：二进制未经第三方审计与签名验证。请核对上方的 SHA-256 后再使用，仅建议用于个人研究 / 自用。因使用本产物导致的任何问题，作者不承担责任。
- **源码归属**：应用源码版权归 deepseek-ai 所有，遵循其上游 LICENSE（Apache-2.0）。本仓库仅包含构建脚本、补丁、日志与构建产物，不含上游源码的完整副本。
- **适用范围**：仅适用于 **Intel (x86_64) Mac**，macOS 10.15+。Apple Silicon (arm64) Mac 请使用官方 / 其他构建。

## 来源与版本

- 上游仓库：`deepseek-ai/deepseek-harness`
- 构建基于 commit：`687f282e8625c6b8d11ff58211a90524be2e4317`
  （merge of `release-dsh-0.2.1-rc.2`，2026-10-17）
- 桌面端版本：`0.2.1-rc.2`
- Electron：`44.7.0`

## 仓库结构

```
.
├── DeepSeek Harness-0.2.1-rc.2-x64.dmg   # 产物（Git LFS）
├── README.md                             # 本文件
├── BUILD.md                              # 完整构建过程与踩坑记录
├── buildtools/                           # 本机构建辅助脚本
│   ├── bootstrap.cjs                     # 给 Node 全局 fetch 注入代理（绕过下载失败）
│   ├── seed_cache.py                     # 预种 primary-runtime 缓存（sha256 命名）
│   ├── seed_electron.py                  # 预种 Electron 到 @electron/get 缓存
│   └── download-toolchain.sh            # 用 npmmirror 一键下载工具链（electron + dmgbuild）
├── patches/
│   └── source-build-patches.patch        # 对上游源码的 6 处修改（适配旧 clang / 离线构建）
└── logs/                                 # 各次构建的原始日志（build*.log）
```

## 自行复现构建

详见 [BUILD.md](./BUILD.md)。核心步骤：克隆上游 → 应用 `patches/source-build-patches.patch` → `CI=true pnpm install` → 用 `buildtools/` 预种缓存 → `pnpm package:desktop:mac:x64:unsigned`。

## English

This is an **unofficial** build of the DeepSeek Harness desktop app for **Intel (x86_64) Macs**,
produced locally because the upstream project does not ship an Intel client. The DMG is **unsigned
and un-notarized** (ad-hoc signature only) — Gatekeeper will warn "unidentified developer", which is
expected; clear the quarantine with `xattr -cr` and open anyway. Use at your own risk. Source code
belongs to deepseek-ai under its upstream LICENSE. SHA-256 of the DMG is listed above.
