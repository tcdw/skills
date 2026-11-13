#!/usr/bin/env python3
"""Print the default model a coding agent is configured to use, as JSON.

Usage: python3 -I default_model.py <agent> [--cwd <workspace>]

<agent> is a T3 providerInstanceId or driverKind: opencode, codex, claudeAgent/claude.
Output: {"agent", "model", "options", "source", "note"}; "model" is null when unknown.
The model id is what the agent's own config says; confirm it against the T3 catalog
(orchestrator_capabilities with search=<model>) before launching.
"""

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


def result(agent, model=None, options=None, source=None, note=None):
    return {"agent": agent, "model": model, "options": options or {}, "source": source, "note": note}


def opencode(cwd):
    # `opencode debug config` lists every config document it merged (global, then project);
    # later documents override earlier ones, so the last top-level `model` wins.
    try:
        out = subprocess.run(
            ["opencode", "debug", "config"], cwd=cwd, capture_output=True, text=True, timeout=30, check=True
        ).stdout
        docs = json.loads(out)
        model, source = None, None
        for doc in docs if isinstance(docs, list) else []:
            value = (doc.get("info") or {}).get("model")
            if isinstance(value, dict) and value.get("providerID") and value.get("model"):
                model, source = f"{value['providerID']}/{value['model']}", doc.get("path")
            elif isinstance(value, str) and value:
                model, source = value, doc.get("path")
        if model:
            return result("opencode", model, source=source)
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    path = Path.home() / ".config/opencode/opencode.json"
    try:
        value = json.loads(path.read_text()).get("model")
        if isinstance(value, str) and value:
            return result("opencode", value, source=str(path), note="opencode CLI unavailable; global config only")
    except (OSError, ValueError):
        pass
    return result("opencode", note="no top-level model in OpenCode config")


def codex():
    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    path = home / "config.toml"
    try:
        config = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return result("codex", note=f"cannot read {path}")
    options = {}
    if config.get("model_reasoning_effort"):
        options["reasoningEffort"] = config["model_reasoning_effort"]
    return result("codex", config.get("model"), options, str(path))


def claude():
    if os.environ.get("ANTHROPIC_MODEL"):
        return result("claudeAgent", os.environ["ANTHROPIC_MODEL"], source="ANTHROPIC_MODEL")
    path = Path.home() / ".claude/settings.json"
    try:
        model = json.loads(path.read_text()).get("model")
    except (OSError, ValueError):
        model = None
    note = "may be an alias such as 'opus'; pick the newest matching id in the T3 catalog" if model else None
    return result("claudeAgent", model, source=str(path), note=note)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    agent = args[0].lower()
    cwd = args[args.index("--cwd") + 1] if "--cwd" in args else os.getcwd()
    if agent == "opencode":
        out = opencode(cwd)
    elif agent == "codex":
        out = codex()
    elif agent in ("claude", "claudeagent"):
        out = claude()
    else:
        out = result(args[0], note="no known config location; use the T3 catalog default or ask the user")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
