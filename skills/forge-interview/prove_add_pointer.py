#!/usr/bin/env python3
"""Change 2 prove: apply adds this project's line to the home repo.

Runs only against temp copies. Never touches the real Foundry. A home answer of
"repo" or "folder" adds one line under "## Other Repos":

    <Name> (<purpose>): <full path>. Clone from <origin> if missing.

"Clone from" is dropped when the project has no origin remote. The path is the
full resolved path, never "~". A second apply refreshes that one line instead
of adding another. A line that points at the same folder through "~", a
trailing slash, or a symlink counts as the same line. Hand edits to every other
line survive byte for byte. foundry-check then prints all clear.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[1]
APPLY = DIR / "apply_icm_base.py"
CHECK = Path("/Users/ed/Developer/Foundry/bin/foundry-check")

BASE = {"what": "a thing", "who": "me", "done": "it exists", "constraints": "none known yet", "ready": True}


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, check=False)


def pointer_lines(text: str) -> list[str]:
    lines, inside = [], False
    for raw in text.splitlines():
        if raw.startswith("## "):
            inside = raw.strip() == "## Other Repos"
            continue
        if inside and raw.strip():
            lines.append(raw)
    return lines


def apply(
    target: Path, home: Path | None, project: Path | None = None, **answers: object
) -> subprocess.CompletedProcess[str]:
    merged = dict(BASE)
    merged.update(answers)
    cmd = [
        sys.executable,
        str(APPLY),
        "--target",
        str(target),
        "--product",
        "generic",
        "--answers-json",
        json.dumps(merged),
    ]
    if home is not None:
        cmd += ["--home", str(home)]
    if project is not None:
        cmd += ["--project", str(project)]
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)


def home_answers(mode: str, home: Path, name: str, purpose: str) -> dict:
    return {
        "home_mode": mode,
        "home_path": str(home),
        "home_pointer": name,
        "home_pointer_text": purpose,
        "home_skills_link": False,
        "home_wiki": "no",
        "home_wiki_page": None,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-pointer-") as raw:
        tmp = Path(raw)

        home = tmp / "home"
        home.mkdir()
        (home / "docs").mkdir()
        for name in ("self-updating-docs.md", "folder-doc.md"):
            shutil.copy(Path("/Users/ed/Developer/Foundry") / "docs" / name, home / "docs" / name)
        intro = (
            "# Home\n\n"
            "Not this folder: /Users/ed/Developer/Atlas/Foundry is the old one.\n\n"
            "## Other Repos\n\n"
            "Echo (hear your agents): /Users/ed/Developer/Atlas/Echo. "
            "Clone from git@github.com:edheltzel/Echo.git if missing. "
            "# kept by hand\n"
        )
        agents = home / "AGENTS.md"
        agents.write_text(intro, encoding="utf-8")
        before = agents.read_bytes()

        # A project with an origin remote.
        project = tmp / "project"
        project.mkdir()
        git(project, "init", "-q", "-b", "master")
        git(project, "remote", "add", "origin", "git@github.com:edheltzel/project.git")

        # No --home: the home file is not touched.
        target = tmp / "nohome"
        target.mkdir()
        proc = apply(target, None)
        if proc.returncode != 0:
            fail(f"plain apply failed: {proc.stderr or proc.stdout}")
        if agents.read_bytes() != before:
            fail("an apply with no home answer changed the home repo")

        # Repo answer: one line, with Clone from, full path, never "~".
        target = tmp / "with-origin"
        target.mkdir()
        proc = apply(
            target,
            home,
            project,
            home_mode="repo",
            home_path=str(home),
            home_pointer="Project",
            home_pointer_text="a sample project",
            home_skills_link=False,
            home_wiki="no",
            home_wiki_page=None,
        )
        if proc.returncode != 0:
            fail(f"apply failed: {proc.stderr or proc.stdout}")
        text = agents.read_text(encoding="utf-8")
        wanted = (
            f"Project (a sample project): {project.resolve()}. "
            "Clone from git@github.com:edheltzel/project.git if missing."
        )
        lines = pointer_lines(text)
        if wanted not in lines:
            fail(f"missing pointer line; got {lines}")
        if "~" in text.split("## Other Repos", 1)[1]:
            fail("pointer uses ~")

        # Hand edits elsewhere survive byte for byte.
        kept = [ln for ln in text.splitlines() if ln.startswith("Echo ")]
        if kept != [ln for ln in intro.splitlines() if ln.startswith("Echo ")]:
            fail("the hand-written Echo line changed")
        if "# kept by hand" not in text:
            fail("the hand-written trailing note was dropped")

        # A second apply refreshes; it does not add a second line.
        proc = apply(target, home, project, **home_answers("repo", home, "Project", "a sample project"))
        if proc.returncode != 0:
            fail(f"second apply failed: {proc.stderr or proc.stdout}")
        if pointer_lines(agents.read_text(encoding="utf-8")).count(wanted) != 1:
            fail("second apply duplicated the line")

        # The same folder through a symlink is the same line, not a new one.
        link = tmp / "project-link"
        link.symlink_to(project)
        target = tmp / "via-link"
        target.mkdir()
        proc = apply(
            link,
            home,
            link,
            home_mode="repo",
            home_path=str(home),
            home_pointer="Project",
            home_pointer_text="renamed purpose",
            home_skills_link=False,
            home_wiki="no",
                home_wiki_page=None,
        )
        if proc.returncode != 0:
            fail(f"symlink apply failed: {proc.stderr or proc.stdout}")
        lines = pointer_lines(agents.read_text(encoding="utf-8"))
        project_lines = [ln for ln in lines if ln.startswith("Project ")]
        if len(project_lines) != 1:
            fail(f"symlink created a second line: {project_lines}")
        if "renamed purpose" not in project_lines[0]:
            fail("refresh did not update the purpose")
        if str(link) in project_lines[0]:
            fail("line kept the symlink path instead of the resolved one")

        # No origin remote: no "Clone from".
        bare = tmp / "bare-project"
        bare.mkdir()
        git(bare, "init", "-q", "-b", "master")
        target = tmp / "no-origin"
        target.mkdir()
        proc = apply(
            target,
            home,
            bare,
            home_mode="folder",
            home_path=str(home),
            home_pointer="Bare",
            home_pointer_text="no remote",
            home_skills_link=False,
            home_wiki="no",
                home_wiki_page=None,
        )
        if proc.returncode != 0:
            fail(f"no-origin apply failed: {proc.stderr or proc.stdout}")
        bare_lines = [ln for ln in pointer_lines(agents.read_text(encoding="utf-8")) if ln.startswith("Bare ")]
        if len(bare_lines) != 1 or "Clone from" in bare_lines[0]:
            fail(f"no-origin line wrong: {bare_lines}")
        if not bare_lines[0].endswith(f"{bare.resolve()}."):
            fail(f"no-origin line shape wrong: {bare_lines[0]}")

        # foundry-check against the temp copy prints all clear.
        env = dict(os.environ)
        proc = subprocess.run([sys.executable, str(CHECK), str(agents)], capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            fail(f"foundry-check failed:\n{proc.stdout}{proc.stderr}")
        if "all clear" not in proc.stdout:
            fail(f"foundry-check did not say all clear: {proc.stdout.strip()}")

        # home_mode none writes nothing.
        again = agents.read_bytes()
        target = tmp / "none"
        target.mkdir()
        proc = apply(target, home, home_mode="none")
        if proc.returncode != 0:
            fail(f"none apply failed: {proc.stderr or proc.stdout}")
        if agents.read_bytes() != again:
            fail("home_mode none changed the home repo")

    print("PASS: prove_add_pointer")


if __name__ == "__main__":
    main()
