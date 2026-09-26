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
- Overlay reads existing docs (grill-with-docs); do not replace `src/`. Both modes keep an existing root `AGENTS.md` and add one marker-guarded pointer (`<!-- forge-icm:start -->`) aimed at `forge/`. If root `AGENTS.md` is missing, apply writes a thin one. Apply writes `docs/spec.md` unless they said no (`write_spec` or `spec` false). The pointer is written to `AGENTS.md`, not into `CONTEXT.md`. It names `docs/spec.md` only when that file is written, names Forge `specs/<slug>.md` when `spec_dest` is `forge`, and omits the spec line when they said no.
- The binder's shape comes from the interview: `project_type` and a `stages` slug list in answers, laid verbatim. No type-to-stages table in the generator. Absent `stages` falls back to the generic four; a non-list, empty, or non-slug `stages` refuses before anything is written.
- Generic apply refuses unless gap check passes and `ready` is yes. Persist slots in `forge/setup/answers.json` + `forge/setup/project-brief.md`. `--target` stays the project root.

## Work Guidance

- One question at a time. Their words on the page; map to slots behind the scenes.
- Infer project type privately. Do not force software menus.
- Do not invent weight training or self-learning marketing.

## Verification

- `python3 skills/forge-interview/grill.py --help`
- `python3 skills/forge-interview/apply_icm_base.py --help`
- `python3 skills/forge-interview/prove_fm606.py`
- `python3 skills/forge-interview/prove_fm325.py` (website apply / pack pointer — later typed pack, not the day-one grill)
- `python3 skills/forge-interview/prove_issue1.py` (issue 1: type-shaped greenfield, brownfield overlay, spec)

## Child DOX Index

- packs/AGENTS.md — versioned domain pack contract (later hook)

