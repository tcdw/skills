---
name: t3-delegate-review
description: 通过 T3 Code 把一个编码需求派给另一个 coding agent（默认 Pi，也可指定 Codex、Claude、Devin、OpenCode 等，以及具体模型）在独立 worktree 里实现，然后用 ocr（open-code-review）审阅它的改动、逐条核实、打回同一线程修正，主会话独立复验后按仓库规则提交、写 devlog、开 PR。用户说「派给 Pi / Codex 做」「让别的 agent 实现然后 review」「用 t3 调度子 agent」「委派这个需求」「delegate this to pi」，或者想让另一个 agent 动手、自己只把关时，都用这个 skill；即使用户只说了「派个任务试试」也用它。
---

# T3 委派：子 agent 实现 → ocr 审阅 → 打回修正 → 复验交付

主会话只把关，不动手写功能代码。子 agent 看不到当前对话，它的自测结果也不能直接采信，所以质量靠三件事保证：一份自包含的任务说明、核实过的 review 意见，以及主会话亲自重跑的验证。

## 参数

用户可以在请求里指定这两项，没指定就用默认值：

- **agent**：对应 T3 的 provider。用 `mcp__t3__orchestrator_capabilities` 列出 provider，按 `providerInstanceId`、`driverKind` 或 `displayName` 不分大小写匹配用户说的名字（例如 pi→`pi`，codex→`codex`，claude→`claudeAgent`，devin→`acpRegistry_devin`，dimcode→`acpRegistry_dimcode`）。默认用 `pi`。默认的那个缺失、被禁用或 `canRunChildTask` 为 false 时，按 `codex` → `claudeAgent` → 其他任意 `canRunChildTask: true` 的顺序换一个，并告诉用户换成了谁、为什么。用户**明确指定**的 agent 不可用时不要自己换，停下来问。
- **model**：
  - 用户指定了：用 `orchestrator_capabilities` 加 `search=<名字>` 在该 provider 下找到准确的 catalog id。匹配到多个时选和用户说法最接近的，拿不准就问。
  - 没指定：运行 `python3 -I <本 skill 目录>/scripts/default_model.py <agent> --cwd <工作区>`，取这个 agent 自己配置的默认模型和推理强度（Codex 的 `model_reasoning_effort` 会映射成 `reasoningEffort` 选项），然后用 `search` 在 catalog 里确认这个 id 存在。Pi 的 `providerID/model` 和 Codex 的模型名可以直接对上 catalog id；Claude 配置里可能是 `opus` 这样的别名，取 catalog 里该系列最新的 id。脚本拿不到时，用 catalog 里标了 `default` 的模型；还没有就问用户。
  - 每次都要现读配置，不要沿用上一次的值：用户随时会改 agent 的默认模型。

## 流程

### 1. 吃透任务，核实参照

先读用户点名的文件和要改的代码，弄清现状、目标和仓库规则（`AGENTS.md`、`CLAUDE.md` 等）。用户给的参照和描述对不上时（比如说某个文件「有分类导航」，打开却没有），在附近找到真正符合描述的参照，告诉用户你改用了哪个，然后继续，不要卡住等确认。

这一步要收集够写任务说明的材料：子 agent 只能看到你写进去的东西。

### 2. 准备工作区

仓库有自己的 worktree / feature 约定（`AGENTS.md`，或者 `surowan-dev-create-feature` 这类项目 skill）就照着做：从最新的远端主干开 worktree、装依赖，主 checkout 不动。没有约定时，在 `../<仓库目录名>.worktrees/feature/<名字>` 用 `git worktree add -b feature/<名字>` 从 fetch 后的远端主干建一个。把路径、分支和 base commit 告诉用户。

### 3. 选 agent 和模型

按上面「参数」一节解析。顺手用 `mcp__t3__t3_project_list` 找到 `workspaceRoot` 等于仓库主目录的 project，记下 `projectId`。

### 4. 派发

用 `mcp__t3__t3_thread_launch`：

- `projectId`：上一步找到的。
- `workspaceStrategy`：`{ "type": "existing_worktree", "worktreePath": "<worktree 绝对路径>" }`。
- `modelSelection`：`{ "provider": <driverKind>, "instanceId": <providerInstanceId>, "model": <catalog id> }`，有推理强度等选项时放进 `options`（取值必须在 catalog 列出的范围内）。
- `clientRequestId`：起一个稳定的 id，调用出错或丢了回复时用同一个 id 重试，避免开出两个线程。
- 除非用户要求，不传 `runtimeMode`。
- `message`：按 [references/templates.md](references/templates.md) 的「首次任务」模板写。

发出后把线程 `link` 告诉用户。

### 5. 等待

`mcp__t3__t3_thread_wait` 大约一分钟就会返回 `timedOut`，不管 `timeoutMs` 设多大，所以别靠循环调用它干等。用 Bash 后台跑 `sleep 300`（`run_in_background: true`），收到完成通知后再调用一次 `t3_thread_wait`（`timeoutMs` 设 50000 左右）看状态。还没完成就再睡一轮，并用一句话告诉用户进度。

完成后用 `mcp__t3__t3_thread_read`（`view: "messages"`，翻到最后几条）读它的最终报告。

### 6. 自己先读改动

在 worktree 里看 `git status --short` 和完整 diff，新建的未跟踪文件也要读。先自己理解改动，下一步才能判断 ocr 说得对不对。

### 7. ocr 审阅

加载 `open-code-review` skill，在 worktree 里后台运行：

```bash
ocr review --audience agent --output <scratchpad>/ocr-<名字>.txt -b "<业务背景>"
```

不带 `--commit` 时是 workspace 模式，已暂存、未暂存和未跟踪的改动都会审，所以子 agent 不提交正合适。`-b` 写清楚：功能是什么、照着什么参照做的、仓库有哪些硬规则、你最担心哪里出问题。结果用 Read 读全文，不要 `tail`。

### 8. 逐条核实

对每条意见回到代码里确认，判定为「成立」「误报」或「存疑」，并写一句理由。还要看问题是不是从参照实现里一起抄过来的：照样算成立，但要注明来源。`low` 级的吹毛求疵直接丢掉。

用表格向用户汇报：位置 | 问题 | 判定与理由。

### 9. 打回修正

没有其他指示时，把成立的问题用 `mcp__t3__t3_thread_send`（`mode: "auto"`）发回**同一个线程**，按模板的「修正轮」写。用户说要自己修或者让主会话修，就照用户说的做。

误报要放进「不要改」一节并写明理由，否则子 agent 会顺手把它也「修」了。要求新增的回归测试先在旧代码上失败、修完再通过，并在报告里说明确认过。

### 10. 独立复验

子 agent 说「全部通过」不算数。每轮修完都要：

1. 读新代码，确认修法对，没有引入新问题。
2. 在 worktree 里亲自重跑仓库要求的验证（lint、类型检查、构建、受影响的测试）。
3. 新增或改过的 e2e 用例用 `--repeat-each 5` 之类的方式多跑几轮，抓不稳定的用例。

失败了就发回同一个线程，附上事实：命令、失败的是哪个用例哪一轮、断言内容和产物路径。要求它先找出根因，确认是测试的竞态还是真 bug，不要放宽断言了事。修了三轮还没收敛就停下，把现状报告给用户。

改动面大的修正轮，可以再跑一次 ocr，只审新的 diff。

### 11. 交付

由主会话提交，不让子 agent 提交。仓库有交付约定就照做，例如 `surowan-dev-create-feature` 的「实现需求：做完即交付」：同步主题文档、带 attribution 提交、rebase、用 `write-devlog` 写 devlog、push、开 PR。仓库没有约定时，只在 feature 分支上提交，push 和开 PR 之前先问用户。无论哪种情况都不合并。

devlog 和 PR 里写清楚三件事：谁实现的（agent、模型、T3 线程）；review 意见各自怎么处理的；哪些验证是主会话亲自跑的，哪些只是子 agent 自报的。

### 12. 汇报

给用户：PR 链接（或分支）、提交列表、主会话亲自跑的验证结果、没执行的检查、review 意见的处理表、子线程 link，以及用的 agent 和模型。

## 容易踩的坑

- **子 agent 没有上下文**：路径一律写绝对路径；参照文件写明要看哪几个、看它们的什么；仓库规则里会影响这次改动的那几条要点名，不要只写一句「遵守 AGENTS.md」。
- **任务里不放 secret**：token、key、私有配置值都不要写进 `message`。
- **自报 ≠ 验证**：子 agent 报告里的「Pass」只能当线索，交付证据只认主会话自己跑出来的结果。
- **布局切换后的断言会抢跑**：改视口或切换布局后，要先等目标状态出现（元素 visible、旧元素 hidden），再测尺寸或溢出；一次性 `evaluate` 很容易测到中间态。
- **线程继承**：同一个子线程会保留之前几轮的上下文，修正轮直接引用上一轮就行；要彻底换思路时，`t3_thread_send` 可以传 `freshContext: true`。
