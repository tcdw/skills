# Skill Authoring Guide

## Directory Convention

Use one folder per skill:

```text
skills/<skill-name>/SKILL.md
```

The folder name and frontmatter `name` should match exactly.

## Frontmatter

Every skill should start with:

```markdown
---
name: lowercase-hyphen-name
description: Use when the user asks for specific trigger words or workflows.
---
```

Keep descriptions concrete and trigger-oriented. Mention the filenames, tools, domains, or workflows that should activate the skill.

Use `Use ONLY when...` when the skill should avoid adjacent tasks.

## Body Structure

Prefer this order:

```markdown
# Skill Name

## When To Use

## Workflow

## Rules

## Examples
```

Keep skills operational. They should tell the agent what to do, what to avoid, and what evidence to collect.

## Compatibility

Favor portable instructions and avoid depending on one specific agent unless the skill is agent-specific.

Good portable assumptions:

- The skill is loaded from a `SKILL.md` file.
- The agent can read files and run commands.
- The agent may have a different working directory from the skill repository.

Avoid hardcoding local absolute paths unless the skill is explicitly personal and local-only.

## Maintenance Checklist

Before committing a skill:

- Confirm `skills/<name>/SKILL.md` exists.
- Confirm frontmatter `name` matches `<name>`.
- Confirm the `description` says when to use the skill.
- Remove secrets, local tokens, and machine-specific temporary paths.
- Update `README.md` if the skill should be listed as production-ready.
