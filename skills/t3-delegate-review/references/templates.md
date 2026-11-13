# 子 agent 消息模板

子 agent 对当前对话一无所知，模板里每一节都是它唯一的信息来源。用英文写效果最稳定；给最终用户看的文案要求（例如中文 locale）照原样写进去。按实际情况删掉用不上的小节。

## 首次任务

```markdown
# Task: <一句话目标>

You are working in the git worktree `<worktree 绝对路径>` (branch `<分支>`, based on `<base ref 与短 hash>`, dependencies already installed). Work ONLY inside this worktree; do not touch `<主 checkout 绝对路径>`. Do NOT commit, push or open a PR — leave the changes uncommitted; they will be code-reviewed afterwards.

Read `<AGENTS.md 等入口文档>` at the worktree root first and follow its coding style, testing and <相关子系统> rules.

## Goal

<现状：哪个文件/页面/模块，现在长什么样>
<目标：要变成什么样>

Reference (read these; they are the design spec):
- `<参照文件绝对路径>` — <看它的什么>

Behaviour to reproduce:
1. <可验证的行为 1>
2. <可验证的行为 2>

## Constraints

- <必须保留的现有机制，以及为什么>
- <只移植什么、不要移植什么>
- <仓库硬规则里与这次改动相关的几条，逐条点名>
- <文案 / i18n / 设计 token 要求>

## Verification (run all, from the worktree)

- <新增或要更新的测试：断言什么>
- `<命令 1>`, `<命令 2>`, ...

## Final report

Reply with: files changed (one line each, what and why), the exact verification commands you ran with pass/fail, anything you could not run, and any deviation from the reference and why.
```

## 修正轮（review 意见）

```markdown
# Review follow-up: fix <N> findings

A code review of your uncommitted changes in this worktree found the issues below (each verified against the code). Fix them in the same worktree. Still do NOT commit, push or open a PR.

## 1. <标题> — `<文件>` (~line <行号>)

<触发条件 → 错误结果，越具体越好>

Fix: <修正方向；如果有多种合理修法，说清约束，让它自己选>

## 2. ...

## Not to change

<被判为误报的意见>: <为什么现在这样是对的>. Leave it as is.

## Verification

Write the new regression tests so they fail on the current code before your fix, then pass after it; say in your report that you confirmed this.
Re-run from the worktree: `<命令>`, ...

Report: what you changed per finding, the exact commands with pass/fail, and whether the new tests failed before the fix.
```

## 修正轮（复验失败）

```markdown
# Follow-up: <失败现象，例如 flaky e2e test>

Independent re-verification found:

- `<命令>` → <结果，例如 41 passed, 1 failed>
- Failure: <断言原文与实际值>, at `<文件>:<行号>`
- <能定位到哪一轮、哪个参数组合的证据，例如最后写出的截图/产物>

Find the root cause first: is it the test racing <某个状态变化>, or a real bug in <被测对象>? Fix the actual cause; don't just loosen the assertion.

Do NOT commit, push or open a PR.

Verify: `<多轮重复命令，例如 --repeat-each 10>` must pass with zero failures, plus `<其余命令>`. Report the root cause you found, what you changed, and the command results.
```
