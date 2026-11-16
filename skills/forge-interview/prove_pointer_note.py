#!/usr/bin/env python3
"""Prove: refreshing a home line keeps the note written after it.

A home line may carry a hand-written note after the standard part, as the
Foundry's Forge line does ("... if missing. Read its AGENTS.md first.").
Refreshing that project's line must keep the note byte for byte, and a line
that already matches must not change at all.
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


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-note-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        home.mkdir()
        project = tmp / "project"
        project.mkdir()
        subprocess.run(["git", "-C", str(project), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(project), "remote", "add", "origin", "git@github.com:me/project.git"], check=True
        )
        for purpose, note in (("a project", " Read its AGENTS.md first."), ("new words", " Read its AGENTS.md first.")):
            line = f"Project (a project): {project.resolve()}. Clone from git@github.com:me/project.git if missing.{note}"
            (home / "AGENTS.md").write_text(f"# Home\n\n## Other Repos\n\n{line}\n", encoding="utf-8")
            before = (home / "AGENTS.md").read_bytes()
            answers = {
                "what": "a thing", "who": "me", "done": "it exists", "constraints": "none", "ready": True,
                "home_mode": "repo", "home_path": str(home), "home_pointer": "Project",
                "home_pointer_text": purpose, "home_skills_link": False, "home_wiki": "no", "home_wiki_page": None,
            }
            target = tmp / f"t-{purpose.replace(' ', '-')}"
            target.mkdir()
            proc = subprocess.run(
                [sys.executable, str(APPLY), "--target", str(target), "--product", "generic",
                 "--answers-json", json.dumps(answers), "--home", str(home), "--project", str(project)],
                cwd=str(ROOT), capture_output=True, text=True, check=False,
            )
            if proc.returncode != 0:
                fail(f"apply failed: {proc.stderr or proc.stdout}")
            after = (home / "AGENTS.md").read_text(encoding="utf-8")
            if purpose == "a project" and after.encode() != before:
                fail(f"a matching line changed:\n{after}")
            if not after.rstrip("\n").endswith(f"if missing.{note}"):
                fail(f"the note after the line was dropped:\n{after}")
            if purpose == "new words" and "Project (new words):" not in after:
                fail(f"the purpose was not refreshed:\n{after}")
    print("PASS: prove_pointer_note")


if __name__ == "__main__":
    main()
