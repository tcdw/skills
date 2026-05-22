---
name: comment-why-not-what
description: Code-commenting discipline that forbids restating What/How and only allows Why-comments (workarounds, hidden constraints, intentional "looks like a bug", performance/safety reasoning, irreversible side-effect boundaries). Use whenever writing, adding, or editing inline code comments / JSDoc / TODO markers in any language. Also use during code review when judging whether a comment should exist at all.
---

# Comment Why, Not What

> Comments only answer **Why**. Code answers **What** and **How**. If naming or structure can express it, do not comment.

## Why this rule exists

Comments are **patches, not documentation** — they exist to cover what code itself cannot express.

If a piece of code can be made understandable through renaming, extracting a function, or restructuring, do not write a comment. Comments are the last fallback, not the first choice. Code changes; comments do not follow. The more comments you write, the higher the probability they rot.

## When comments MUST be written

When a reader would stop and ask **"is this a bug?"** or **"why isn't this simpler?"**, you must answer them on that exact line:

- **Counter-intuitive workarounds / hacks** — code that reads like "is this a bug?"
- **Hidden external constraints** — BE / upstream / historical reasons forcing a non-obvious shape
- **Intentional "looks like a bug"** — `eslint-disable`, deliberately omitted `useEffect` deps, etc.
- **Performance / safety considerations** — the shape looks suboptimal but is chosen for a reason
- **Irreversible side-effect boundaries** — `dropTable`, `forcePush`, destructive migrations, etc.

## When comments MUST NOT be written

- **Restating code semantics** (`counter += 1` does **not** need `// increment by 1`)
- **Repeating the function signature** (TS already wrote it; JSDoc must not copy it again)
- **Referencing the current task / PR / issue** (belongs in commit message / PR description / git blame)
- **Ownerless, trigger-less `TODO` / `FIXME`** (an ownerless TODO = zero TODOs)
- **Explaining history** (`// used to be lodash, switched to native` — `git log` is the truth of history)
- **JSDoc duplicating TS types** (only add semantics types cannot express: unit, range constraint, call-site constraint)

## Writing rules

- Write **Why**, never **What**
- Write the **question the reader would ask**, not the thing the author wants to say. For every comment, self-check: *what would the reader ask seeing this? am I answering it?*
- The comment should be **shorter than the code** it annotates. If the comment is longer, the code needs refactoring.
- Do not write "obviously", "simply", "trivial" — these words presume the reader's level.
- Avoid future-tense promises. *"Temporary `setTimeout`, will switch to RAF later"* — "temporary" living in the codebase for ten years is the norm.

## Division of labor with other channels

Comments only carry the **Why** slot, which is actually small:

| Information type           | Where it lives                          |
| -------------------------- | --------------------------------------- |
| What (what it does)        | The code itself (naming, structure)     |
| Why (why this way)         | Comments                                |
| History of changes         | `git log` / PR description              |
| Design decision reasoning  | spec / RFC                              |
| Team conventions           | `AGENTS.md` / `CLAUDE.md` / lint rules  |
| Temporary tasks            | Issue tracker / `TODO` with owner       |
| Current task context       | Commit message                          |

## Marker conventions

Only the following semantically clear markers are allowed:

- `HACK:` — counter-intuitive but necessary workaround
- `SAFETY:` — explains why unsafe code is safe **in this context**
- `PERF:` — explains the performance reason behind a non-intuitive shape
- `TODO(owner, trigger):` — must have an **owner** and a **trigger condition**

Forbidden because their semantics are vague: `XXX`, `FIXME`, `NOTE`.

## Minimum memorable version

1. Comments answer **Why**, not **What**.
2. If you can't write a **Why**, don't write a comment — refactor the code.
3. Don't reference task numbers, don't write history, don't write future plans.

## Agent behavior checklist

Before emitting any comment, the agent must run through:

1. Does this comment answer a **Why** the reader would actually ask? If no → delete it.
2. Could renaming a variable / extracting a function / reshaping the code remove the need for this comment? If yes → refactor instead.
3. Does this comment restate the code, the signature, the task number, or the history? If yes → delete it.
4. If it is a `TODO`, does it carry an **owner** and a **trigger condition**? If no → either complete it or delete it.
5. Is the comment longer than the code it annotates? If yes → either tighten the comment or refactor the code.

Apply the same checklist when reviewing existing comments in a diff. Recommend deletion or rewriting for any comment that fails the checklist.
