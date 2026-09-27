---
title: Spec Disclosure Before Ready - Plan
type: fix
date: 2026-09-27
artifact_contract: ce-unified-plan/v1
product_contract_source: ce-plan-bootstrap
depth: lightweight
---

# Spec Disclosure Before Ready - Plan

## Goal Capsule

- Objective: A person hears that a spec file will be written before they agree to structure the project, and a spoken no skips that file.
- Means: Say the default writes immediately before the existing ready question (KTD1).
- Authority: R-IDs own product behavior. KTD-IDs own the mechanism.
- Stop: Do not add a second wait after ready. Do not treat silence as a yes before the disclosure. Do not abort the interview because they never mentioned a spec.
- Execution: one pass, three units, existing prove scripts.
- Ships: the implementer, after the verification commands pass.

## Product Contract

### Summary

The interview states the `forge/` and `docs/spec.md` writes immediately before the current ready question. Ready-yes still starts the write. A spec decline is recorded before apply and skips only that file.

### Problem Frame

Today the ready question asks whether they are ready to structure the project. It does not name the files. A missing `write_spec` still writes `docs/spec.md`. A person who never hears the word spec cannot decline it, so silence becomes consent.

### Key Decisions

- KD1. Silence is not consent for the spec. (session-settled: user-directed — chosen over treating an unspoken decline as yes: the person must hear the file before ready counts as agreement) Governs R1, R4, R6.

### Requirements

- R1. Immediately before the existing ready question, the person hears that the workflow will be written under `forge/` in the folder they name, that `docs/spec.md` will be written unless they say they do not want one, and that an existing `docs/spec.md` will be replaced.
- R2. The ready question stays exactly: "Are you ready for us to structure this project, or is there anything else you want to add?"
- R3. No project files are written until they say ready and a target path is known.
- R4. A spec decline is stored as `write_spec` false in the answers before apply, including when the same utterance is also ready-yes.
- R5. A spec decline without ready-yes is kept, the ready question is asked again, and nothing is written yet.
- R6. Ready-yes after the disclosure, with no decline, writes `docs/spec.md`.
- R7. The close names the spec path or says the spec was skipped.
- R8. The interview does not stop, and does not write nothing, merely because they never mentioned a spec.

### Scope Boundaries

- In: the disclosure, the decline-before-apply rule, the human-facing docs that describe that moment, and a prove that the skill text matches R1 and R2.
- Deferred: showing the four facts during the grill, a visible suggestion offer, Cursor slash-command wiring, and preserving edited `forge/` files on a second run.
- Out: a post-ready wait that writes if they stay silent. Chat has no silence-triggered continuation, and that wait would treat silence as consent again.
- Out: aborting the interview or writing no binder when they do not mention a spec.

### Acceptance Examples

- AE1. Covers R1, R2, R6. Given the four facts are filled, when the agent offers ready, then the disclosure is spoken and the exact ready question follows. Given they say ready and do not decline, when apply runs, then `docs/spec.md` exists.
- AE2. Covers R4, R5, R7. Given they say they do not want a spec and have not said ready, when the agent continues, then nothing is written and the ready question is asked again. Given they then say ready, when apply runs, then the binder exists, `docs/spec.md` does not, and the close says the spec was skipped.
- AE3. Covers R4. Given they say ready and decline the spec in the same breath, when apply runs, then the binder exists and `docs/spec.md` does not.

## Planning Contract

### Key Technical Decisions

- KTD1. The disclosure is spoken immediately before the exact ready question, in the ready-gate section, not as a change to that question. Sentence: "After you say ready, you'll name the folder. The workflow goes under `forge/` there. I'll also write `docs/spec.md` unless you say you don't want one. If that file is already there, this replaces it." Rejected: a second question after ready that waits and then writes on silence. Chat cannot detect silence, and that step would make an unspoken yes the default again.
- KTD2. The agent copies a spec decline into the answers JSON as `write_spec` false before `apply_icm_base.py` runs. Do not add phrase matching to `grill.py`. The grill already stores slots, not speech, and a phrase list will miss ordinary paraphrases. The skill is the speech contract. `want_spec` already skips when that flag is false.
- KTD3. On the interview path, the answers passed to apply set `write_spec` true when the disclosure was spoken and they did not decline, and false when they did. A missing key still writes for a call that is not this interview. Do not change `want_spec`. Do not treat that missing-key write as the interview's consent.

### Sequencing

U1, then U2, then U3. U3 fails if U1 drops the exact ready question or places the disclosure after it.

## Implementation Units

### U1. Require the disclosure and the pre-apply flag

- Goal: The interviewing agent says KTD1 before R2, copies a decline into the answers before apply, and sets `write_spec` explicitly on the interview path.
- Requirements: R1, R2, R3, R4, R5, R8
- Files: `skills/forge-interview/SKILL.md`, `skills/forge-interview/AGENTS.md`, `AGENTS.md`
- Approach: Put the KTD1 sentence in `## 3. Ready gate`, immediately before that section's ready-question blockquote. Point the earlier HARD "Exact ask" bullet at that section so it is not a second spoken script. Put the same sentence immediately before the exact ready question in `skills/forge-interview/AGENTS.md`. Delete "Do not ask whether they want a spec." Do not quiz them. A bare no, not yet, or wait is not ready and does not set `write_spec` false. An explicit refusal of the spec write is the decline, including when it shares the ready utterance. A decline alone is not ready-yes. The interview answers set `write_spec` true or false before the helper. Do not omit the key on that path.
- Test scenarios: The ready-gate section contains the KTD1 sentence before its blockquote. A bare no does not set the flag. An explicit spec refusal does, including in the same breath as ready. The interview answers example includes the key.
- Verification: `python3 skills/forge-interview/prove_fm606.py` still requires the exact ready question in the skill, and the new order check in U3.

### U2. Say the same thing in the human docs

- Goal: A person reading the README or the tutorial sees the disclosure before ready, and sees that the close names the spec path or says the spec was skipped.
- Requirements: R1, R6, R7
- Files: `README.md`, `docs/getting-started.md`
- Approach: The spec section and the ready step say the disclosure happens before the ready question, that ready-yes writes the spec unless they declined, and that a late flag does not delete a file already written. The close described there names the spec path or says the spec was skipped. Do not add a second chart.
- Test scenarios: Neither doc tells the reader that Forge never mentions a spec. Both say the close names the spec path or the skip.
- Verification: Read both sections against R1 and R7. No new command.

### U3. Prove the disclosure precedes the ready question

- Goal: A future edit cannot hide the disclosure or move it after the ready question without a failing prove.
- Requirements: R1, R2
- Files: `skills/forge-interview/prove_fm606.py`
- Approach: Inside `## 3. Ready gate`, assert the KTD1 sentence appears before that section's ready-question blockquote. Keep the existing whole-file check that `READY_PROMPT` is present. Do not use a whole-file "before the first copy" check. The skill's interview answers example must include `write_spec`. Do not assert chat behavior.
- Test scenarios: Moving the disclosure below the ready question fails the prove. Deleting it fails the prove. The exact ready question still has to be present.
- Verification: `python3 skills/forge-interview/prove_fm606.py` and `python3 skills/forge-interview/prove_issue1.py`

## Verification Contract

- `python3 skills/forge-interview/prove_fm606.py` proves the exact ready question is present and that the disclosure sits before it inside the ready-gate section.
- `python3 skills/forge-interview/prove_issue1.py` proves a false `write_spec` still skips `docs/spec.md`. A missing flag still writes for a non-interview call. That missing-flag write is not the interview consent rule.
- No release gate. No behavioral chat evaluation. The interview is agent instructions, and these proves check the instruction text and the writer, not a Cursor session.

## Definition of Done

- R1 through R8 are true in the skill and the human docs.
- U3's prove fails if the disclosure is missing or follows the ready question.
- No abandoned parser, second ready question, or silence timer is left in the diff.
- The exact ready question is unchanged.
