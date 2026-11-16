#!/usr/bin/env python3
"""Change 0 prove: today's generic apply output, frozen byte for byte.

Copies fixtures/sample-project into a temp folder ("existing"), makes an empty
temp folder ("new"), points HOME at an empty temp folder, and runs
apply_icm_base.py --product generic --answers fixtures/snapshot-answers.json on
both, then applies again on the same already-applied folders with the same
temp HOME; the second apply must leave every file byte-identical. The output
must match fixtures/snapshots/before/MANIFEST.json and the stored files byte
for byte, and a fresh-folder rerun must match too. Fails if anything lands in
the temp HOME.

--update --reason "<why>" writes the current output to snapshots/after/.
It never touches snapshots/before/.
"""
from __future__ import annotations

import argparse
import hashlib
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
FIXTURES = DIR / "fixtures"
SAMPLE = FIXTURES / "sample-project"
ANSWERS = FIXTURES / "snapshot-answers.json"
SNAPSHOTS = FIXTURES / "snapshots"
BEFORE = SNAPSHOTS / "before"
AFTER = SNAPSHOTS / "after"
TARGETS = ("existing", "new")


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect(root: Path, prefix: str) -> dict[str, bytes]:
    return {
        f"{prefix}/{p.relative_to(root).as_posix()}": p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def apply_to(target: Path, home: Path) -> None:
    env = {**os.environ, "HOME": str(home)}
    proc = subprocess.run(
        [
            sys.executable,
            str(APPLY),
            "--target",
            str(target),
            "--product",
            "generic",
            "--answers",
            str(ANSWERS),
        ],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"apply on {target.name} exited {proc.returncode}: {proc.stderr or proc.stdout}")
    left = sorted(p.name for p in home.iterdir())
    if left:
        fail(f"apply on {target.name} wrote into temp HOME: {left}")


def run_once() -> dict[str, bytes]:
    for need in (SAMPLE, ANSWERS):
        if not need.exists():
            fail(f"missing fixture {need.relative_to(DIR)}")
    with tempfile.TemporaryDirectory(prefix="forge-snapshot-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        home.mkdir()
        shutil.copytree(SAMPLE, tmp / "existing")
        (tmp / "new").mkdir()
        produced: dict[str, bytes] = {}
        for name in TARGETS:
            apply_to(tmp / name, home)
            produced.update(collect(tmp / name, name))
        again: dict[str, bytes] = {}
        for name in TARGETS:
            apply_to(tmp / name, home)
            again.update(collect(tmp / name, name))
        if again != produced:
            diff = sorted(k for k in set(produced) | set(again) if produced.get(k) != again.get(k))
            fail(f"second apply on the same folders is not idempotent: {diff}")
        return produced


def compare(produced: dict[str, bytes], snap: Path, label: str) -> None:
    manifest_path = snap / "MANIFEST.json"
    if not manifest_path.is_file():
        fail(f"missing {manifest_path.relative_to(DIR)}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("source_forge_commit"):
        fail("manifest has no source_forge_commit")
    expected = {f["path"]: f["sha256"] for f in manifest["files"]}
    stored = {k: v for k, v in collect(snap, "").items() if k != "/MANIFEST.json"}
    stored = {k[1:]: v for k, v in stored.items()}
    if set(stored) != set(expected):
        fail(f"{snap.name}/ files differ from its manifest: {sorted(set(stored) ^ set(expected))}")
    missing = sorted(set(expected) - set(produced))
    extra = sorted(set(produced) - set(expected))
    if missing or extra:
        fail(f"{label}: missing {missing} extra {extra}")
    for path, digest in sorted(expected.items()):
        if sha256(stored[path]) != digest:
            fail(f"{snap.name}/{path} does not match its manifest hash")
        if produced[path] != stored[path] or sha256(produced[path]) != digest:
            fail(f"{label}: {path} differs from {snap.name}/ byte for byte")


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path, data in sorted(collect(root, "").items()):
        h.update(path.encode())
        h.update(data)
    return h.hexdigest()


def source_commit() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True, check=False
    )
    return proc.stdout.strip() or "unknown"


def write_snapshot(dest: Path, produced: dict[str, bytes], commit: str, reason: str) -> None:
    if dest.resolve() == BEFORE.resolve() and dest.exists():
        fail("refusing to overwrite snapshots/before/")
    if dest.exists():
        shutil.rmtree(dest)
    for path, data in produced.items():
        out = dest / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    manifest = {
        "source_forge_commit": commit,
        "reason": reason,
        "answers": ANSWERS.relative_to(DIR).as_posix(),
        "files": [{"path": p, "sha256": sha256(d)} for p, d in sorted(produced.items())],
    }
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--update", action="store_true", help="write current output to snapshots/after/")
    p.add_argument("--reason", help="required with --update")
    args = p.parse_args()
    if args.update and not (args.reason or "").strip():
        p.error("--update needs --reason")

    first = run_once()
    second = run_once()
    if first != second:
        diff = sorted(k for k in set(first) | set(second) if first.get(k) != second.get(k))
        fail(f"rerun differs from first run: {diff}")

    if args.update:
        before_digest = tree_digest(BEFORE) if BEFORE.exists() else None
        write_snapshot(AFTER, first, source_commit(), args.reason.strip())
        after_digest = tree_digest(BEFORE) if BEFORE.exists() else None
        if before_digest != after_digest:
            fail("snapshots/before/ changed during --update")
        print(f"updated snapshots/after/ ({len(first)} files); snapshots/before/ untouched")
        return

    compare(first, BEFORE, "run 1")
    compare(second, BEFORE, "run 2")
    print(f"PASS: prove_snapshot ({len(first)} files; same-folder reapply idempotent; fresh rerun identical; temp HOME empty)")


if __name__ == "__main__":
    main()
