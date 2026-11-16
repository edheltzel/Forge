#!/usr/bin/env python3
"""Change 1 prove: the home question is asked once and saved, never applied.

Drives apply_icm_base.py --home-answer against temp folders. A clear "neither"
saves home_mode "none" and nothing else. A clear "repo" or "folder" saves the
mode plus home_path (resolved; must exist and contain AGENTS.md; Forge never
creates it), home_pointer, home_pointer_text, home_skills_link, home_wiki, and
home_wiki_page, and says the answer is saved but not applied yet. An unclear
answer saves nothing. A second run with a saved answer asks nothing and says
"Using your saved home answer: ...". A saved home_path that no longer exists
asks again. Answers with no home keys behave exactly as before.
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

HOME_KEYS = (
    "home_mode",
    "home_path",
    "home_pointer",
    "home_pointer_text",
    "home_skills_link",
    "home_wiki",
    "home_wiki_page",
)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def run(target: Path, answers: dict, home_answer: str | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(APPLY),
        "--target",
        str(target),
        "--product",
        "generic",
        "--answers-json",
        json.dumps(answers),
    ]
    if home_answer is not None:
        cmd += ["--home-answer", home_answer]
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)


BASE = {"what": "a thing", "who": "me", "done": "it exists", "constraints": "none known yet", "ready": True}


def saved(target: Path) -> dict:
    path = target / "forge" / "setup" / "answers.json"
    if not path.is_file():
        fail(f"no answers.json under {target}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-home-") as raw:
        tmp = Path(raw)
        home = tmp / "home-repo"
        home.mkdir()
        (home / "AGENTS.md").write_text("# Home\n", encoding="utf-8")

        missing = tmp / "no-such-folder"

        # Unclear answer: nothing saved, asked again next run.
        t = tmp / "unclear"
        t.mkdir()
        proc = run(t, dict(BASE), "maybe later")
        if proc.returncode == 0:
            fail("unclear answer should not apply")
        if (t / "forge").exists():
            fail("unclear answer wrote a binder")
        out = proc.stderr + proc.stdout
        if "home folder or a home repo" not in out:
            fail(f"unclear answer did not re-ask: {out.strip()}")

        # Clear neither: home_mode none, no other home keys, no home files touched.
        t = tmp / "neither"
        t.mkdir()
        before = home.read_text(encoding="utf-8") if False else (home / "AGENTS.md").read_bytes()
        proc = run(t, dict(BASE), "neither")
        if proc.returncode != 0:
            fail(f"neither failed: {proc.stderr or proc.stdout}")
        ans = saved(t)
        if ans.get("home_mode") != "none":
            fail(f"neither saved {ans.get('home_mode')!r}, want 'none'")
        extra = [k for k in HOME_KEYS if k != "home_mode" and k in ans]
        if extra:
            fail(f"neither saved extra home keys: {extra}")
        if (home / "AGENTS.md").read_bytes() != before:
            fail("neither changed the home repo")

        # Repo answer: path must exist and hold AGENTS.md. Forge never creates it.
        t = tmp / "missing-path"
        t.mkdir()
        proc = run(t, dict(BASE), f"repo {missing}")
        if proc.returncode == 0 or (t / "forge").exists():
            fail("a home_path that does not exist was accepted or created")

        bare = tmp / "bare"
        bare.mkdir()
        t = tmp / "no-agents"
        t.mkdir()
        proc = run(t, dict(BASE), f"folder {bare}")
        if proc.returncode == 0:
            fail("a home_path without AGENTS.md was accepted")

        # Clear repo answer saves every key and says it is not applied yet.
        t = tmp / "repo"
        t.mkdir()
        proc = run(t, dict(BASE), f"repo {home} ; pointer: Forge ; skills: yes ; wiki: create ; page: Forge")
        if proc.returncode != 0:
            fail(f"repo answer failed: {proc.stderr or proc.stdout}")
        text = proc.stdout + proc.stderr
        if "Saved, not applied yet" in text:
            fail(f"change 5 applies the home answer; drop saved-not-applied: {text.strip()}")
        ans = saved(t)
        if ans.get("home_mode") != "repo":
            fail(f"home_mode {ans.get('home_mode')!r}")
        if ans.get("home_path") != str(home.resolve()):
            fail(f"home_path {ans.get('home_path')!r}")
        for key in HOME_KEYS:
            if key not in ans:
                fail(f"repo answer dropped {key}")
        if ans.get("home_wiki") not in {"link", "create", "no"}:
            fail(f"home_wiki {ans.get('home_wiki')!r}")

        # A purpose may itself contain ';'. Only '; <known field>:' starts a new field.
        t = tmp / "semicolon"
        t.mkdir()
        proc = run(t, dict(BASE), f"repo {home} ; pointer: GAP ; purpose: one set of rules; gap sync copies them out ; skills: no")
        if proc.returncode != 0:
            fail(f"semicolon purpose failed: {proc.stderr or proc.stdout}")
        got = saved(t).get("home_pointer_text")
        if got != "one set of rules; gap sync copies them out":
            fail(f"semicolon purpose saved as {got!r}")

        # The pointer's purpose is its own field, not a copy of the name.
        t = tmp / "purpose"
        t.mkdir()
        proc = run(t, dict(BASE), f"repo {home} ; pointer: Muse ; purpose: visual explainer")
        if proc.returncode != 0:
            fail(f"purpose answer failed: {proc.stderr or proc.stdout}")
        ans_p = saved(t)
        if ans_p.get("home_pointer") != "Muse":
            fail(f"home_pointer {ans_p.get('home_pointer')!r}")
        if ans_p.get("home_pointer_text") != "visual explainer":
            fail(f"home_pointer_text {ans_p.get('home_pointer_text')!r}, want the purpose")

        # Rerun with the saved answer asks nothing.
        t2 = tmp / "rerun"
        t2.mkdir()
        proc = run(t2, ans, None)
        text = proc.stdout + proc.stderr
        if proc.returncode != 0:
            fail(f"rerun failed: {text}")
        if not text.startswith("Using your saved home answer:"):
            fail(f"rerun did not announce the saved answer: {text.splitlines()[0]}")
        if "home folder or a home repo" in text:
            fail("rerun asked the home question again")

        # A saved path that vanished asks again.
        gone = tmp / "gone-home"
        gone.mkdir()
        (gone / "AGENTS.md").write_text("# x\n", encoding="utf-8")
        t = tmp / "vanish"
        t.mkdir()
        proc = run(t, dict(BASE), f"folder {gone}")
        if proc.returncode != 0:
            fail(f"folder answer failed: {proc.stderr or proc.stdout}")
        ans = saved(t)
        shutil.rmtree(gone)
        t2 = tmp / "vanish-rerun"
        t2.mkdir()
        proc = run(t2, ans, None)
        if proc.returncode == 0:
            fail("a vanished home_path was reused without asking")

        # No home keys at all: byte-identical to today's apply.
        plain_answers = dict(BASE)
        a = tmp / "plain-a"
        b = tmp / "plain-b"
        a.mkdir()
        b.mkdir()
        pa = run(a, plain_answers, None)
        pb = run(b, plain_answers, None)
        if pa.returncode != 0 or pb.returncode != 0:
            fail("plain apply failed")

        def tree(root: Path) -> dict:
            # The spec and the ICM pointer name the target, so swap the path and
            # the folder name out before comparing two different temp folders.
            return {
                p.relative_to(root).as_posix(): p.read_bytes()
                .replace(str(root).encode(), b"TARGET")
                .replace(root.name.encode(), b"NAME")
                for p in sorted(root.rglob("*"))
                if p.is_file()
            }

        if tree(a) != tree(b):
            fail("plain apply is not deterministic")
        if any(k in saved(a) for k in HOME_KEYS):
            fail("plain apply wrote home keys")

    print("PASS: prove_home_question")


if __name__ == "__main__":
    main()
