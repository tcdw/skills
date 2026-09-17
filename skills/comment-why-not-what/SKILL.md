---
name: comment-why-not-what
description: On-demand code-comment review and cleanup. Audits inline comments, JSDoc/docstrings, and TODO markers against a "comments explain Why, code explains What" rubric, then reports keep/rewrite/delete/refactor verdicts or applies comment-only fixes. Use ONLY when the user explicitly asks to review, audit, lint, clean up, prune, or tidy comments (e.g. "review the comments in this diff", "clean up comments in src/foo", "注释 review", "清理注释", "删掉废话注释"). Do NOT use for general code review, for writing new code, or for generating API documentation.
---

# Comment Why, Not What

A focused pass over code comments. Two modes:

- **Review** — report findings with verdicts; do not edit files.
- **Cleanup** — apply the verdicts as comment-only edits, then verify nothing else changed.

Pick the mode from the request. "review / audit / check / 看看" → Review. "clean up / prune / fix / 清理 / 删掉" → Cleanup. If unclear, run Review and offer Cleanup at the end.

## Workflow

### 1. Fix the scope

Resolve in this order and state the scope in the output:

1. Paths, files, or a PR/branch the user named.
2. Otherwise the current change: `git diff` + `git diff --staged` (and untracked files if relevant). In a diff, judge **added or modified comments**; mention pre-existing ones in touched hunks only when clearly harmful.
3. Whole-repo sweeps only when asked. Then sample by directory and cap the report; say what was not covered.

Skip vendored code, generated files, lockfiles, build output, and fixtures that assert on comment text.

### 2. Read the repo's conventions first

Check `AGENTS.md` / `CLAUDE.md` / `CONTRIBUTING`, lint config, and a few existing files. Repo rules win over this skill — e.g. if the repo mandates JSDoc on every export, or uses `NOTE:` as a convention, do not flag those.

### 3. Collect comments

Use the diff, or search by language comment syntax (`//`, `/* */`, `#`, `--`, `"""`, `<!-- -->`). Read each comment **together with the code it annotates** — a verdict made from the comment alone is not valid.

### 4. Classify each comment

Assign exactly one verdict:

| Verdict      | When                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| **Keep**     | Answers a Why the reader would actually ask (see "Must keep").                                          |
| **Rewrite**  | Has a real Why buried in What, is longer than needed, or uses a vague marker. Provide the new text.     |
| **Delete**   | Restates code/signature, narrates history, references the task/PR, or is an ownerless TODO.             |
| **Refactor** | Exists only because a name or structure is unclear. Propose the rename/extraction that removes it.      |
| **Move**     | Real information in the wrong channel (history → commit message, plan → issue, convention → lint/AGENTS.md). |
| **Ask**      | Cannot tell whether the Why is still true (possible stale workaround, unknown external constraint).     |

Commented-out code is its own finding: recommend deletion (git keeps it) unless a Why explains why it must stay visible.

### 5. Report (Review mode)

Group by file, most harmful first (misleading/stale > noise). Per finding:

```text
path/to/file.ts:42  Delete
  // increment retry counter
  Reason: restates `retries += 1`.

path/to/file.ts:88  Rewrite
  - // wait 50ms
  + // HACK: Safari fires `resize` before layout settles; 50ms avoids reading stale width.
  Reason: the delay is the non-obvious part; the comment said what, not why.
```

Close with counts per verdict, the scope covered, and any **Ask** items as explicit questions. For large scopes, list the top findings and summarize the rest by pattern rather than dumping every line.

### 6. Apply (Cleanup mode)

- Edit **comments only**. **Refactor** verdicts change code, so apply them only when the user authorized refactoring; otherwise leave the comment and list the proposal.
- Never invent a Why. If the reason is unknown, mark it **Ask** and leave the comment untouched rather than guessing.
- Leave **Ask** and **Move** items in place; list them for the user (draft the commit/issue text for Move if useful).
- Preserve formatting: remove the now-empty comment lines without leaving stray blank lines or breaking indentation.
- Verify:
  1. Read the final diff; every hunk must be comment-only (or an authorized refactor).
  2. Run `git diff --check` and the repo's formatter/linter on touched files.
  3. If any directive-adjacent line or doc-generation comment changed, run the type check / relevant tests.
- Summarize: counts per verdict applied, items left for the user, and checks run vs. not run. Do not commit unless asked.

## Rubric

### Must keep (or add when the user asks)

A reader would stop and ask **"is this a bug?"** or **"why isn't this simpler?"**:

- Counter-intuitive workarounds / hacks
- Hidden external constraints (backend, upstream bug, spec quirk, platform limit)
- Intentional "looks like a bug" (deliberately omitted deps, swallowed error, odd ordering)
- Performance or safety reasoning behind a non-obvious shape
- Irreversible side-effect boundaries (destructive migrations, force pushes, deletes)
- Semantics types cannot express: units, ranges, call-order or threading constraints

### Delete or rewrite

- Restating code semantics (`counter += 1  // increment`)
- Repeating the signature; JSDoc/docstrings that only mirror parameter types
- Task / PR / issue / ticket references as explanation (belongs in commit message or blame)
- History (`// used to use lodash`) — `git log` is the source of truth
- Ownerless, trigger-less `TODO` / `FIXME`
- Future promises (`// temporary, will switch to RAF later`)
- Presumptive words: "obviously", "simply", "just", "trivial"
- A comment longer than the code it annotates → tighten it or refactor the code

### Markers

Preferred: `HACK:`, `SAFETY:`, `PERF:`, `TODO(owner, trigger):`. Flag `XXX`, `FIXME`, bare `NOTE` as **Rewrite** — unless the repo's own convention uses them. Do not mass-rename markers during Cleanup unless asked.

## Never touch

These look like comments but are not prose. Do not delete or reword them, even if they "restate" something:

- Tool directives: `eslint-disable*`, `@ts-expect-error`, `@ts-ignore`, `biome-ignore`, `prettier-ignore`, `istanbul ignore`, `c8 ignore`, `# noqa`, `# type: ignore`, `# pragma`, `// nolint`, `#[allow]`-style pragmas, `rubocop:disable`
- Build/compiler directives: `//go:build`, `//go:generate`, `// +build`, `/// <reference>`, `#region`, `@jsx` pragmas, magic comments like `# frozen_string_literal`, `-*- coding -*-`
- Shebangs, license/copyright headers, SPDX lines
- Doc comments that feed generated public API docs (TypeDoc, rustdoc, godoc on exported symbols, Sphinx) — tighten them if they only mirror types, but do not remove the doc surface
- Comments asserted by tests, snapshots, or codegen markers (`// @generated`, `<!-- BEGIN ... -->`)

A directive may still lack a reason — e.g. `eslint-disable-next-line` with no Why. Suggest appending one (`-- reason`), but keep the directive.

## Self-check scenarios

- "Review the comments in my diff" → Review mode on the diff; no edits.
- "清理 src/utils 的注释" → Cleanup on that path; comment-only edits; Refactor proposals listed, not applied.
- `// @ts-expect-error` with no explanation → keep the directive, suggest adding a reason.
- `// wait for animation` above `setTimeout(fn, 300)` with no known cause → **Ask**, do not fabricate a Why.
- Repo `AGENTS.md` requires JSDoc on every export → do not flag those JSDoc blocks as signature duplicates; only flag type-mirroring content inside them.
- User asks for a general code review → this skill does not apply.
