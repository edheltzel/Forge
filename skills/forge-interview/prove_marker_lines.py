#!/usr/bin/env python3
"""Prove: block markers count only on their own line.

An AGENTS.md may quote a marker in prose, as Forge's own does ("one
marker-guarded pointer (`<!-- forge-icm:start -->`)"). Apply must treat only a
marker that is the whole line as a block edge. Applying twice to such a file
keeps the prose byte for byte and leaves exactly one block of each kind.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[1]
APPLY = DIR / "apply_icm_base.py"
PROSE = (
    "# Mine\n\n"
    "Keep one marker-guarded pointer (`<!-- forge-icm:start -->`) aimed at `forge/`.\n"
    "Refresh the `<!-- foundry-docs:start -->` block, never duplicate it.\n"
)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-markers-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        (home / "docs").mkdir(parents=True)
        (home / "AGENTS.md").write_text("# Home\n\n## Other Repos\n", encoding="utf-8")
        (home / "docs" / "self-updating-docs.md").write_text("# Rules\n", encoding="utf-8")
        target = tmp / "project"
        target.mkdir()
        (target / "AGENTS.md").write_text(PROSE, encoding="utf-8")
        answers = {
            "what": "a thing", "who": "me", "done": "it exists", "constraints": "none", "ready": True,
            "home_mode": "repo", "home_path": str(home), "home_pointer": "Mine", "home_pointer_text": "a project",
            "home_skills_link": False, "home_wiki": "no", "home_wiki_page": None,
        }
        for run in (1, 2, 3):
            src = json.dumps(answers) if run == 1 else (target / "forge" / "setup" / "answers.json").read_text()
            proc = subprocess.run(
                [sys.executable, str(APPLY), "--target", str(target), "--product", "generic",
                 "--answers-json", src],
                cwd=str(ROOT), capture_output=True, text=True, check=False,
            )
            if proc.returncode != 0:
                fail(f"apply {run} failed: {proc.stderr or proc.stdout}")
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            if not text.startswith(PROSE):
                fail(f"apply {run} changed the prose that quotes a marker:\n{text}")
            for marker in ("<!-- forge-icm:start -->", "<!-- foundry-docs:start -->"):
                own = [ln for ln in text.splitlines() if ln == marker]
                if len(own) != 1:
                    fail(f"apply {run}: {len(own)} blocks start with {marker}")
            if run == 2:
                second = text
            if run == 3 and text != second:
                fail("third apply changed AGENTS.md")
    print("PASS: prove_marker_lines")


if __name__ == "__main__":
    main()
