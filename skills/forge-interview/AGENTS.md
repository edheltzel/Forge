# forge-interview

## Purpose

ICM-first interview skill for `/forge-interview`. Capture answers, generate ICM BASE from answers (no SoT copytree).

## Ownership

Parent: `skills/AGENTS.md`. Apply helper: `apply_icm_base.py`.

## Local Contracts

- After product shape = **website**, ask experience gate **0–5** (integer only) before intake Q1. Skip gate for **generic** in v1.
- 0–5 selects versioned domain pack + probe depth + vocabulary (`packs/website/v1.yaml`).
- Load selected pack as **session expert** (read into session). Never dump pack body into the target.
- HIL answers fill ICM. Same core ICM slots at every level; higher levels add probes only.
- No template dump / no copytree of workbench. Generate via mkdir + write.
- Persist `experience_level`, `pack_id`, `pack_version` in `setup/answers.json`. Optional `setup/session-expert.md` pointer (id/version/level only).

## Work Guidance

- Phrase intake by pack level vocab. L0 = plain / shallow (core 8). L5 = expert terms + deep probes.
- Do not invent weight training or self-learning marketing.

## Verification

- `python3 skills/forge-interview/apply_icm_base.py --help`
- `python3 skills/forge-interview/prove_fm325.py`

## Child DOX Index

- packs/AGENTS.md — versioned domain pack contract
