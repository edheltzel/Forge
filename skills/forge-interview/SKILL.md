---
name: forge-interview
description: Interview for an ICM workspace. Capture answers, then generate ICM skeleton + gated folders from those answers (no SoT copytree). Software rails only on an explicit separate toggle. Use for /forge-interview.
---

# Forge interview (ICM-first)

Grow Me style. One question at a time. Short. No forms.
Do not implement the product. Do not build features after apply.
Do not clone `fm279-forge-e2e` throwaway software rails as the ICM deliverable.

**Interview alone must be enough** for the agent to understand requirements, create ICM structure, and scaffold project-type architecture.
Captain SoT folders (workbench, ICM `_core`) remain **reference for the interviewing agent** (read during interview) — **never** dumped into the target.
Do **not** copy `icm-website-workbench`, ICM-reuseable-template, or product workspaces into brown/greenfield projects.

SoT paths (BigMac defaults — **read-only reference**, never apply targets):
- Website shape reference: `/Users/ed/Developer/ForgeTemplates/icm-website-workbench`
- ICM conventions reference: `/Users/ed/Developer/AI/Standards/ICM/_core`

Deterministic generate (preferred for prove / non-interactive):  
`python3 skills/forge-interview/apply_icm_base.py --help`

HARD:
- Always **generate** a minimal **ICM BASE** from interview answers before any gated add.
- **No template dump.** Never `shutil.copytree` / `copy2` (or equivalent tree dump) of `icm-website-workbench`, `ICM-reuseable-template`, `ICM/workspaces`, or any Captain product workspace into the target. Generate via mkdir + write markdown only. Captain SoT may be read as reference while coding/interviewing — never as an apply copy source.
- Durable interview artifacts: `setup/client.md`, `setup/answers.json`, root `CONTEXT.md`, architecture notes as needed.
- Software rails only if the user explicitly opts in on the **separate** software toggle. Sibling stubs generated from answers — never wholesale-copy greenfield/brownfield template trees.
- Stop after apply. Humans edit markdown next.

---

## 0. Path / mode

Ask: new ICM workspace at a path (greenfield ICM), or overlay ICM into an existing repo?
Wait. Record target path. Still ICM BASE — not `apps/*` monorepo rails unless software toggle later.

## 1. Product shape

Ask: client **website** pipe (stages 01–07), or **generic** ICM workflow (listed stages only)?
Wait.

- Website → generate website ICM spine (stages 01–07) from answers + inlined stubs.
- Generic → generate `_config` / `setup` / `shared` + only the stage folders they list. Do not clone a product workspace.

Optionally **read** captain SoT (workbench / `_core`) while interviewing for shape cues — do not copy those folders into the target.

## 2. Website intake (only if website)

Ask one at a time (same questions as workbench intake reference):

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
11. Bundle any domain `skills/<name>/`? (yes → name them; no → none).

## 4. Software rails toggle (separate)

Ask: also apply Forge **software** rails (task runner / host / data / IdP + greenfield or brownfield AGENTS stubs) as a **sibling** to ICM?

- If **no**: skip. ICM only.
- If **yes**: then ask one at a time — Turbo or Nx; host; data; IdP. No silent defaults. **Generate** `forge-software/STACK.md` + AGENTS stubs from answers — do **not** copytree `templates/greenfield` / `templates/brownfield` / `templates/software` into the project.

## 5. Spec this run?

Ask: write a short note into the target's docs or Forge `specs/` this run, or skip?
Optional. Wait.

## 6. Apply rails

Run generate helper (or equivalent manual writes). Order is mandatory:

1. **Generate BASE** as fresh files from interview content: numbered stages with CONTEXT stubs, `_config/` process stubs, `setup/`, `shared/`. Website vs generic layout comes from answers + small generators — **not** cloning Captain SoT folders.
2. Persist answers into `setup/client.md` + `setup/answers.json` (website) or `setup/project-brief.md` + `setup/answers.json` (generic).
3. **Gated adds only**: `brand-vault/`, `stages/02-scaffold/references/stack-astro.md` or `stack-next.md`, optional `shared/content-model.md`, optional `skills/`, keep/delete stage folders.
4. Software sibling stubs only if toggle yes (generated — no template tree dump).
5. Stop. Do not build features. Do not treat `agent-workflows/` one-liners as the ICM deliverable.

## 7. Close

Name: target path, mode, product shape, client intake picks (if website), gates (brand vault / stages kept|dropped / skills), software toggle (+ four picks if yes), spec yes/no.
Stop.
