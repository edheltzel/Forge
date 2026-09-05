---
name: forge-interview
description: Interview for an ICM workspace (website workbench BASE first, then gated folders). Software rails only on an explicit separate toggle. Use for /forge-interview.
---

# Forge interview (ICM-first)

Grow Me style. One question at a time. Short. No forms.
Do not implement the product. Do not build features after apply.
Do not clone `fm279-forge-e2e` throwaway software rails as the ICM deliverable.

**Captain folders are SoT.** This skill drives the interview and apply steps.
Layout comes from workbench / `_core` — do not invent a parallel ontology inside this skill.

SoT paths (BigMac defaults):
- Website BASE: `/Users/ed/Developer/ForgeTemplates/icm-website-workbench`
- ICM conventions: `/Users/ed/Developer/AI/Standards/ICM/_core`
- Optional software sibling sources: `templates/software/`, `templates/greenfield/`, `templates/brownfield/` under this Forge repo

Deterministic apply (preferred for prove / non-interactive):  
`python3 skills/forge-interview/apply_icm_base.py --help`

HARD:
- Always lay **ICM BASE** before any gated add.
- Interview answers fill `setup/client.md` and gate folders — they do not replace BASE.
- Software rails only if the user explicitly opts in on the **separate** software toggle. Sibling, never substitute for ICM.
- Stop after apply. Humans edit markdown next.

---

## 0. Path / mode

Ask: new ICM workspace at a path (greenfield ICM), or overlay ICM into an existing repo?
Wait. Record target path. Still ICM BASE — not `apps/*` monorepo rails unless software toggle later.

## 1. Product shape

Ask: client **website** pipe (workbench stages 01–07), or **generic** ICM workflow (builder / `_core` blanks)?
Wait.

- Website → BASE = icm-website-workbench shape.
- Generic → BASE = `_core` templates + only the stage folders they list later. Do not copy a product workspace wholesale (e.g. do not clone `script-to-animation`).

## 2. Website intake (only if website)

Ask one at a time (workbench `_config/intake-questions.md`):

1. Brief, live rebuild, or both?
2. Existing URL and who owns DNS / hosting today?
3. Astro or Next for this client?
4. Cloudflare / own VPS, or their host?
5. Markdown collections, headless CMS, or keep the old CMS?
6. Figma: full file or key screens only?
7. What does "shipped live" mean (domain, staging first, analytics)?
8. Accessibility bar (default WCAG 2.2 AA)?

No silent stack default for Astro vs Next.

## 3. Gated ICM adds

Ask one at a time:

9. Brand vault needed? (yes → add `brand-vault/` outside `_config/`; no → brand notes only in `client.md`)
10. Drop any default stages as a clear no-op? Prefer keep with thinner contract; delete folder only when answer is explicit no-op (ICM Remotion precedent).
11. Bundle any domain `skills/<name>/`? (yes → name them; no → none). Workbench ships with no skills/.

## 4. Software rails toggle (separate)

Ask: also apply Forge **software** rails (task runner / host / data / IdP templates + greenfield or brownfield AGENTS) as a **sibling** to ICM?

- If **no**: skip. ICM only.
- If **yes**: then ask one at a time — Turbo or Nx; host; data; IdP. No silent defaults. Apply under a sibling path (e.g. `forge-software/`) or brownfield overlay beside `src/` — never instead of ICM BASE.

## 5. Spec this run?

Ask: write a short note into the target's docs or Forge `specs/` this run, or skip?
Optional. Wait.

## 6. Apply rails

Run apply (script or equivalent manual steps). Order is mandatory:

1. **Materialize BASE** from SoT (website workbench tree, or `_core` + listed stages for generic).
2. Write interview answers into `setup/client.md` (website) or intake brief (generic).
3. **Gated adds only**: `brand-vault/`, `stages/02-scaffold/references/stack-astro.md` or `stack-next.md`, optional `shared/content-model.md`, optional `skills/`, keep/delete stage folders.
4. Software sibling only if toggle yes.
5. Stop. Do not build features. Do not treat `agent-workflows/` one-liners as the ICM deliverable.

## 7. Close

Name: target path, mode, product shape, client intake picks (if website), gates (brand vault / stages kept|dropped / skills), software toggle (+ four picks if yes), spec yes/no.
Stop.
