#!/usr/bin/env python3
"""Change 3 prove: remove one project's line from the home repo, on request only.

Runs only against temp copies. `apply_icm_base.py --remove-pointer <project>
--home <home>` removes the one line under "## Other Repos" that points at that
folder, matched the same way a line is added: expand "~", drop a trailing
slash, resolve symlinks.

One match prints "Removed: <line>" and leaves every other line byte for byte.
No match prints "No line in <home>/AGENTS.md points at <path>. Nothing
changed." and leaves the file byte for byte identical. Two matches list both
lines and ask which, changing nothing. The command never touches folders,
project files, forge/, or wiki pages, and a normal apply never removes a line.
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


def remove(home: Path, project: Path, choose: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(APPLY),
        "--remove-pointer",
        str(project),
        "--home",
        str(home),
    ]
    if choose is not None:
        cmd += ["--choose", choose]
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-remove-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        home.mkdir()
        project = tmp / "project"
        project.mkdir()
        other = tmp / "other"
        other.mkdir()

        def write(lines: list[str]) -> None:
            body = "# Home\n\n## Other Repos\n\n" + "\n".join(lines) + "\n"
            (home / "AGENTS.md").write_text(body, encoding="utf-8")

        one = f"Project (a sample): {project}."
        echo = "Echo (hear your agents): /Users/ed/Developer/Atlas/Echo. Clone from git@github.com:edheltzel/Echo.git if missing."

        # One match: that line goes, the hand-written line stays byte for byte.
        write([echo, one])
        before_echo = echo
        proc = remove(home, project)
        text = (home / "AGENTS.md").read_text(encoding="utf-8")
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            fail(f"one match failed: {out}")
        if f"Removed: {one}" not in out:
            fail(f"did not report the removed line: {out.strip()}")
        if one in text:
            fail("the line is still there")
        if before_echo not in text:
            fail("the hand-written line changed")

        # No match: the message, and the file byte for byte identical.
        write([echo])
        before = (home / "AGENTS.md").read_bytes()
        proc = remove(home, project)
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            fail(f"no match should not be an error: {out}")
        wanted = f"No line in {home}/AGENTS.md points at {project.resolve()}. Nothing changed."
        if wanted not in out:
            fail(f"no-match message wrong: {out.strip()}")
        if (home / "AGENTS.md").read_bytes() != before:
            fail("no match changed the file")

        # "~" and a trailing slash still count as the same folder.
        write([f"Project (a sample): {project}/."])
        proc = remove(home, project)
        if "Removed:" not in proc.stdout + proc.stderr:
            fail("a trailing slash was not matched")

        # Two matches: list them and ask, changing nothing.
        write([f"Project (one): {project}.", f"Project (two): {project}."])
        before = (home / "AGENTS.md").read_bytes()
        proc = remove(home, project)
        out = proc.stdout + proc.stderr
        if "Project (one)" not in out or "Project (two)" not in out:
            fail(f"two matches were not listed: {out.strip()}")
        if (home / "AGENTS.md").read_bytes() != before:
            fail("two matches changed the file before being asked")

        # Answering the question removes exactly that one line.
        proc = remove(home, project, choose="2")
        text = (home / "AGENTS.md").read_text(encoding="utf-8")
        if "Project (two)" in text or "Project (one)" not in text:
            fail(f"choosing 2 removed the wrong line: {text}")

        # A normal apply never removes a line.
        write([one])
        before = (home / "AGENTS.md").read_bytes()
        target = tmp / "apply-target"
        target.mkdir()
        answers = {"what": "a thing", "who": "me", "done": "it exists", "constraints": "none", "ready": True}
        proc = subprocess.run(
            [sys.executable, str(APPLY), "--target", str(target), "--product", "generic",
             "--answers-json", json.dumps(answers)],
            cwd=str(ROOT), capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            fail(f"plain apply failed: {proc.stderr or proc.stdout}")
        if (home / "AGENTS.md").read_bytes() != before:
            fail("a normal apply changed the home repo")

        # Nothing but the one line is touched: a wiki page and a project file survive.
        wiki = home / "wiki" / "projects" / "project.md"
        wiki.parent.mkdir(parents=True)
        wiki.write_text("keep\n", encoding="utf-8")
        note = project / "README.md"
        note.write_text("keep\n", encoding="utf-8")
        write([one])
        proc = remove(home, project)
        if proc.returncode != 0:
            fail(f"cleanup remove failed: {proc.stderr or proc.stdout}")
        if wiki.read_text(encoding="utf-8") != "keep\n" or note.read_text(encoding="utf-8") != "keep\n":
            fail("remove touched more than the one line")

    print("PASS: prove_remove_pointer")


if __name__ == "__main__":
    main()
