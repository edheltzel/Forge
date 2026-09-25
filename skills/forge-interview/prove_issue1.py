#!/usr/bin/env python3
"""Issue 1 prove: the three interview flows.

1. Greenfield shaped by the project type the interview inferred.
2. Brownfield repo converted to ICM without losing its own AGENTS.md or src/.
3. Greenfield continued into a spec.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
APPLY = DIR / "apply_icm_base.py"

SLOTS = {
    "what": "A weekly interview podcast about small-town bakeries",
    "who": "Me and one producer; listeners are home bakers",
    "done": "Ten episodes published and a feed accepted by Apple and Spotify",
    "constraints": "Record in one afternoon a month; no paid studio",
    "ready": True,
}

PODCAST_STAGES = ["01-format", "02-guests", "03-record", "04-edit", "05-distribute"]
DEFAULT_STAGES = ["01-intake", "02-discovery", "03-build", "04-review"]


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def apply_to(target: Path, payload: dict, product: str = "generic") -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(APPLY),
            "--target",
            str(target),
            "--product",
            product,
            "--answers-json",
            json.dumps(payload),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def stage_names(target: Path) -> list[str]:
    return sorted(p.name for p in (target / "stages").iterdir() if p.is_dir())


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(str(path.relative_to(root)).encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def prove_type_shaped_greenfield(tmp: Path) -> None:
    target = tmp / "podcast"
    payload = {**SLOTS, "project_type": "podcast launch", "stages": PODCAST_STAGES}
    proc = apply_to(target, payload)
    if proc.returncode != 0:
        fail(f"type-shaped apply should succeed: {proc.stdout}{proc.stderr}")

    got = stage_names(target)
    if got != sorted(PODCAST_STAGES):
        fail(f"stages should be the interview's own, got {got}")

    context = (target / "CONTEXT.md").read_text(encoding="utf-8")
    brief = (target / "setup" / "project-brief.md").read_text(encoding="utf-8")
    for name, text in (("CONTEXT.md", context), ("project-brief.md", brief)):
        if "podcast launch" not in text:
            fail(f"{name} should name the inferred project type")

    stage_context = (target / "stages" / "03-record" / "CONTEXT.md").read_text(encoding="utf-8")
    if "03-record" not in stage_context:
        fail("each invented stage should get its own CONTEXT.md")
    print("type-shaped greenfield OK")


def prove_stage_fallback(tmp: Path) -> None:
    target = tmp / "no-stages"
    proc = apply_to(target, dict(SLOTS))
    if proc.returncode != 0:
        fail(f"apply without stages should still succeed: {proc.stdout}{proc.stderr}")
    got = stage_names(target)
    if got != sorted(DEFAULT_STAGES):
        fail(f"absent stages should keep the generic spine, got {got}")
    print("stage fallback OK")


def prove_bad_stages_refuse(tmp: Path) -> None:
    cases = [
        ("01-intake,02-build", "must be a list"),
        ([], "empty"),
        (["01-intake", "02 build/extra"], "not a slug"),
    ]
    for i, (value, needle) in enumerate(cases):
        target = tmp / f"bad-stages-{i}"
        proc = apply_to(target, {**SLOTS, "stages": value})
        err = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            fail(f"stages={value!r} must refuse")
        if needle not in err:
            fail(f"refusal for {value!r} should say {needle!r}, got {err.strip()!r}")
        if target.exists():
            fail(f"refusal for {value!r} must not create {target}")
    print("bad stages refuse OK")


def seed_existing_repo(target: Path) -> None:
    (target / "src").mkdir(parents=True)
    (target / "src" / "app.py").write_text("print('live app')\n", encoding="utf-8")
    (target / "AGENTS.md").write_text(
        "# My app\n\nRun `make dev`. Do not touch generated clients.\n", encoding="utf-8"
    )
    (target / "README.md").write_text("# My app\n\nAn app that already exists.\n", encoding="utf-8")
    (target / ".gitignore").write_text("node_modules/\n", encoding="utf-8")


def prove_brownfield_overlay(tmp: Path) -> None:
    target = tmp / "existing-repo"
    seed_existing_repo(target)
    src_before = tree_digest(target / "src")
    readme_before = (target / "README.md").read_text(encoding="utf-8")
    gitignore_before = (target / ".gitignore").read_text(encoding="utf-8")

    payload = {
        **SLOTS,
        "mode": "overlay",
        "project_type": "internal tool",
        "stages": ["01-map", "02-contracts", "03-migrate"],
        "spec_problem": "Nobody can tell which parts of this app are still owned.",
    }
    for run in (1, 2):
        proc = apply_to(target, payload)
        if proc.returncode != 0:
            fail(f"overlay run {run} should succeed: {proc.stdout}{proc.stderr}")

    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    if not agents.startswith("# My app"):
        fail("overlay must keep the repo's own AGENTS.md text")
    if "make dev" not in agents:
        fail("overlay must not drop existing AGENTS.md content")
    if agents.count("<!-- forge-icm:start -->") != 1:
        fail("overlay must leave exactly one ICM pointer block")
    if "internal tool" not in agents:
        fail("pointer block should name the inferred project type")
    if "CONTEXT.md" not in agents:
        fail("pointer block should route the agent to CONTEXT.md")

    if tree_digest(target / "src") != src_before:
        fail("overlay must not touch src/")
    if (target / "README.md").read_text(encoding="utf-8") != readme_before:
        fail("overlay must not overwrite an existing README.md")
    if (target / ".gitignore").read_text(encoding="utf-8") != gitignore_before:
        fail("overlay must not overwrite an existing .gitignore")

    if stage_names(target) != sorted(["01-map", "02-contracts", "03-migrate"]):
        fail("overlay should still lay the interview's stages")
    if not (target / "docs" / "spec.md").is_file():
        fail("overlay always writes a spec")
    print("brownfield overlay OK")


def prove_greenfield_spec(tmp: Path) -> None:
    target = tmp / "greenfield-spec"
    problem = "Home bakers have nowhere to hear how small bakeries actually run."
    payload = {
        **SLOTS,
        "project_type": "podcast launch",
        "stages": PODCAST_STAGES,
        "write_spec": True,
        "spec_problem": problem,
    }
    proc = apply_to(target, payload)
    if proc.returncode != 0:
        fail(f"greenfield spec apply should succeed: {proc.stdout}{proc.stderr}")

    spec_path = target / "docs" / "spec.md"
    if not spec_path.is_file():
        fail("greenfield with write_spec should write docs/spec.md")
    spec = spec_path.read_text(encoding="utf-8")
    if problem not in spec:
        fail("spec should carry the continued-interview problem")
    if not spec.startswith("# podcast launch"):
        fail("spec should be titled with the inferred project type, not the folder name")
    if "- Product type: podcast launch" not in spec:
        fail("spec scope should name the inferred project type")
    for slot in ("what", "who", "done", "constraints"):
        if SLOTS[slot] not in spec:
            fail(f"spec should carry the {slot} answer")

    bare = tmp / "greenfield-nospec"
    proc = apply_to(bare, {**SLOTS, "project_type": "podcast launch"})
    if proc.returncode != 0:
        fail(f"greenfield without a spec request should succeed: {proc.stderr}")
    if (bare / "docs" / "spec.md").exists():
        fail("greenfield writes a spec only when asked")
    print("greenfield spec OK")


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="forge-issue1-"))
    try:
        print("=== issue 1 flow 1: greenfield shaped by project type ===")
        prove_type_shaped_greenfield(tmp)
        prove_stage_fallback(tmp)
        prove_bad_stages_refuse(tmp)
        print("=== issue 1 flow 2: brownfield to ICM ===")
        prove_brownfield_overlay(tmp)
        print("=== issue 1 flow 3: greenfield continued into a spec ===")
        prove_greenfield_spec(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nISSUE 1 PROVE PASS — three flows: type-shaped greenfield, brownfield overlay, spec")


if __name__ == "__main__":
    main()
