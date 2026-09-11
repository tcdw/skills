---
name: create-agent-docs
description: "Create and maintain Coding-Agent-friendly documentation for any repository: a root AGENTS.md entry point plus an agent-doc/ directory of task-indexed topic docs (architecture, data layer, verification, operations, glossary, and more), so each agent session reads only the docs a task needs instead of scanning the whole repo. Use when asked to bootstrap or generate agent-facing project docs, create or restructure AGENTS.md or agent-doc/, onboard an agent to a codebase, or refresh stale agent docs after architecture, command, or workflow changes. 适用于为项目创建 AGENTS.md、agent-doc 或面向 Coding Agent 的文档体系，或在架构、命令、工作流变化后更新这些文档。"
---

# Create Agent Docs

为仓库建立「检索式」agent 文档体系：根 `AGENTS.md`（统一入口）+ `agent-doc/`（按主题拆分的知识文档）。目标：agent 每次创建 session 只按任务读取相关文档，不再扫描整个仓库。

产出布局：

```text
repo/
├── AGENTS.md              # 统一入口：简介、结构、命令、Where to Look 索引（约 150 行内）
└── agent-doc/
    ├── README.md          # 使用方式 + 快速入口表 + 文档边界
    ├── architecture.md    # 进程 / 模块 / 数据流 / 信任边界
    ├── verification.md    # 本仓库特有的验证手段
    ├── <主题>.md          # 按项目性质选配（data-layer / configuration / operations / …）
    └── design/            # 可选：设计原文，只归档不改写
```

`AGENTS.md` 是 Claude Code、OpenAI Codex、Gemini CLI、opencode 等工具共同读取的仓库级入口，保持工具中立，不写任何单一工具的专有指令。生成文档的语言跟随仓库主要文档语言（默认中文正文 + 英文技术词），用户另有要求时听用户的。

## 核心原则

1. **检索式推理**：AGENTS.md 开场即声明「优先从 agent-doc/ 检索阅读，不要凭通用知识猜测本仓库」。文档读者是 agent：短段落、表格、ASCII 图，不写面向人的营销话术。
2. **渐进披露**：入口 → Where to Look 索引 → 主题文档，三层。任何典型任务应在两跳内定位到答案。
3. **事实层级**：源码 / 迁移 / 配置 schema ＞ 测试 ＞ agent-doc 正文 ＞ design/ 原文。文档与源码冲突时，先核对源码，再修文档。
4. **防腐化**：不写易变事实（依赖版本号、行号、文件数量）。版本一律指向 `package.json` / lockfile 等真实来源；文档只记录「是什么、为什么、怎么验证」。
5. **双向同步**：行为或运维契约变化时，同步更新对应主题文档与索引，这是维护模式的唯一触发条件。

## 工作流

### 1. 调查仓库（只读，控制读取量）

按需读取，不要全仓库扫描：

- 根清单：README、包管理清单（`package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` 等）、lockfile、CI 配置、lint / format 配置、既有 `AGENTS.md` / `CLAUDE.md` / `.cursorrules`。
- 目录树：顶层 2-3 层，判断 monorepo / 单应用 / 库。
- 命令：scripts 段、Makefile / justfile、CI 中的实际调用方式。
- 入口源码：main / 组合根 / 路由表 / schema 定义，读关键文件即可。
- 测试布局：测试目录、运行命令、能看出的测试契约。
- 已有人类文档：判断「吸收进主题文档」还是「原样保留并引用」。

产出一张事实清单：模块与职责、命令与平台坑（JDK/SDK 版本要求等）、技术栈、特殊约束（长期进程、安全红线、agent 临时文件约定）。

### 2. 向用户确认

无法从仓库确定的行为约定集中问一次（有 AskUserQuestion 就用它）：提交规范、验证深度、部署方式、agent 临时文件位置等。宁问勿编；能跑只读命令验证的先验证再问。

### 3. 写 AGENTS.md

逐节模板与写法见 [references/agents-md.md](references/agents-md.md)。固定骨架：开场声明 → 项目简介与目标 → Project Structure → Architecture Overview（简版 + 链接）→ Where to Look → 命令 → Long-Running Process Rules → 编码风格 → 测试 → 提交 → 安全不变量。

### 4. 写 agent-doc/

选型表与每篇模板见 [references/topic-docs.md](references/topic-docs.md)：

- 必写：`README.md`、`architecture.md`、`verification.md`。
- 选配：`data-layer` / `configuration` / `operations` / `glossary` / 领域流程文档 / `design/` 等，按调查结果决定，宁缺毋滥。
- 单篇通常控制在 250 行内；表格优先于长段落；数据流用 ASCII 图。

### 5. 自检

- 模拟 3 个典型任务（定位 bug、加功能、跑验证），确认从 AGENTS.md 出发两跳内定位到答案。
- 运行本 skill 的 `scripts/check_links.py` 检查所有相对链接可达。
- 复查：无密钥、无精确依赖版本号、无易变数字；AGENTS.md 在 150 行左右。

## 维护模式（更新既有文档）

- 行为 / 命令 / 契约变化 → 更新对应主题文档，必要时同步索引。
- 新增文档 → `agent-doc/README.md` 快速入口与 AGENTS.md Where to Look 各补一行。
- 依赖升级、行号漂移 → 不改文档（文档本来就不记录这些）。
- 计划类文档（migration / plan）完成 → 归档或删除，结论吸收进主题文档。
- 拿不准文档是否过期 → 以源码为准核对，再修正文档。
