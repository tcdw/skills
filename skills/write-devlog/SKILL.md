---
name: write-devlog
description: 为任意代码仓库编写开发日志（devlog）：记录一次功能或改动的背景、主要变更、验证结果与提交 hash，并按“先提交代码、再提交日志”的两次提交流程落盘。用户要求“写 devlog”“写开发日志”“记录这次改动”“把这个功能写成 devlog”“write a devlog / development log for this change”时使用。不用于 CHANGELOG、release notes、用户指南或描述当前行为的架构/主题文档。
---

# Write Devlog

为一次已完成的改动写开发日志。devlog 反映写作当时的代码状态，写完即是历史记录，之后不再回改。

## When To Use

- 一项功能、重构、升级或修复做完后，用户要求留档。
- 用户要求补写某次历史提交的 devlog。

不适用：面向用户的变更说明（CHANGELOG / release notes）、使用指南、描述当前行为的主题文档。

## Workflow

### 1. 确定位置与项目约定

1. 读入口文档（`AGENTS.md`、`CLAUDE.md`、`agent-doc/README.md` 等），找 devlog 目录和相关规则。有的仓库把 devlog 标为默认不读取的历史目录：写新日志时可以读已有文件参考格式，但不要从中推断当前行为。
2. 按优先级选目录：入口文档指定的位置 → 已存在的 `agent-doc/devlogs/` → 其他已存在的 `devlogs/` 目录（`find . -type d -name devlogs -not -path '*/node_modules/*'`）→ 都没有时新建 `agent-doc/devlogs/`。
3. 读最近 1–2 篇已有 devlog，沿用其标题前缀、语言、章节和代码块风格。已有风格与下方模板冲突时，以已有风格为准。
4. 找验证命令的来源：`agent-doc/verification.md`、`AGENTS.md`、`package.json` scripts、`Makefile` 等。

### 2. 确保代码已提交

devlog 要引用代码的 commit hash。代码和文档必须分两次提交，否则“文档写入 hash → 提交文档又产生新 hash”会陷入死循环。

- 代码改动尚未提交：按项目提交规范先提交代码；用户没授权提交时先询问。
- 改动跨多个提交：全部列进「提交」一节。
- 用 `git log --oneline` 取实际 hash，用 `git show --stat <hash>` 或 `git diff <base>..<hash>` 取实际改动。

### 3. 收集事实

- **背景**：从对话、issue、commit message 和改动前的代码里找动机、原状态和关键约束。
- **变更**：代码片段和 `path:line` 引用只能取自真实的 diff 或文件。可以删减（用 `// ...` 标出省略处），不能改写或编造。
- **验证**：只写本次实际跑过的命令和真实结果（退出码、通过数、关键输出）。还没验证时先跑项目的验证命令；跑不了的写明“未运行”及原因。

### 4. 写文件

文件名：`YYYYMMDD-<kebab-topic>.md`。日期取代码提交日期（`git log -1 --format=%cd --date=format:%Y%m%d <hash>`），topic 用简短的英文 kebab-case。

````markdown
# <Project> - YYYYMMDD <标题>

## 背景

为什么要做这个改动：要解决的问题、改动前的状态、关键约束。

## 主要变更

### 1. <小标题>

做了什么、为什么这样做。附代码片段（标注语言，如 ```ts）或文件引用：`src/config.ts:42`

### 2. <小标题>

...

## 验证

```bash
<实际运行的命令>
# <实际结果>
```

## 提交

```txt
<commit-hash> <commit message>
```
````

### 5. 提交文档

单独提交这篇 devlog，沿用项目的提交风格；没有明确风格时用 `docs: add <topic> devlog`。只 stage 这篇 devlog，不要带上其他未提交的改动。

## Rules

- 不回改旧 devlog，新情况写新文件。
- 语言跟随已有 devlog；没有已有文件时用中文。
- 标题前缀用项目名，取自已有 devlog、README 标题或包名。
- 文件路径一律写仓库相对路径。
- 篇幅与改动规模匹配，小改动可以只有一个变更小节。
- 不写入 secret、token、本地私有配置值；验证输出里的 API key、Authorization 头要打码或删掉。

## Examples

文件名：

- `20260517-image-generation.md`
- `20260601-expo-sdk-56-upgrade.md`

标题：

- `# AI Gateway - 20260603 极简重写：从功能丰富到前缀路由`
- `# Bilisound - 20260702 看板娘直接拖拽与缩放编辑`
