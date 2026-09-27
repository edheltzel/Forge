#!/usr/bin/env python3
"""FM-606 prove: adaptive grill gap check, refuse-on-ready, 12-round cap, ask-only suggest."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
if str(DIR) not in sys.path:
    sys.path.insert(0, str(DIR))
import grill  # noqa: E402

APPLY = DIR / "apply_icm_base.py"
SKILL = DIR / "SKILL.md"
GENERIC_OK = {
    "what": "Kitchen remodel plan for the back of the house",
    "who": "Our household — two adults, one kid",
    "done": "Signed contractor packet and a room that passes inspection",
    "constraints": "Keep the existing plumbing wall; no open-plan",
    "ready": True,
}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def run_apply(target: Path, product: str, payload: dict) -> subprocess.CompletedProcess:
    if target.exists():
        shutil.rmtree(target)
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


def prove_gap_check() -> None:
    g = grill.gap_check({})
    if g["pass"] or g["empty"] != list(grill.SLOTS):
        fail(f"empty answers should fail all four, got {g}")
    g = grill.gap_check({"what": "  ", "who": "us", "done": "ship", "constraints": "none known yet"})
    if g["pass"] or g["empty"] != ["what"]:
        fail(f"whitespace what should be empty, got {g}")
    g = grill.gap_check(
        {
            "what": "a brand system",
            "who": "the client",
            "done": "guidelines in hand",
            "constraints": "none known yet",
        }
    )
    if not g["pass"] or g["empty"]:
        fail(f"four filled slots should pass, got {g}")
    if grill.enough_to_structure(
        {
            "what": "a",
            "who": "b",
            "done": "c",
            "constraints": "d",
        }
    ):
        fail("filled slots without ready must not be enough-to-structure")
    if not grill.enough_to_structure(GENERIC_OK):
        fail("four slots + ready should be enough-to-structure")
    print("gap check OK")


def prove_opener_and_invent() -> None:
    state = grill.GrillState()
    action = grill.step(state, "start")
    if action.kind != "opener" or action.question != grill.OPENER:
        fail(f"start should opener, got {action}")
    if action.invent_rounds != 0:
        fail("opener must not count as an invent round")
    action = grill.step(state, "answer", value="A research memo on local birds")
    if state.slots["what"] != "A research memo on local birds":
        fail("opener answer should fill what")
    if action.kind != "invent" or action.slot != "who":
        fail(f"next invent should target who, got {action}")
    if action.invent_rounds != 1:
        fail(f"first invent should be round 1, got {action.invent_rounds}")
    print("opener + invent OK")


def prove_ready_last() -> None:
    state = grill.GrillState()
    grill.step(state, "answer", value="DIY deck")
    grill.step(state, "answer", slot="who", value="self")
    grill.step(state, "answer", slot="done", value="cards and permit in hand")
    action = grill.step(state, "answer", slot="constraints", value="none known yet")
    if action.kind != "ready" or action.question != grill.READY_PROMPT:
        fail(f"gap pass must offer ready prompt, got {action}")
    if action.allow_structure:
        fail("ready offer must not allow structure yet")
    action = grill.step(state, "add_more", value="also want a shade sail")
    notes = " ".join(state.notes)
    if action.kind != "ready" or "shade sail" not in notes:
        fail(f"add-more should re-offer ready, got {action} notes={state.notes}")
    action = grill.step(state, "ready")
    if action.kind != "structure" or not action.allow_structure:
        fail(f"ready after gap pass should structure, got {action}")
    print("ready-last OK")


def prove_refuse_on_ready_empties() -> None:
    state = grill.GrillState(opener_done=True, slots={"what": "a podcast", "who": "", "done": "", "constraints": ""})
    action = grill.step(state, "ready")
    if action.kind != "refuse":
        fail(f"ready with empties must refuse, got {action.kind}")
    if action.allow_structure:
        fail("refuse must not allow structure")
    if action.slot != "who":
        fail(f"refuse should invent first empty (who), got {action.slot}")
    msg = action.message or ""
    for needle in ("who it's for", "what must be true", "must-haves"):
        if needle not in msg:
            fail(f"refuse should name empty slots in plain words, missing {needle!r} in {msg!r}")
    if "Ready-yes alone" not in msg:
        fail(f"refuse should say ready-yes alone is not enough: {msg!r}")
    if action.question != grill.QUESTIONS["who"]:
        fail(f"refuse should ask the first empty slot, got {action.question!r}")
    print("refuse-on-ready-empties OK")


def prove_round_cap() -> None:
    state = grill.GrillState()
    grill.step(state, "answer", value="a")  # fills what; invent 1 → who
    # Burn invent rounds with empty answers (unclear / unmapped).
    while state.invent_rounds < grill.MAX_INVENT_ROUNDS:
        action = grill.step(state, "answer", value="")
        if action.kind != "invent":
            fail(f"pre-cap should invent, round {state.invent_rounds} got {action.kind}")
    if state.invent_rounds != 12:
        fail(f"want 12 invent rounds, got {state.invent_rounds}")
    action = grill.step(state, "answer", value="")
    if action.kind != "cap_chase":
        fail(f"past cap should cap_chase, got {action.kind}")
    if action.slot not in grill.SLOTS or action.slot == "what":
        fail(f"cap chase must target an empty enough-slot, got {action.slot}")
    if "no new soft gaps" not in action.message:
        fail(f"cap chase must forbid new soft gaps: {action.message!r}")
    if action.allow_structure:
        fail("cap must not waive structure")
    # Ready at cap with empties still refuses.
    action = grill.step(state, "ready")
    if action.kind != "refuse" or action.allow_structure:
        fail(f"ready at cap with empties must refuse, got {action}")
    if not action.at_cap:
        fail("refuse at cap should flag at_cap")
    # Filling remaining slots after cap still required before ready.
    for sl, val in (
        ("who", "self"),
        ("done", "plan on paper"),
        ("constraints", "none known yet"),
    ):
        grill.step(state, "answer", slot=sl, value=val)
    action = grill.step(state, "answer", value="")
    if action.kind != "ready":
        fail(f"after filling at/past cap, offer ready, got {action}")
    action = grill.step(state, "ready")
    if not action.allow_structure:
        fail("cap does not block structure once gaps pass + ready")
    print("round cap OK")


def prove_ask_only_suggestions() -> None:
    state = grill.GrillState(opener_done=True, slots={"what": "logo", "who": "", "done": "", "constraints": ""})
    action = grill.step(state, "answer", value="")
    if action.kind == "suggest":
        fail("unsolicited answer must not suggest")
    action = grill.step(state, "suggest")
    if action.kind != "suggest" or not action.standards_only:
        fail(f"ask-suggest must be standards_only, got {action}")
    if "Industry practice" not in action.message:
        fail(f"suggestions must cite industry practice, got {action.message!r}")
    lower = action.message.lower()
    for banned in ("turbo", "nx", "vercel", "you should use"):
        if banned in lower:
            fail(f"suggestion must not always-recommend {banned!r}: {action.message!r}")
    print("ask-only suggest OK")


def prove_generic_apply_gate() -> None:
    missing = Path("/tmp/fm606-refuse-empty")
    proc = run_apply(missing, "generic", {"what": "x", "ready": True})
    err = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        fail("generic apply with empty slots must refuse")
    if "Refuse structure" not in err or "who it's for" not in err:
        fail(f"generic apply refuse should name empty slots, got {err}")
    if missing.exists() and (missing / "AGENTS.md").is_file():
        fail("refuse must not lay binder files")

    noready = Path("/tmp/fm606-refuse-noready")
    filled = {k: GENERIC_OK[k] for k in grill.SLOTS}
    proc = run_apply(noready, "generic", filled)
    err = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        fail("generic apply without ready must refuse")
    if "ready gate is not yes" not in err:
        fail(f"expected ready-gate refuse, got {err}")

    ok = Path("/tmp/fm606-generic-ok")
    proc = run_apply(ok, "generic", GENERIC_OK)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        fail(f"generic apply with four slots + ready should succeed: {out}")
    brief = (ok / "forge" / "setup" / "project-brief.md").read_text(encoding="utf-8")
    for needle in (
        "Kitchen remodel plan",
        "Our household",
        "Signed contractor packet",
        "existing plumbing wall",
    ):
        if needle not in brief:
            fail(f"brief missing {needle!r}")
    ctx = (ok / "forge" / "CONTEXT.md").read_text(encoding="utf-8")
    if "Kitchen remodel plan" not in ctx:
        fail("CONTEXT.md should fill from what")
    if (ok / "CONTEXT.md").exists() or (ok / "stages").exists():
        fail("binder files must not land at the project root")
    answers = json.loads((ok / "forge" / "setup" / "answers.json").read_text(encoding="utf-8"))
    if answers.get("what") != GENERIC_OK["what"]:
        fail("answers.json should persist slots")
    print("generic apply gate OK")


def prove_skill_retarget() -> None:
    text = SKILL.read_text(encoding="utf-8")
    if grill.READY_PROMPT not in text:
        fail("SKILL.md must include the ready-gate prompt")
    if "## 3. Ready gate" not in text:
        fail("SKILL.md must have a ready-gate section")
    section = text.split("## 3. Ready gate", 1)[1].split("\n## ", 1)[0]
    disclosure = (
        "After you say ready, you'll name the folder. "
        "The workflow goes under `forge/` there. "
        "I'll also write `docs/spec.md` unless you say you don't want one. "
        "If that file is already there, this replaces it."
    )
    quote = f"> {grill.READY_PROMPT}"
    if disclosure not in section:
        fail("ready-gate section must include the disclosure")
    if quote not in section:
        fail("ready-gate section must quote the ready prompt")
    if section.find(disclosure) > section.find(quote):
        fail("disclosure must precede the ready-question blockquote")
    example = text.split("--answers-json", 1)[-1][:160]
    if "write_spec" not in example:
        fail("interview answers example must include write_spec")
    if "Do not ask whether they want a spec" in text:
        fail("SKILL.md must not hide the spec")
    if "Invent-and-branch" not in text and "invent-and-branch" not in text:
        fail("SKILL.md must name invent-and-branch")
    if "max **12**" not in text:
        fail("SKILL.md must lock the 12-round cap")
    # Subtracted fixed spine
    for dead in (
        "Astro or Next for this client?",
        "Ask: client **website** pipe",
        "Turbo or Nx; host; data; IdP",
        "before intake Q1",
        "Core 8 (always):",
    ):
        if dead in text:
            fail(f"SKILL.md still has dead fixed-spine text: {dead!r}")
    print("skill retarget OK")


def prove_grill_cli() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(DIR / "grill.py"),
            "--slots-json",
            json.dumps({"what": "x", "ready": True}),
            "--check",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        fail("grill --check with empties should exit 2")
    data = json.loads(proc.stdout)
    if data.get("gap_pass") or "who" not in data.get("empty", []):
        fail(f"grill --check payload wrong: {data}")
    proc = subprocess.run(
        [
            sys.executable,
            str(DIR / "grill.py"),
            "--slots-json",
            json.dumps(GENERIC_OK),
            "--check",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"grill --check on full+ready should pass: {proc.stdout}{proc.stderr}")
    print("grill CLI OK")


def main() -> None:
    print("=== FM-606 prove: gap check ===")
    prove_gap_check()
    print("=== FM-606 prove: opener + invent ===")
    prove_opener_and_invent()
    print("=== FM-606 prove: ready last ===")
    prove_ready_last()
    print("=== FM-606 prove: refuse on ready with empties ===")
    prove_refuse_on_ready_empties()
    print("=== FM-606 prove: 12-round cap ===")
    prove_round_cap()
    print("=== FM-606 prove: ask-only suggestions ===")
    prove_ask_only_suggestions()
    print("=== FM-606 prove: generic apply gate ===")
    prove_generic_apply_gate()
    print("=== FM-606 prove: skill retarget ===")
    prove_skill_retarget()
    print("=== FM-606 prove: grill CLI ===")
    prove_grill_cli()
    print(
        "ASSERT OK: four-slot gap; refuse ready-yes-alone; ready last; "
        "12-round cap does not waive gaps; ask-only suggestions; "
        "generic apply lays thin skeleton only after enough; fixed spine subtracted"
    )


if __name__ == "__main__":
    main()
