# forge-interview

## Purpose

ICM-first interview skill for `/forge-interview`. Adaptive invent-and-branch until enough-to-structure, then generate a thin generic ICM BASE from answers (no SoT copytree). Domain-agnostic.

## Ownership

Parent: `skills/AGENTS.md`. Grill machine: `grill.py`. Apply helper: `apply_icm_base.py`.

## Local Contracts

- Invent the next question from empty enough-slots. No fixed Q1–Q5 / core-8 product spine. No project-type menu.
- Enough-to-structure (day one): **what**, **who**, **done**, **constraints** all non-empty after trim. Ready-yes alone does not lay the binder.
- Offer ready gate only after gap check passes. Exact: "Are you ready for us to structure this project, or is there anything else you want to add?"
- Max **12** invent rounds after the opener. Past cap: chase empty slots only. Cap does not waive the gap check.
- Suggestions only when the human asks; ground in industry standards. No always-recommend.
- Typed pack floors (website 0–5 included) are a **hook for later**. Day one does not load packs as the interview spine. Never dump pack body into the target.
- Software four-pack is not this interview. Optional later pack branch only if they explicitly ask.
- No template dump / no copytree of workbench. Generate via mkdir + write.
- Overlay reads existing docs (grill-with-docs); do not replace `src/`. Overlay always writes a spec. Greenfield spec only when asked.
- Generic apply refuses unless gap check passes and `ready` is yes. Persist slots in `setup/answers.json` + `setup/project-brief.md`.

## Work Guidance

- One question at a time. Their words on the page; map to slots behind the scenes.
- Infer project type privately. Do not force software menus.
- Do not invent weight training or self-learning marketing.

## Verification

- `python3 skills/forge-interview/grill.py --help`
- `python3 skills/forge-interview/apply_icm_base.py --help`
- `python3 skills/forge-interview/prove_fm606.py`
- `python3 skills/forge-interview/prove_fm325.py` (website apply / pack pointer — later typed pack, not the day-one grill)

## Child DOX Index

- packs/AGENTS.md — versioned domain pack contract (later hook)

