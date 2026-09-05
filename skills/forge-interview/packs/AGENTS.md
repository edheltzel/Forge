# packs (forge-interview)

## Purpose

Versioned **domain packs** that select interview vocabulary and probe depth for `/forge-interview`. Packs are session experts only.

## Ownership

Owned by `skills/forge-interview`. Parent: `skills/AGENTS.md`.

## Local Contracts

- Pack path shape: `packs/<domain>/<version>.yaml` (example: `website/v1.yaml`).
- Required fields: `id`, `version`, `domain`, `core_slots`, `levels`.
- Levels are integers **0–5**. v1 ships **every** of `"0"`..`"5"` explicitly (no clamp to endpoints):
  - **0–2**: plain vocab / shallow / `probes: []`
  - **3–4**: expert vocab / deep phrasing / `probes: []` (no L5 deep probe slots)
  - **5**: expert vocab / deep / full L5 probes list
- Persist HIL `experience_level` as the raw integer; resolve vocab/depth/probes from `levels["N"]` for that N.
- **Session expert** = read the selected pack level entry into the interview session. Phrase questions and optional probes by that entry. Same ICM core slots at every level.
- **Never** dump pack body into the target workspace. Apply may write a pointer only (`setup/session-expert.md` with id / version / level).
- HIL answers still fill ICM (`setup/answers.json`, `setup/client.md`). Packs do not invent weight training or self-learning marketing.
- Website product shape only in v1. Generic ICM skips the 0–5 gate.

## Work Guidance

- Edit pack YAML when vocabulary or probe lists change; bump `version` when contracts change incompatibly.
- Keep core_slots stable across levels; probes are additive at higher levels.

## Verification

- Fixtures: `skills/forge-interview/fixtures/answers-L0.json`, `answers-L5.json`, `expected-probes-L0.txt`, `expected-probes-L5.txt`.
- Prove: `python3 skills/forge-interview/prove_fm325.py` (or apply_icm_base with L0/L5 fixtures).

## Child DOX Index

- (none — YAML packs only)
