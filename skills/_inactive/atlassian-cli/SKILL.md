---
name: atlassian-cli
description: |
  USE THIS FIRST for Jira, Confluence, Atlassian Cloud, atlassian.net URLs,
  /browse/PROJECT-123 links, and Jira issue keys like DEV-19747.
  Do NOT use fetch, glab and other tools for Jira issue keys or atlassian.net URLs.
  Provides acli commands for viewing/searching/updating Jira workitems and Confluence pages.
---

# Atlassian CLI (acli)

Command-line access to Jira and Confluence Cloud. This skill covers conventions and gotchas — for exact flags, run `acli <product> <entity> <action> --help`.

## Authentication

Always check first; commands fail silently-ish without it.

```bash
acli auth status        # check
acli auth login         # if not authenticated
```

## Command Structure

```
acli <product> <entity> <action> [flags]
```

The `--action` flag is **legacy and no longer works**. Use the positional form:

```bash
# ❌ acli jira --action getIssueList --jql "..."
# ✅ acli jira workitem search --jql "..."
```

## Quick Reference

### Jira

| Entity     | Common actions                                                       |
|------------|----------------------------------------------------------------------|
| `workitem` | search, create, create-bulk, edit, view, transition, assign, delete |
| `workitem comment` | create, list, update, delete                                |
| `project`  | list, view, create, update, delete, archive                          |
| `sprint`   | create, update, view, delete, list-workitems                         |
| `board`    | search, get, create, delete, list-sprints                            |

### Confluence

| Entity   | Common actions                                       |
|----------|------------------------------------------------------|
| `space`  | list, view, create, update, archive, restore         |

## Batch Operations

Prefer built-in batching over bash loops:

- `--jql "<query>"` — operate on every match
- `--filter <id>` — use a saved filter
- `--key KEY-1,KEY-2,...` — explicit list
- `--yes` / `-y` — skip confirmation
- `--ignore-errors` — keep going on failures

For bulk create: `acli jira workitem create-bulk` or `create --from-json file.json`. Generate a template with `--generate-json`.

## Output Flags (easy to get wrong)

| Want            | Use         | Not                  |
|-----------------|-------------|----------------------|
| CSV             | `--csv`     | `--outputFormat 999` |
| JSON            | `--json`    |                      |
| Pick columns    | `--fields`  | `--columns`          |
| Count only      | `--count`   |                      |
| All pages       | `--paginate`|                      |
| Open in browser | `--web`     |                      |

## When in doubt

```bash
acli jira workitem --help
acli jira workitem search --help
```

Don't guess command or flag names — `--help` is authoritative.
