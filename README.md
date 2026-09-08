# tcdw 自用 Skills

这是 tcdw 用于集中管理自用 Agent Skills 的仓库。

仓库地址计划为 `https://github.com/tcdw/skills`。

The repository is intentionally structured around the portable `skills/<skill-name>/SKILL.md` layout used by Claude Code, Cursor, Codex, opencode, and other agents that support the Agent Skills convention.

## Layout

```text
skills/
  omp-add-provider/
    SKILL.md
docs/
  authoring.md
```

Each skill lives in its own directory and must include a `SKILL.md` file with frontmatter:

```markdown
---
name: omp-add-provider
description: Use when the user wants to add or configure a model provider.
---
```

## Install

Repository URL: `https://github.com/tcdw/skills`

### opencode

opencode can load this repository directly from a configured skills path after cloning:

```sh
git clone https://github.com/tcdw/skills.git ~/skills
```

Then add the path to `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["~/skills/skills"]
  }
}
```

Restart opencode after changing config.

### Claude Code

```sh
mkdir -p ~/.claude/skills
curl -sL https://github.com/tcdw/skills/archive/main.tar.gz | tar xz -C ~/.claude/skills --strip-components=2 skills-main/skills
```

Or from a local clone:

```sh
cp -R skills/* ~/.claude/skills/
```

### Codex And Other Agent Skills Directories

```sh
mkdir -p ~/.agents/skills
cp -R skills/* ~/.agents/skills/
```

For project-level installation, copy `skills/*` into the agent's project skill directory, such as `.agents/skills`, `.claude/skills`, `.cursor/skills`, or `.github/skills`.

## Authoring

See `docs/authoring.md` for the local conventions used when adding or editing skills.

## Available Skills

| Skill | 一句话介绍 |
| --- | --- |
| `atlassian-cli` | 通过 `acli` 命令行查看、搜索、更新 Jira issue 和 Confluence 页面。 |
| `comment-why-not-what` | 注释纪律：只写解释 Why 的注释、禁止复述 What/How，写注释或 review 注释时使用。 |
| `just-do-it` | 把任务执行到底而不是停在分析阶段，用于「帮我升级依赖 / 重构 / 修复」等有明确交付预期的任务。 |
| `omp-add-provider` | 为 oh-my-pi (omp) 配置第三方模型提供商，包括 OpenAI 兼容中转、Anthropic 代理、双 key 网关等。 |
| `review-renovate-mr` | 以资深前端工程师视角审查 Renovate 生成的 `feature/renovate-*` 依赖升级 MR。 |
| `mobile-validation` | 在 React Native 项目的真实设备或模拟器上运行并验证当前改动。 |
| `web-design-taste` | tcdw 的个人视觉设计语言（语义色别名、圆润无衬线、克制用色、暗色一等公民），做界面或 review 设计稿时使用。 |
