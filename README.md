# tcdw 自用 Skills

这是 tcdw 用于集中管理自用 Agent Skills 的仓库。

仓库地址计划为 `https://github.com/tcdw/skills`。

The repository is intentionally structured around the portable `skills/<skill-name>/SKILL.md` layout used by Claude Code, Cursor, Codex, opencode, and other agents that support the Agent Skills convention.

## Layout

```text
skills/
  example-skill/
    SKILL.md
docs/
  authoring.md
```

Each skill lives in its own directory and must include a `SKILL.md` file with frontmatter:

```markdown
---
name: example-skill
description: Use when the user needs a concrete example skill skeleton.
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

No production skills yet. Use `skills/example-skill` as a template, then remove it when real skills exist.
