# AGENTS.md 模板与写法

AGENTS.md 是仓库级统一入口，放在仓库根目录。全文控制在 **150 行左右**；它是索引和规则，不是知识正文——细节全部下沉到 `agent-doc/` 主题文档。本文件给出逐节写法与可直接套用的骨架。

## 目录

- [开场](#开场)
- [项目简介与目标](#项目简介与目标)
- [Project Structure 与 Module Organization](#project-structure-与-module-organization)
- [Architecture Overview](#architecture-overview)
- [Where to Look（核心资产）](#where-to-look核心资产)
- [Build, Test, and Development Commands](#build-test-and-development-commands)
- [Long-Running Process Rules](#long-running-process-rules)
- [Agent Temporary Files（可选）](#agent-temporary-files可选)
- [Coding Style 与 Naming Conventions](#coding-style-与-naming-conventions)
- [Testing Guidelines](#testing-guidelines)
- [Commit 与 Pull Request Guidelines](#commit-与-pull-request-guidelines)
- [Security 与 Configuration Invariants](#security-与-configuration-invariants)
- [完整骨架](#完整骨架)

## 开场

第一段完成三件事：声明这是所有 AI agent 的统一入口、列出兼容工具、立下检索优先原则。

```markdown
# Repository Guidelines

本文件是所有 AI agent 的统一入口。**Compatible with**: Claude Code, opencode, OpenAI Codex, Gemini CLI。

> **IMPORTANT**: 优先「检索式」推理，而非「预训练记忆」式推理。项目约定请从 `agent-doc/` 检索阅读，不要凭通用知识臆测本仓库的结构与规则。
```

要点：

- 检索优先声明用引用块突出，这是整个文档体系成立的根基。
- 兼容工具列表按仓库实际支持的写，不确定就只写 AGENTS.md 标准。

## 项目简介与目标

一段话讲清项目是什么，再用 3-6 条 bullet 写目标与边界。目标里要包含「不做什么」（例如「无广告和不相关的社交元素」），这是 agent 判断需求合理性的依据。

## Project Structure 与 Module Organization

目录树 2-3 层，每个顶层条目行内注释一句话职责；树下再对每个模块补 1-2 句说明。monorepo 按包划分；单应用按顶层目录划分。只写稳定层级，不深入到易变的文件级。

## Architecture Overview

一段文字 + 一个极简数据流（箭头链即可），让 agent 30 秒建立心智模型。细节链接到 `agent-doc/architecture.md`，本节不展开。典型句式：

```markdown
**数据流**: `用户输入 → 解析层 → 服务层 → 存储`
架构细节参见 **[agent-doc/architecture.md](agent-doc/architecture.md)**。
```

## Where to Look（核心资产）

agent 导航的唯一入口，直接决定「是否还要扫仓库」。表格模板：

```markdown
## Where to Look

| 你想了解…… | 去看…… |
| --- | --- |
| 整体架构、数据流 | [agent-doc/architecture.md](agent-doc/architecture.md) |
| 存储层、表结构 | [agent-doc/data-layer.md](agent-doc/data-layer.md) |
| 验证命令、既有失败 | [agent-doc/verification.md](agent-doc/verification.md) |
| <按主题逐行补全> | <agent-doc/xxx.md> |
```

规则：

- 左列用「任务动词」而非「文档名」（写「查页面路由」，不写「routes 文档」）。
- 覆盖 `agent-doc/` 下每一篇文档；仓库内其他高质量 README（子包 README）也收入。
- monorepo 额外加一张「用户提到…… → 子项目」映射表（App/客户端 → `apps/mobile`、服务端 → `apps/server`）。
- 行数随文档增长时优先合并同类项，而不是无限加行。

## Build, Test, and Development Commands

- 写实际验证过可跑的命令，按「根级 → 子包」分组，每条一句话注释。
- 平台前置要求（JDK 版本、包管理器、系统依赖）单独列在最前面，写清「缺了会怎样」与自查命令（如 `java -version`）。
- 不确定命令是否可跑时，先跑一遍再写。

## Long-Running Process Rules

列出所有不会自行退出的命令（dev server、watch mode、`tail -f`）并给出强制处理方式：

```markdown
开发服务器和任何不会自行退出的命令，**禁止直接裸跑**。必须使用以下任一方式处理：
1. 后台运行 + 验证就绪 + kill
2. `timeout` 命令包裹
3. 调用工具时设置超时参数

**判断标准**：命令在正常情况下不会自行退出，就属于「长期运行进程」。构建、lint 等会正常结束的命令不受此限制。
```

## Agent Temporary Files（可选）

若仓库需要约定 agent 临时产物（截图、日志、pid 文件）的落点，写明固定目录（如仓库根 `.temp/`）与理由（便于检视清理、避免反复申请仓库外权限）。

## Coding Style 与 Naming Conventions

从 lint / format 配置和既有代码中提取。只写配置文件表达不了的约定（文件命名模式、导入别名、平台后缀约定如 `.web.ts`）；能被 Prettier / ESLint 自动表达的写一句「见配置文件」即可。

## Testing Guidelines

写当前真实状态（包括「没有强制 CI 测试」这种事实）和对新代码的期望。深入的验收矩阵放 `agent-doc/verification.md`。

## Commit 与 Pull Request Guidelines

从 `git log` 提取既有风格（Conventional Commits 或简短祈使句），不要发明仓库没有的规范。写提交前必须运行的检查。

## Security 与 Configuration Invariants

安全红线用 bullet 列表写死，每条是可判定的断言：

- 哪些文件是 git-ignore 的凭证，绝不提交。
- 外部输入是否可信、在哪个边界校验。
- 密钥如何注入（环境变量 / 平台配置），错误输出是否脱敏。

## 完整骨架

```markdown
# Repository Guidelines

本文件是所有 AI agent 的统一入口。**Compatible with**: <工具列表>。

> **IMPORTANT**: 优先「检索式」推理，而非「预训练记忆」式推理。项目约定请从 `agent-doc/` 检索阅读，不要凭通用知识臆测本仓库的结构与规则。

<一段项目简介>

## Project Goals

- <做什么 1>
- <做什么 2>
- <不做什么>

## Project Structure & Module Organization

<目录树 2-3 层，行内注释职责>
<每个模块 1-2 句补充>

## Architecture Overview

**数据流**: <极简箭头链>
架构细节参见 **[agent-doc/architecture.md](agent-doc/architecture.md)**。

## Where to Look

| 你想了解…… | 去看…… |
| --- | --- |
| <任务> | <agent-doc/xxx.md> |

## Build, Test, and Development Commands

<平台前置要求>
<分组命令 + 一句话注释>

## Long-Running Process Rules

<长期进程清单 + 三种处理方式>

## Coding Style & Naming Conventions

<配置外的命名与别名约定>

## Testing Guidelines

<真实状态 + 新代码期望>

## Commit & Pull Request Guidelines

<从 git log 提取的风格 + 提交前检查>

## Security & Configuration Tips

<红线 bullet 列表>
```
