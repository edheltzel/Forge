#!/usr/bin/env python3
"""Change 4 prove: a skills line inside the forge-icm block, text only.

With home_mode folder or repo and home_skills_link true, apply puts one line
"Shared skills: <home_path>/skills/." inside the project's forge-icm block.
False, home_mode none, or no home keys leave the block as it was. Apply never
creates a symlink, a skills folder, or anything in the home repo for this.
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
BASE = {"what": "a thing", "who": "me", "done": "it exists", "constraints": "none known yet", "ready": True}


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def apply(target: Path, answers: dict) -> None:
    merged = dict(BASE)
    merged.update(answers)
    proc = subprocess.run(
        [sys.executable, str(APPLY), "--target", str(target), "--product", "generic",
         "--answers-json", json.dumps(merged)],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        fail(f"apply failed: {proc.stderr or proc.stdout}")


def block(target: Path) -> str:
    text = (target / "AGENTS.md").read_text(encoding="utf-8")
    start = text.index("<!-- forge-icm:start -->")
    end = text.index("<!-- forge-icm:end -->")
    return text[start:end]


def home_keys(home: Path, mode: str, skills: bool) -> dict:
    return {
        "home_mode": mode,
        "home_path": str(home),
        "home_pointer": None,
        "home_pointer_text": "",
        "home_skills_link": skills,
        "home_wiki": "no",
        "home_wiki_page": None,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-skills-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        home.mkdir()
        (home / "AGENTS.md").write_text("# Home\n\n## Other Repos\n", encoding="utf-8")
        home_before = sorted(p.relative_to(home).as_posix() for p in home.rglob("*"))
        line = f"Shared skills: {home}/skills/."

        on = tmp / "on"
        on.mkdir()
        apply(on, home_keys(home, "repo", True))
        if block(on).count(line) != 1:
            fail(f"skills line missing or doubled in the block:\n{block(on)}")
        outside = (on / "AGENTS.md").read_text(encoding="utf-8").replace(block(on), "")
        if line in outside:
            fail("skills line landed outside the forge-icm block")

        apply(on, home_keys(home, "repo", True))
        if block(on).count(line) != 1:
            fail("a second apply doubled the skills line")

        for name, keys in (
            ("off", home_keys(home, "folder", False)),
            ("none", {"home_mode": "none"}),
            ("plain", {}),
        ):
            target = tmp / name
            target.mkdir()
            apply(target, keys)
            if "Shared skills:" in block(target):
                fail(f"{name}: skills line written when it should not be")

        links = [p for p in tmp.rglob("*") if p.is_symlink()]
        if links:
            fail(f"apply created symlinks: {links}")
        if sorted(p.relative_to(home).as_posix() for p in home.rglob("*")) != home_before:
            fail("apply changed the home repo for a skills link")

    print("PASS: prove_skills_link")


if __name__ == "__main__":
    main()
