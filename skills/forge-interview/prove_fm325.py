#!/usr/bin/env python3
"""FM-325 prove: L0 vs L5 apply, pack keys 0-5, pack meta, probe diff, no dump."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPLY = Path(__file__).resolve().parent / "apply_icm_base.py"
FIX = Path(__file__).resolve().parent / "fixtures"
PACK = Path(__file__).resolve().parent / "packs" / "website" / "v1.yaml"
L0_TARGET = Path("/tmp/fm325-L0")
L5_TARGET = Path("/tmp/fm325-L5")
DEEP = (
    "redirect_strategy",
    "seo_equity_notes",
    "cms_lockin_risk",
    "staging_hostname",
    "analytics_owner",
)
SPINE = (
    "AGENTS.md",
    "CONTEXT.md",
    "setup/answers.json",
    "setup/client.md",
    "stages/01-audit-ia/CONTEXT.md",
    "stages/07-cd/CONTEXT.md",
    "_config/intake-questions.md",
)


def run_apply(target: Path, answers: Path) -> str:
    if target.exists():
        shutil.rmtree(target)
    proc = subprocess.run(
        [
            sys.executable,
            str(APPLY),
            "--target",
            str(target),
            "--product",
            "website",
            "--answers",
            str(answers),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out, end="" if out.endswith("\n") else "\n")
    if proc.returncode != 0:
        raise SystemExit(f"apply failed rc={proc.returncode}")
    return out


def load_answers(target: Path) -> dict:
    return json.loads((target / "setup" / "answers.json").read_text(encoding="utf-8"))


def assert_spine(target: Path) -> None:
    for rel in SPINE:
        p = target / rel
        if not p.is_file():
            raise SystemExit(f"missing ICM spine file: {target}/{rel}")


def assert_no_dump(target: Path) -> None:
    banned_names = ("icm-website-workbench",)
    for p in target.rglob("*"):
        if any(b in p.name for b in banned_names):
            raise SystemExit(f"banned workbench marker in target: {p}")
    ptr = target / "setup" / "session-expert.md"
    if ptr.is_file():
        body = ptr.read_text(encoding="utf-8")
        if "core_slots:" in body or "phrase_hints:" in body or "probes:" in body:
            raise SystemExit("session-expert.md looks like pack body dump")
        if "pack_id:" not in body or "experience_level:" not in body:
            raise SystemExit("session-expert.md missing pointer fields")


def expected_probes(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "NONE":
            return []
        lines.append(line)
    return lines



def assert_pack_levels_0_through_5() -> None:
    """Cheap RedTeam fix: pack must define explicit keys "0".."5" (no clamp)."""
    if not PACK.is_file():
        raise SystemExit(f"missing pack: {PACK}")
    body = PACK.read_text(encoding="utf-8")
    keys = set()
    in_levels = False
    for line in body.splitlines():
        if line.strip() == "levels:":
            in_levels = True
            continue
        if in_levels:
            if line and not line[0].isspace() and ":" in line:
                break
            s = line.strip()
            if s.startswith('"') and '":' in s:
                k = s.split('":', 1)[0].strip().strip('"')
                if k.isdigit():
                    keys.add(k)
    missing = [str(i) for i in range(6) if str(i) not in keys]
    if missing:
        raise SystemExit(f"pack missing explicit level keys {missing}; found {sorted(keys)}")
    print(f"pack levels OK: {sorted(keys, key=int)}")


def main() -> None:
    print("=== FM-325 prove: pack levels 0-5 ===")
    assert_pack_levels_0_through_5()
    print("=== FM-325 prove: apply L0 ===")
    run_apply(L0_TARGET, FIX / "answers-L0.json")
    print("=== FM-325 prove: apply L5 ===")
    run_apply(L5_TARGET, FIX / "answers-L5.json")

    a0 = load_answers(L0_TARGET)
    a5 = load_answers(L5_TARGET)
    assert_spine(L0_TARGET)
    assert_spine(L5_TARGET)
    assert_no_dump(L0_TARGET)
    assert_no_dump(L5_TARGET)

    if a0.get("experience_level") != 0:
        raise SystemExit(f"L0 experience_level want 0 got {a0.get('experience_level')!r}")
    if a5.get("experience_level") != 5:
        raise SystemExit(f"L5 experience_level want 5 got {a5.get('experience_level')!r}")
    for a, label in ((a0, "L0"), (a5, "L5")):
        if a.get("pack_id") != "website" or a.get("pack_version") != "v1":
            raise SystemExit(
                f"{label} pack meta missing/wrong: {a.get('pack_id')}@{a.get('pack_version')}"
            )

    exp0 = expected_probes(FIX / "expected-probes-L0.txt")
    exp5 = expected_probes(FIX / "expected-probes-L5.txt")
    if exp0 != []:
        raise SystemExit(f"fixture expected-probes-L0 should be empty, got {exp0}")
    if exp5 != list(DEEP):
        raise SystemExit(f"fixture expected-probes-L5 mismatch: {exp5}")

    for k in DEEP:
        if k in a0 and a0.get(k) not in (None, ""):
            raise SystemExit(f"L0 should not carry deep probe {k}")
        if not a5.get(k):
            raise SystemExit(f"L5 missing deep field {k}")

    client5 = (L5_TARGET / "setup" / "client.md").read_text(encoding="utf-8")
    for label in (
        "Redirect strategy",
        "SEO equity notes",
        "CMS lock-in risk",
        "Staging hostname",
        "Analytics owner",
    ):
        if label not in client5:
            raise SystemExit(f"L5 client.md missing {label}")

    client0 = (L0_TARGET / "setup" / "client.md").read_text(encoding="utf-8")
    for label in ("Redirect strategy", "SEO equity notes"):
        if label in client0:
            raise SystemExit(f"L0 client.md should omit deep probe section {label}")

    print("=== probe list diff (L5 - L0) ===")
    print("L0 probes: (none — core 8 only)")
    print("L5 probes:")
    for k in DEEP:
        print(f"  + {k}")
    print(
        "ASSERT OK: pack keys 0-5; ICM spine both; experience_level 0 vs 5; "
        "L5 deeper fields; no workbench/pack dump"
    )


if __name__ == "__main__":
    main()
