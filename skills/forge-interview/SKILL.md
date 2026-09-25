---
name: forge-interview
description: Adaptive ICM interview. Invent the next question from gaps until enough-to-structure, then generate a thin generic ICM skeleton from answers (no SoT copytree). Domain-agnostic. Use for /forge-interview.
---

# Forge interview (ICM-first)

Adaptive invent-and-branch (Pocock-style). One question at a time. Short. No forms.
Domain-agnostic — software, branding, research, DIY, anything. Infer type; do not serve a type menu.
Do not implement the product. Do not build features after apply.

**Sole product opinion:** outputs are structured as ICM. The interview exists to learn enough to lay that binder. No other product opinions. No always-recommend.

Captain SoT folders (workbench, ICM `_core`) remain **reference for the interviewing agent** (read during interview) — **never** dumped into the target.

SoT paths (BigMac defaults — **read-only reference**, never apply targets):
- Website shape reference: `/Users/ed/Developer/ForgeTemplates/icm-website-workbench`
- ICM conventions reference: `/Users/ed/Developer/AI/Standards/ICM/_core`

Machine gate (preferred after each turn / before apply):

```
python3 skills/forge-interview/grill.py --help
python3 skills/forge-interview/grill.py --slots-json '{"what":"…","who":"…","done":"…","constraints":"…"}' --check
```

Deterministic generate (only after gap pass ∧ ready yes):

```
python3 skills/forge-interview/apply_icm_base.py --product generic --help
```

HARD:
- **Invent-and-branch.** Forge invents the next question from remaining gaps. There is **no** fixed Q1–Q5 / core-8 product spine.
- **Enough-to-structure** (machine): after trim, **what**, **who**, **done**, **constraints** are all non-empty. That is the only day-one floor. Typed pack floors are a hook for later — **none ship in this interview**.
- **Ready-yes alone must not lay the binder.** If they say ready with empty slots: refuse, name the empty slots in plain words, invent the next question for the first empty slot.
- **Offer the ready gate only after the gap check passes.** Exact ask: Are you ready for us to structure this project, or is there anything else you want to add?
- **Grill bound:** max **12** invent rounds after the opener. Past the cap, only chase empty enough-slots (no new soft gaps). Cap does **not** waive the gap check.
- **Suggestions only when the human asks.** Ground in industry standards / best practices. Never force a stack or host. Never always-recommend.
- Always **generate** a thin **generic ICM BASE** from interview answers after gap pass ∧ ready yes. **No template dump.** Never `shutil.copytree` / `copy2` of workbench, `ICM-reuseable-template`, or product workspaces into the target.
- Durable artifacts: `setup/project-brief.md`, `setup/answers.json`, root `CONTEXT.md`.
- Software four-pack (Turbo/Nx/host/data/identity) is **not** this interview. Dead end for the product story. Optional later pack branch only if they explicitly ask later — never a required ask.
- Stop after apply. Humans edit markdown next.

Out of workflow as required asks: timeline/deadline (only if they volunteer); forced stack/host quizzes; always-on recommendations; a separate “anything else?” catch-all (folded into the ready gate); website vs generic type menu; 0–5 experience gate as a required first-day ask.

---

## 0. Open

Ask the opener (not a project-type menu):

> What are you trying to make or figure out?

Wait. Store the answer in **what**. Infer project type privately. Do not make them pick from a list.

If overlaying into an existing repo is already obvious from context, read `AGENTS.md`, `README.md`, and `docs/` (grill-with-docs) and do not re-ask facts those files already state. Target path is apply logistics — ask it only after ready yes, not as the opener.

## 1. Invent-and-branch

Keep a slot map: `what`, `who`, `done`, `constraints` (plus free-form notes). Shown to the human only as plain follow-ups — never as a labeled five-question spine.

| Slot | Pass when | Plain meaning |
|------|-----------|----------------|
| **what** | non-empty after trim | What they’re trying to make or figure out |
| **who** | non-empty after trim | Who it’s for (self, client, team, …) |
| **done** | non-empty after trim | Finish line — what must be true / in hand |
| **constraints** | non-empty after trim | Must-have and/or must-avoid (`none known yet` counts if they said so) |

Each turn:

1. Map their words into slots. Their words stay on the page; you structure behind the scenes.
2. Run the gap check (`grill.py --check` or the same rules).
3. If any slot is empty: invent **one** question aimed at the **first** empty slot (or a clarifying follow-up on a thin slot). Wait.
4. Count that invented question as one invent round. Opener does not count. Ready-gate ask does not count.
5. Do not bombard. Do not ask Turbo/Nx/host/data/IdP. Do not ask a type menu.

If they **ask for suggestions**: pause invent, cite industry standards / best practices for the current empty slot, do not dictate a pick, then continue the grill. If they did not ask, do not suggest.

Experience 0–5 / website pack: **not loaded day one**. When a typed pack exists later for the inferred type, scale probe depth and vocabulary from that pack and satisfy its floor before ready. Until then, only the four-slot floor applies. Never dump a pack body into the target.

## 2. Grill bounds

- **Generic floor:** the four slots above. Until they pass, every invented question targets the first empty slot.
- **Pack floor:** hook only. Day one has no typed packs in this interview.
- **Round cap:** max **12** invent rounds after the opener. At the cap, if the gap check still fails: summarize what’s filled, name what’s still empty in plain words, and keep grilling **only** the empty slots (or ask whether they want to add the missing piece / mark constraints as `none known yet`). Do **not** invent soft new gaps. Cap hit does not waive the gap check and does not offer ready.

## 3. Ready gate (only after gap check passes)

When all four slots are non-empty, ask **exactly**:

> Are you ready for us to structure this project, or is there anything else you want to add?

- If they add more: take the note, re-run the gap check, then ask the ready gate again until they say ready.
- If they say ready while any required slot is empty: **refuse structure**. Name the empty slots in plain words. Invent the next question for the first empty one. Do not call apply.
- If they say ready and the gap check passes: interview done. Go to apply.

Interview done = gap check pass ∧ ready yes.

## 4. Apply rails

Ask target path if you do not already have it (greenfield path vs overlay into an existing repo). Overlay: do not replace `src/` or the live app tree; overlay always writes a spec, and apply appends one marker-guarded ICM pointer block to the repo's existing `AGENTS.md` so its agent finds the binder. Greenfield spec only if they asked for one.

Then run generate. Order is mandatory:

1. Confirm `grill.py --check` reports enough-to-structure (all four slots + ready). If not, refuse and return to invent.
2. **Name the shape from the type you inferred.** Put your inference in `project_type` and the stages this project actually has in `stages` (slugs, in order — a podcast gets `01-format` … `05-distribute`, a remodel gets its own). Apply lays exactly those. Omit `stages` only when the interview never reached shape; then the generic `01-intake,02-discovery,03-build,04-review` spine fills in. Never offer the human a stage menu.
3. **Generate BASE** as fresh files from interview content: numbered stages with CONTEXT stubs, `_config/`, `setup/`, `shared/`. Thin skeleton — **not** cloning Captain SoT folders, **not** the website 01–07 pipe unless a later typed pack says so.
4. Persist `setup/project-brief.md` + `setup/answers.json` with project type / what / who / done / constraints / notes / `ready: true`.
5. Software sibling stubs **only** if they explicitly asked for software rails later (generated — no template tree dump). Do not prompt for Turbo/Nx as part of this apply.
6. Spec: overlay always (problem may be `what`); greenfield when they asked.
7. Stop. Do not build features. Do not treat `agent-workflows/` one-liners as the ICM deliverable.

```
python3 skills/forge-interview/apply_icm_base.py \
  --target <path> \
  --product generic \
  --answers-json '<slots + ready true>'
```

Generic apply **refuses** if any enough-slot is empty, ready is not yes, or `stages` is anything but a non-empty list of slugs.

## 5. Close

Name: target path, inferred type (your inference, not a menu pick), the four slots in their words, invent-round count, ready yes, spec path or skip.

Stop.
