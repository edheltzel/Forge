#!/usr/bin/env python3
"""Change 7 prove: the foundry-docs block at the end of the project's AGENTS.md.

Runs only against temp folders. With home_mode folder or repo, apply adds or
refreshes this block at the end of the project's AGENTS.md:

    <!-- foundry-docs:start -->
    Folder docs: follow <home_path>/docs/self-updating-docs.md. Use a short FOLDER.md in a folder you actually change, only if none exists or if asked.
    <!-- foundry-docs:end -->

Covers: first apply, idempotent second apply (same digest), drift, hand edits,
a block the user deleted (never put back unless asked with --add-folder-docs),
a missing rule file (refuse, project file left alone by this block), home_mode
none or missing (no block), no new FOLDER.md or docs/ tree, and the standalone
--refresh-docs mode.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[1]
APPLY = DIR / "apply_icm_base.py"
BASE = {"what": "a thing", "who": "me", "done": "it exists", "constraints": "none known yet", "ready": True}
START = "<!-- foundry-docs:start -->"
END = "<!-- foundry-docs:end -->"


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def canonical(home: Path) -> str:
    return (
        f"{START}\n"
        f"Folder docs: follow {home}/docs/self-updating-docs.md. Use a short FOLDER.md in a folder "
        "you actually change, only if none exists or if asked.\n"
        f"{END}\n"
    )


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(APPLY), *args], cwd=str(ROOT), capture_output=True, text=True, check=False)


def apply(target: Path, answers: dict, *extra: str) -> subprocess.CompletedProcess[str]:
    merged = dict(BASE)
    merged.update(answers)
    proc = run("--target", str(target), "--product", "generic", "--answers-json", json.dumps(merged), *extra)
    if proc.returncode != 0:
        fail(f"apply failed: {proc.stderr or proc.stdout}")
    return proc


def saved(target: Path) -> dict:
    return json.loads((target / "forge" / "setup" / "answers.json").read_text(encoding="utf-8"))


def home_keys(home: Path, mode: str = "repo") -> dict:
    return {
        "home_mode": mode,
        "home_path": str(home),
        "home_pointer": None,
        "home_pointer_text": "",
        "home_skills_link": False,
        "home_wiki": "no",
        "home_wiki_page": None,
    }


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_home(tmp: Path, name: str, rule: bool = True) -> Path:
    home = tmp / name
    home.mkdir()
    (home / "AGENTS.md").write_text("# Home\n\n## Other Repos\n", encoding="utf-8")
    if rule:
        (home / "docs").mkdir()
        (home / "docs" / "self-updating-docs.md").write_text("# Self-updating docs\n", encoding="utf-8")
    return home


def files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*")}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-docs-") as raw:
        tmp = Path(raw)
        home = make_home(tmp, "home")
        block = canonical(home)

        # First apply: block appended at the end, exact text.
        target = tmp / "first"
        target.mkdir()
        (target / "AGENTS.md").write_text("# Mine\n\nHand line one.\n", encoding="utf-8")
        apply(target, home_keys(home))
        agents = target / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        if not text.endswith(block):
            fail(f"block is not the canonical text at the end:\n{text}")
        if text.count(START) != 1:
            fail("block appears more than once")
        if not text.startswith("# Mine\n\nHand line one.\n"):
            fail("hand lines before the block changed")
        if saved(target).get("home_folder_docs") != "on":
            fail("answers.json does not record the block as on")

        # Second apply with the saved answers: same digest.
        first = digest(agents)
        apply(target, saved(target))
        if digest(agents) != first:
            fail("second apply changed AGENTS.md")

        # Drift: inner text differs, only the inner text is rewritten.
        drifted = text.replace(block, f"{START}\nFolder docs: an old rule.\n{END}\n") + "Trailing hand line.\n"
        agents.write_text(drifted, encoding="utf-8")
        apply(target, saved(target))
        text = agents.read_text(encoding="utf-8")
        if "an old rule" in text:
            fail("drifted inner text was not refreshed")
        if not text.endswith(block + "Trailing hand line.\n"):
            fail(f"refresh moved or dropped lines outside the block:\n{text}")

        # Hand edits elsewhere survive byte for byte.
        edited = text.replace("Hand line one.", "Hand line one, edited by hand.")
        agents.write_text(edited, encoding="utf-8")
        apply(target, saved(target))
        if agents.read_text(encoding="utf-8") != edited:
            fail("apply changed hand edits outside the block")

        # Deleted block: never put back without being asked.
        start = edited.index(START)
        end = edited.index(END) + len(END) + 1
        removed = edited[:start] + edited[end:]
        agents.write_text(removed, encoding="utf-8")
        apply(target, saved(target))
        if START in agents.read_text(encoding="utf-8"):
            fail("a deleted block was put back")
        if saved(target).get("home_folder_docs") != "off":
            fail("answers.json does not record the block as removed")
        apply(target, saved(target))
        if START in agents.read_text(encoding="utf-8"):
            fail("a deleted block came back on the next run")

        # Asked: "add the folder-docs rule" puts it back.
        apply(target, saved(target), "--add-folder-docs")
        if not agents.read_text(encoding="utf-8").endswith(block):
            fail("--add-folder-docs did not put the block back")
        if saved(target).get("home_folder_docs") != "on":
            fail("--add-folder-docs did not record the block as on")

        # Missing rule file: refuse; no block; the project file is left alone by it.
        bare_home = make_home(tmp, "bare-home", rule=False)
        target = tmp / "missing-rule"
        target.mkdir()
        proc = apply(target, home_keys(bare_home))
        text = (target / "AGENTS.md").read_text(encoding="utf-8")
        if START in text:
            fail("block written though the rule file is missing")
        if "self-updating-docs.md" not in proc.stdout + proc.stderr:
            fail(f"missing rule file was not reported: {proc.stdout}{proc.stderr}")

        # home_mode none and no home keys: no block, and no answers key.
        for name, answers in (("none", {"home_mode": "none"}), ("plain", {})):
            target = tmp / name
            target.mkdir()
            apply(target, answers)
            if START in (target / "AGENTS.md").read_text(encoding="utf-8"):
                fail(f"{name}: block written")
            if "home_folder_docs" in saved(target):
                fail(f"{name}: answers.json gained home_folder_docs")

        # No new FOLDER.md or docs/ tree beyond what a plain apply makes.
        plain_files = files(tmp / "plain")
        target = tmp / "tree"
        target.mkdir()
        apply(target, home_keys(home))
        if files(target) != plain_files:
            fail(f"block apply made extra files: {sorted(files(target) ^ plain_files)}")
        if any(p.name == "FOLDER.md" for p in tmp.rglob("*")):
            fail("a FOLDER.md was created")
        if files(home) != {"AGENTS.md", "docs", "docs/self-updating-docs.md"}:
            fail(f"the home repo changed: {sorted(files(home))}")

        # Standalone refresh: drift fixed, nothing else touched.
        agents = target / "AGENTS.md"
        agents.write_text(
            agents.read_text(encoding="utf-8").replace(block, f"{START}\nstale\n{END}\n"), encoding="utf-8"
        )
        before_files = files(target)
        proc = run("--refresh-docs", "--home", str(home), "--project", str(target))
        if proc.returncode != 0:
            fail(f"--refresh-docs failed: {proc.stderr or proc.stdout}")
        if not agents.read_text(encoding="utf-8").endswith(block):
            fail("--refresh-docs did not refresh the block")
        if files(target) != before_files:
            fail("--refresh-docs touched other files")
        same = digest(agents)
        run("--refresh-docs", "--home", str(home), "--project", str(target))
        if digest(agents) != same:
            fail("--refresh-docs is not idempotent")

    print("PASS: prove_home_docs")


if __name__ == "__main__":
    main()
