#!/usr/bin/env python3
"""Change 5 prove: the wiki page and link.

Runs only against temp home copies. home_wiki "create" writes
<home>/wiki/projects/<slug>.md from the brief and lists it in wiki/index.md,
never overwriting: a page that already exists is linked instead. Both
"create" and "link" put "Wiki: <path>" inside the forge-icm block. A second
create changes nothing. "no", home_mode none, and no home keys write no wiki
page and no wiki line. The "Saved, not applied yet" message is gone.
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
BASE = {
    "what": "a sample tool",
    "who": "the captain",
    "done": "it runs",
    "constraints": "no network",
    "ready": True,
}


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def apply(target: Path, home: Path, answers: dict) -> subprocess.CompletedProcess[str]:
    merged = dict(BASE)
    merged.update(answers)
    proc = subprocess.run(
        [sys.executable, str(APPLY), "--target", str(target), "--product", "generic",
         "--answers-json", json.dumps(merged), "--home", str(home), "--project", str(target)],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        fail(f"apply failed: {proc.stderr or proc.stdout}")
    if "Saved, not applied yet" in proc.stdout + proc.stderr:
        fail("still says saved, not applied yet")
    return proc


def keys(home: Path, wiki: str, page: str | None = "Sample") -> dict:
    return {
        "home_mode": "repo",
        "home_path": str(home),
        "home_pointer": "Sample",
        "home_pointer_text": "a sample tool",
        "home_skills_link": False,
        "home_wiki": wiki,
        "home_wiki_page": page,
    }


def block(target: Path) -> str:
    text = (target / "AGENTS.md").read_text(encoding="utf-8")
    return text[text.index("<!-- forge-icm:start -->"):text.index("<!-- forge-icm:end -->")]


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def make_home(tmp: Path, name: str) -> Path:
    home = tmp / name
    (home / "wiki").mkdir(parents=True)
    (home / "AGENTS.md").write_text("# Home\n\n## Other Repos\n", encoding="utf-8")
    (home / "wiki" / "index.md").write_text("# Wiki\n\nList of wiki pages.\n", encoding="utf-8")
    return home


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-wiki-") as raw:
        tmp = Path(raw)

        # Create: page from the brief, listed once in the index, linked in the block.
        home = make_home(tmp, "home-create")
        target = tmp / "create"
        target.mkdir()
        apply(target, home, keys(home, "create"))
        page = home / "wiki" / "projects" / "sample.md"
        if not page.is_file():
            fail("create did not write the wiki page")
        body = page.read_text(encoding="utf-8")
        for want in ("a sample tool", "the captain", "it runs", "no network", str(target.resolve())):
            if want not in body:
                fail(f"page is missing {want!r}:\n{body}")
        index = (home / "wiki" / "index.md").read_text(encoding="utf-8")
        if index.count("projects/sample.md") != 1:
            fail(f"index should list the page once:\n{index}")
        if "List of wiki pages." not in index:
            fail("index lost its existing text")
        if f"Wiki: {page}" not in block(target):
            fail(f"block has no wiki line:\n{block(target)}")

        # Create twice: nothing changes the second time.
        before_home = tree(home)
        before_target = (target / "AGENTS.md").read_bytes()
        apply(target, home, keys(home, "create"))
        if tree(home) != before_home:
            fail("second create changed the home repo")
        if (target / "AGENTS.md").read_bytes() != before_target:
            fail("second create changed the project AGENTS.md")

        # Create over an existing page: never overwrite; link it instead.
        home = make_home(tmp, "home-existing")
        existing = home / "wiki" / "projects" / "sample.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("hand written\n", encoding="utf-8")
        target = tmp / "existing"
        target.mkdir()
        apply(target, home, keys(home, "create"))
        if existing.read_text(encoding="utf-8") != "hand written\n":
            fail("create overwrote an existing page")
        if f"Wiki: {existing}" not in block(target):
            fail("existing page was not linked")

        # Link: line in the block, no page and no index change.
        home = make_home(tmp, "home-link")
        target = tmp / "link"
        target.mkdir()
        before_home = tree(home)
        apply(target, home, keys(home, "link"))
        wanted = home / "wiki" / "projects" / "sample.md"
        if f"Wiki: {wanted}" not in block(target):
            fail(f"link did not add the wiki line:\n{block(target)}")
        after = {k: v for k, v in tree(home).items() if k != "AGENTS.md"}
        if after != {k: v for k, v in before_home.items() if k != "AGENTS.md"}:
            fail("link wrote into the wiki")

        # No, none, plain: no page, no line.
        for name, answers in (
            ("no", keys(make_home(tmp, "home-no"), "no")),
            ("none", {"home_mode": "none"}),
            ("plain", {}),
        ):
            home = Path(answers["home_path"]) if "home_path" in answers else make_home(tmp, f"home-{name}")
            target = tmp / name
            target.mkdir()
            apply(target, home, answers)
            if "Wiki:" in block(target):
                fail(f"{name}: wiki line written")
            if (home / "wiki" / "projects").exists():
                fail(f"{name}: wiki page written")

    print("PASS: prove_wiki")


if __name__ == "__main__":
    main()
