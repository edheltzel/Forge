#!/usr/bin/env python3
"""FM-606 adaptive grill — invent-and-branch machine gate.

Domain-agnostic. Four enough-slots. No fixed Q spine. Suggestions only when asked.
Pack floors are a documented hook; day one uses the generic floor only.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

SLOTS: tuple[str, ...] = ("what", "who", "done", "constraints")
MAX_INVENT_ROUNDS = 12

OPENER = "What are you trying to make or figure out?"
READY_PROMPT = (
    "Are you ready for us to structure this project, or is there anything else you want to add?"
)

PLAIN: dict[str, str] = {
    "what": "what you're trying to make or figure out",
    "who": "who it's for",
    "done": "what must be true before you'd call this done",
    "constraints": "must-haves or must-avoids",
}

# Default phrasing for the machine. The interviewing agent may reword, but must
# aim at the same empty slot (not a numbered product spine).
QUESTIONS: dict[str, str] = {
    "what": "What are you trying to make or figure out?",
    "who": "Who is this for?",
    "done": "What has to be true before you'd call this done?",
    "constraints": (
        "Anything you must have or must avoid? If nothing yet, say none known yet."
    ),
}

# Ask-only. Ground in industry practice. Never a forced pick / always-recommend.
SUGGESTIONS: dict[str, str] = {
    "what": (
        "Industry practice: name the outcome in one sentence "
        "(a site, a brand system, a research memo, a remodel plan) — not a stack."
    ),
    "who": (
        "Industry practice: name the primary beneficiary "
        "(self, household, client, team, public)."
    ),
    "done": (
        "Industry practice: a finish line you can check "
        "(artifact in hand, live URL, signed-off plan) rather than a feeling."
    ),
    "constraints": (
        "Industry practice: budget, tools, codes, must-avoids; "
        'if none are known, say "none known yet".'
    ),
}


def trim(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def slot_filled(value: object) -> bool:
    return bool(trim(value))


def empty_slots(answers: dict | None) -> list[str]:
    src = answers or {}
    return [k for k in SLOTS if not slot_filled(src.get(k))]


def gap_check(answers: dict | None) -> dict:
    empty = empty_slots(answers)
    return {"pass": len(empty) == 0, "empty": empty}


def first_empty_slot(answers: dict | None) -> str | None:
    empty = empty_slots(answers)
    return empty[0] if empty else None


def invent_question(slot: str) -> str:
    if slot not in QUESTIONS:
        raise KeyError(f"unknown slot {slot!r}")
    return QUESTIONS[slot]


def plain_empty(empty: list[str]) -> str:
    return ", ".join(PLAIN[s] for s in empty)


def is_ready(answers: dict | None) -> bool:
    src = answers or {}
    val = src.get("ready", src.get("ready_yes"))
    if val is True:
        return True
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "y", "ready"}
    return False


def enough_to_structure(answers: dict | None) -> bool:
    """Interview done = gap pass ∧ ready yes. Ready-yes alone is not enough."""
    return bool(gap_check(answers)["pass"]) and is_ready(answers)


def structure_refusal(answers: dict | None) -> str | None:
    """None when binder may be laid. Else a refuse message naming empty slots."""
    empty = empty_slots(answers)
    if empty:
        nxt = invent_question(empty[0])
        return (
            "Refuse structure. Still need: "
            f"{plain_empty(empty)}. "
            "Ready-yes alone does not lay the binder. "
            f"Next: {nxt}"
        )
    if not is_ready(answers):
        return (
            "Refuse structure. Enough-slots are filled, but the ready gate is not yes. "
            f"Next: {READY_PROMPT}"
        )
    return None


@dataclass
class Action:
    kind: str
    question: str | None = None
    slot: str | None = None
    empty: list[str] = field(default_factory=list)
    allow_structure: bool = False
    message: str = ""
    standards_only: bool = False
    invent_rounds: int = 0
    at_cap: bool = False

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "question": self.question,
            "slot": self.slot,
            "empty": list(self.empty),
            "allow_structure": self.allow_structure,
            "message": self.message,
            "standards_only": self.standards_only,
            "invent_rounds": self.invent_rounds,
            "at_cap": self.at_cap,
        }


@dataclass
class GrillState:
    opener_done: bool = False
    invent_rounds: int = 0
    slots: dict[str, str] = field(default_factory=lambda: {k: "" for k in SLOTS})
    notes: list[str] = field(default_factory=list)
    ready_yes: bool = False

    def as_answers(self) -> dict:
        out = {k: self.slots.get(k, "") for k in SLOTS}
        if self.notes:
            out["notes"] = list(self.notes)
        if self.ready_yes:
            out["ready"] = True
        return out


def _fill(state: GrillState, slot: str, value: str) -> None:
    if slot not in SLOTS:
        raise KeyError(f"unknown slot {slot!r}")
    state.slots[slot] = trim(value)


def _at_cap(state: GrillState) -> bool:
    return state.invent_rounds >= MAX_INVENT_ROUNDS


def _question_for_empty(state: GrillState) -> Action:
    """Invent (or cap-chase) a question for the first empty enough-slot."""
    empty = empty_slots(state.slots)
    slot = empty[0]
    question = invent_question(slot)
    at_cap = _at_cap(state)
    if at_cap:
        filled = [k for k in SLOTS if slot_filled(state.slots.get(k))]
        filled_plain = ", ".join(PLAIN[k] for k in filled) or "(nothing yet)"
        return Action(
            kind="cap_chase",
            question=question,
            slot=slot,
            empty=empty,
            allow_structure=False,
            invent_rounds=state.invent_rounds,
            at_cap=True,
            message=(
                f"Round cap ({MAX_INVENT_ROUNDS}) hit. Filled: {filled_plain}. "
                f"Still need: {plain_empty(empty)}. "
                "Only empty enough-slots from here — no new soft gaps."
            ),
        )
    state.invent_rounds += 1
    return Action(
        kind="invent",
        question=question,
        slot=slot,
        empty=empty,
        allow_structure=False,
        invent_rounds=state.invent_rounds,
        at_cap=False,
    )


def _after_slots(state: GrillState) -> Action:
    empty = empty_slots(state.slots)
    if not empty:
        return Action(
            kind="ready",
            question=READY_PROMPT,
            empty=[],
            allow_structure=False,
            invent_rounds=state.invent_rounds,
            at_cap=_at_cap(state),
            message="Gap check passed. Offer the ready gate. Do not lay the binder yet.",
        )
    return _question_for_empty(state)


def step(
    state: GrillState,
    event: str,
    *,
    slot: str | None = None,
    value: str | None = None,
) -> Action:
    """Advance the grill. One event → one action. Ready-yes does not waive gaps."""
    event = (event or "").strip().lower()

    if event == "start":
        return Action(
            kind="opener",
            question=OPENER,
            slot="what",
            empty=list(SLOTS),
            invent_rounds=0,
            at_cap=False,
        )

    if event == "suggest":
        target = slot or first_empty_slot(state.slots) or "what"
        return Action(
            kind="suggest",
            question=invent_question(target) if first_empty_slot(state.slots) else READY_PROMPT,
            slot=target,
            empty=empty_slots(state.slots),
            allow_structure=False,
            standards_only=True,
            invent_rounds=state.invent_rounds,
            at_cap=_at_cap(state),
            message=SUGGESTIONS[target],
        )

    if event == "add_more":
        note = trim(value)
        if note:
            state.notes.append(note)
        state.ready_yes = False
        return _after_slots(state)

    if event == "answer":
        text = trim(value)
        if not state.opener_done:
            state.opener_done = True
            if text:
                _fill(state, "what", text)
            return _after_slots(state)
        target = slot or first_empty_slot(state.slots)
        if target and text:
            _fill(state, target, text)
        return _after_slots(state)

    if event == "ready":
        empty = empty_slots(state.slots)
        if empty:
            state.ready_yes = False
            follow = _question_for_empty(state)
            follow.kind = "refuse"
            follow.allow_structure = False
            follow.message = structure_refusal(state.as_answers()) or follow.message
            return follow
        state.ready_yes = True
        return Action(
            kind="structure",
            question=None,
            empty=[],
            allow_structure=True,
            invent_rounds=state.invent_rounds,
            at_cap=_at_cap(state),
            message="Gap check passed and ready yes. Lay the thin generic ICM skeleton.",
        )

    raise ValueError(
        f"unknown event {event!r}; use start|answer|ready|add_more|suggest"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slots-json", default="{}", help="JSON object with what/who/done/constraints")
    p.add_argument("--invent-rounds", type=int, default=0)
    p.add_argument("--opener-done", action="store_true")
    p.add_argument(
        "--event",
        default="start",
        choices=("start", "answer", "ready", "add_more", "suggest"),
    )
    p.add_argument("--slot", choices=SLOTS, default=None)
    p.add_argument("--value", default=None)
    p.add_argument(
        "--check",
        action="store_true",
        help="Print gap_check + enough_to_structure for --slots-json (ignores --event).",
    )
    args = p.parse_args()
    slots = json.loads(args.slots_json)
    if args.check:
        answers = {k: slots.get(k, "") for k in SLOTS}
        if "ready" in slots:
            answers["ready"] = slots["ready"]
        gap = gap_check(answers)
        refusal = structure_refusal(answers)
        print(
            json.dumps(
                {
                    "gap_pass": gap["pass"],
                    "empty": gap["empty"],
                    "empty_plain": plain_empty(gap["empty"]),
                    "ready": is_ready(answers),
                    "enough_to_structure": enough_to_structure(answers),
                    "refusal": refusal,
                },
                indent=2,
            )
        )
        raise SystemExit(0 if enough_to_structure(answers) else 2)

    state = GrillState(
        opener_done=args.opener_done or any(slot_filled(slots.get(k)) for k in SLOTS),
        invent_rounds=args.invent_rounds,
        slots={k: trim(slots.get(k, "")) for k in SLOTS},
    )
    action = step(state, args.event, slot=args.slot, value=args.value)
    payload = action.as_dict()
    payload["slots"] = state.as_answers()
    print(json.dumps(payload, indent=2))
    if action.kind == "refuse" or (
        action.kind in {"invent", "cap_chase", "opener", "ready", "suggest"}
        and not action.allow_structure
    ):
        # Non-zero only when they asked to structure and were refused.
        if action.kind == "refuse":
            raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
