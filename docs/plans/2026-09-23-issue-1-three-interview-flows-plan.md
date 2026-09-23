---
title: Issue 1 — three interview flows end to end - Plan
type: feat
date: 2026-09-23
---

# Issue 1 — three interview flows end to end - Plan

## Goal Capsule

- Objective: someone who answers `/forge-interview` gets a workspace they can immediately work in — a greenfield binder whose stages match the kind of project they described, an existing repo that gains an ICM layer its agent will actually find, and a spec they can hand to someone else.
- Means: carry the interviewing agent's inferred type and invented stage list through `setup/answers.json` into generation, and make overlay attach the ICM layer to an existing `AGENTS.md` instead of leaving it orphaned (KTD1, KTD2).
- Authority: `AGENTS.md` (repo root) governs Forge contracts — generate from answers, never copytree a source-of-truth tree, no silent stack defaults. `skills/forge-interview/SKILL.md` governs interview behavior.
- Stop conditions: stop before inventing a project-type menu, a per-type stage table baked into the generator, or any feature build inside a generated workspace.
- Finishes and ships: `ce-work`, then the LFG pipeline through PR.

---

## Product Contract

### Summary

GitHub issue 1 asks for three interview flows: greenfield shaped by project type, brownfield converted to ICM, and greenfield continued into a spec. Two of the three already work after PR 3 and PR 4. This plan closes the two real gaps — generation ignores the type the interview inferred, and an overlay into a repo that already has `AGENTS.md` leaves the ICM layer unreferenced — and proves all three flows with a runnable check plus two live runs.

### Problem Frame

FM-606 made the interview domain-agnostic and told the agent to infer project type privately rather than serve a menu. Nothing carries that inference into the deliverable: `apply_icm_base.py` generates generic workspaces from the hardcoded CLI default `01-intake,02-discovery,03-build,04-review`, so a kitchen remodel, a podcast launch, and a research review all get the same four stages. The binder is technically ICM and practically generic.

Overlay has the mirror problem. `generate_generic_base` and `generate_website_base` pass `clobber=False` in overlay mode, which correctly protects an existing `AGENTS.md` — and therefore writes `CONTEXT.md`, `workflow-map.md`, and `stages/` into a repo whose agent entry point never mentions them. The maintainer closed PR 3 with "this PR does not close issue 1"; these two gaps plus missing proof are what is left.

### Key Decisions

- **Stages come from the interview, not from a type table.** Governs R1, R2. A table mapping `project_type` to stages would reintroduce the fixed spine FM-606 deleted; the interviewing agent already knows the shape and can name it.
- **Overlay augments an existing `AGENTS.md`; it never replaces one.** Governs R5, R7. PR 3 settled that an overlay leaves the live tree alone, and that decision stands — the fix is additive.

### Requirements

Type-shaped greenfield generation:

- R1. When `setup/answers.json` carries a `stages` list, the generated generic workspace has exactly those stages, in that order, and no others.
- R2. When answers carry no `stages`, generation keeps today's four-stage generic spine, so an interview that never got to stage shape still produces a working binder.
- R3. A `project_type` in answers appears in the generated `CONTEXT.md` and `setup/project-brief.md`, so a later agent reads the type the interview inferred rather than re-guessing it.
- R4. A malformed `stages` value — not a list, an empty list, or an entry that is not a slug — refuses with a message naming the bad value, and writes nothing.

Brownfield overlay:

- R5. Overlaying into a repo that already has `AGENTS.md` leaves the original text intact and appends one ICM pointer block naming `CONTEXT.md` and the stages directory.
- R6. Overlaying twice leaves exactly one pointer block.
- R7. Overlay never writes into `src/`, and never overwrites an existing `README.md`, `CONTEXT.md`, or `.gitignore`.

Spec continuation:

- R8. A greenfield run with `write_spec` and `spec_problem` writes `docs/spec.md` in the target carrying the problem, the four interview slots, and the answers payload.

### Scope Boundaries

In scope: `skills/forge-interview/apply_icm_base.py`, `skills/forge-interview/SKILL.md`, a proof script, and DOX updates.

Out of scope: a Matt Pocock plugin port, frontier grill rounds, typed packs beyond the existing website pack, the experience-level gate, and any feature build inside a generated workspace.

### Acceptance Examples

- AE1. Covers R1, R3. Given answers with `project_type: "podcast launch"` and `stages: ["01-format", "02-guests", "03-record", "04-publish", "05-distribute"]`, when generic apply runs, then `stages/` holds exactly those five directories and `CONTEXT.md` names the podcast launch type.
- AE2. Covers R5, R6, R7. Given a target repo with `AGENTS.md` reading `# My app` and a populated `src/`, when overlay apply runs twice, then `AGENTS.md` still opens with `# My app`, contains one pointer block, and `src/` is byte-identical to before.
- AE3. Covers R4. Given answers with `stages: "01-intake,02-build"` (a string, not a list), when apply runs, then it exits non-zero naming the value and the target directory is not created.

---

## Planning Contract

### Key Technical Decisions

- KTD1. Resolve stages inside `apply_icm_base.py` as answers `stages` first, then the `--generic-stages` CLI value. The CLI flag keeps its current default so existing callers and `prove_fm606.py` are unaffected. Chosen over making `--generic-stages` required, which would break every current caller for no gain.
- KTD2. Append the overlay pointer between HTML comment markers (`<!-- forge-icm:start -->` / `<!-- forge-icm:end -->`) and rewrite the block when the markers are already present. Marker-guarded replacement is the smallest idempotent edit and survives the user editing prose around it. Chosen over appending unconditionally (duplicates on re-run) and over a separate `ICM.md` (another file the agent must be told to read).
- KTD3. Validate `stages` with the same slug shape the generator already assumes — lowercase alphanumerics and dashes — and refuse before `target.mkdir`, so a bad run leaves no partial tree. Chosen over silently coercing bad input, which would hide interview mistakes in the binder.
- KTD4. Prove the three flows with one `prove_issue1.py` in the skill directory, matching the existing `prove_fm325.py` / `prove_fm606.py` convention. Chosen over adding a test framework the repo does not have.

### Assumptions

- The interviewing agent, not the generator, names the stages; the generator's job is to lay exactly what it is given. Nothing in the repo infers project type in Python today and this plan does not add that.
- `~/Developer/ForgeTESTS/one` and `~/Developer/ForgeTESTS/two` are throwaway verification targets outside the Forge repo and are never committed.

---

## Implementation Units

### U1. Answers-driven, type-shaped generic stages

- Goal: the generated binder matches the project the interview described.
- Requirements: R1, R2, R3, R4.
- Files: `skills/forge-interview/apply_icm_base.py`.
- Approach: add a stage resolver that reads `answers["stages"]`, validates each entry as a slug per KTD3, and falls back to the parsed `--generic-stages` value. Call it before `generate_generic_base` and refuse via the existing `die` helper ahead of any directory creation. Thread `project_type` into `generate_generic_base`'s `CONTEXT.md` body and into `render_project_brief`.
- Test Scenarios: five invented stages land verbatim; absent `stages` yields the current four; `project_type` appears in both generated files; a string `stages`, an empty list, and an entry containing a slash each refuse without creating the target.
- Verification: `python3 skills/forge-interview/prove_issue1.py` and `python3 skills/forge-interview/prove_fm606.py`.

### U2. Overlay attaches the ICM layer to an existing AGENTS.md

- Goal: an existing repo's agent finds the ICM binder that was just added to it.
- Requirements: R5, R6, R7.
- Files: `skills/forge-interview/apply_icm_base.py`.
- Approach: add a marker-guarded append that runs only when `is_overlay(answers)` and `AGENTS.md` already exists; replace the block between markers when present, otherwise append it to the end of the file. The block names `CONTEXT.md`, `stages/`, and `setup/answers.json`, and states that the live application tree is not ICM's to edit. Leave the existing `clobber=False` paths alone.
- Test Scenarios: existing heading survives; one block after two runs; block content refreshes when answers change; `src/` untouched; existing `README.md` and `.gitignore` unchanged.
- Verification: `python3 skills/forge-interview/prove_issue1.py`.

### U3. Proof script and documentation

- Goal: the three flows in issue 1 have a runnable check, and the repo's contracts describe what the generator now does.
- Requirements: R1 through R8.
- Files: `skills/forge-interview/prove_issue1.py`, `skills/forge-interview/SKILL.md`, `skills/forge-interview/AGENTS.md`, `AGENTS.md`.
- Approach: `prove_issue1.py` drives `apply_icm_base.py` as a subprocess against temporary targets, one function per flow, following `prove_fm606.py`'s structure. In `SKILL.md`, state in the apply section that the agent records the inferred type and the stage list it invented into answers before running generate, and that overlay attaches the pointer block. Update the two `AGENTS.md` files where the generation contract is described.
- Test Scenarios: the script exits zero on a correct tree and non-zero when a flow regresses.
- Verification: run the script; run `prove_fm606.py` and `prove_fm325.py` to confirm no regression.

---

## Verification Contract

- `python3 skills/forge-interview/prove_issue1.py` — the three issue-1 flows.
- `python3 skills/forge-interview/prove_fm606.py` — adaptive grill and generic apply gate unchanged.
- `python3 skills/forge-interview/prove_fm325.py` — website pack gate unchanged.
- Live end-to-end, requested by the user: two runs of differing project type, generated into `~/Developer/ForgeTESTS/one` and `~/Developer/ForgeTESTS/two`, one greenfield with a continued-interview spec and one brownfield overlay onto a repo that already has `AGENTS.md` and `src/`. Inspect both trees and report what each contains.

## Definition of Done

- R1 through R8 hold, demonstrated by the proof script.
- The two live runs exist under `~/Developer/ForgeTESTS/` and their contents are reported.
- `SKILL.md` and both `AGENTS.md` files describe the current generation contract; no stale text about a fixed generic stage list remains.
- No experimental or dead-end code left in the diff, and nothing from `~/Developer/ForgeTESTS/` committed.
- GitHub issue 1 is referenced from the PR with the evidence for each of its three flows.
