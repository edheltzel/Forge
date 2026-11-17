#!/usr/bin/env python3
"""Change 6 prove: Forge's docs carry no stale paths and explain the home answer.

Fails on any tracked markdown file (outside docs/plans/) that still names the
removed ForgeTemplates workbench or the lowercase ~/Developer/forge path. Also
requires an "If you use a home folder or home repo" section in README.md and
docs/getting-started.md.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADING = "## If you use a home folder or home repo"
STALE = (
    re.compile(r"ForgeTemplates"),
    re.compile(r"~/Developer/forge(?![A-Za-z])"),
)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md"], capture_output=True, text=True, check=True
    ).stdout.split()
    hits = []
    for rel in tracked:
        if rel.startswith("docs/plans/"):
            continue
        path = ROOT / rel
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(p.search(line) for p in STALE):
                hits.append(f"{rel}:{number}: {line.strip()}")
    if hits:
        fail("stale paths remain:\n" + "\n".join(hits))
    for rel in ("README.md", "docs/getting-started.md"):
        if HEADING not in (ROOT / rel).read_text(encoding="utf-8"):
            fail(f"{rel} has no '{HEADING}' section")
    print("PASS: prove_docs_paths")


if __name__ == "__main__":
    main()
