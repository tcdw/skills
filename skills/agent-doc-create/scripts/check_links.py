#!/usr/bin/env python3
"""Check relative markdown links in AGENTS.md and agent-doc/.

Usage:
    python check_links.py <repo-root> [repo-root2 ...]

For each repo root, scans AGENTS.md (if present) and every *.md under
agent-doc/, then verifies that each relative markdown link target exists on
disk. External URLs (http/https/mailto) and pure anchors are skipped. Link
targets are URL-decoded before resolving, so "%20" style escapes in links to
filenames containing spaces are handled correctly.

Exits 1 if any broken link is found, 0 otherwise.
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Inline markdown link/image: [text](target "optional title") or [text](<target>)
LINK_RE = re.compile(r"\[[^\]]*\]\(<([^>]*)>|!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL_SCHEMES = {"http", "https", "mailto"}


def visible_lines(text):
    """Yield (lineno, line) for lines outside fenced code blocks."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line


def extract_targets(line):
    for match in LINK_RE.finditer(line):
        target = match.group(1) or match.group(2)
        if target:
            yield target


def check_repo(root):
    """Return (checked_count, broken_list) for one repo root."""
    root = Path(root).resolve()
    files = []
    agents_md = root / "AGENTS.md"
    if agents_md.is_file():
        files.append(agents_md)
    agent_doc = root / "agent-doc"
    if agent_doc.is_dir():
        files.extend(sorted(agent_doc.rglob("*.md")))

    checked = 0
    broken = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in visible_lines(text):
            for target in extract_targets(line):
                parts = urlsplit(target)
                if parts.scheme.lower() in EXTERNAL_SCHEMES:
                    continue
                if parts.netloc:
                    continue  # protocol-relative or authority-bearing URL
                decoded = unquote(parts.path)
                if not decoded:
                    continue  # pure anchor like #section
                resolved = (path.parent / decoded).resolve()
                checked += 1
                if not resolved.exists():
                    broken.append(f"{path.relative_to(root)}:{lineno} -> {target}")
    return checked, broken


def main():
    parser = argparse.ArgumentParser(
        description="Check relative markdown links in AGENTS.md and agent-doc/."
    )
    parser.add_argument("roots", nargs="+", help="repository root directory(ies)")
    args = parser.parse_args()

    total_checked = 0
    all_broken = []
    for root in args.roots:
        if not Path(root).is_dir():
            print(f"[ERROR] not a directory: {root}")
            sys.exit(2)
        checked, broken = check_repo(root)
        total_checked += checked
        all_broken.extend(broken)
        status = "OK" if not broken else "BROKEN"
        print(f"[{status}] {root}: {checked} links checked, {len(broken)} broken")
        for item in broken:
            print(f"  - {item}")

    if all_broken:
        print(f"FAILED: {len(all_broken)} broken link(s) found")
        sys.exit(1)
    print(f"PASSED: {total_checked} links checked, all targets exist")
    sys.exit(0)


if __name__ == "__main__":
    main()
