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
- **Experience gate (FM-325):** for website only, ask integer **0–5** immediately after product shape, before intake Q1. Load `packs/website/v1.yaml` **levels["N"]** for that integer (all of 0–5 are explicit — do not clamp mid levels). Vocab/depth/probes come from that entry; persist raw `experience_level`. Never dump pack body into the target. Do not invent weight training or self-learning marketing.

---

## 0. Path / mode

Ask: new ICM workspace at a path (greenfield ICM), or overlay ICM into an existing repo?
Wait. Record target path. Still ICM BASE — not `apps/*` monorepo rails unless software toggle later.
Record `mode`: `greenfield` or `overlay`. Overlay is brownfield → ICM.
If overlay: read the target's existing `AGENTS.md`, `README.md`, and `docs/` first (grill-with-docs). Do not re-ask facts those files already state. Ask only gaps. Do not replace `src/` or the live app tree.


## 1. Project type

Ask: client **website** pipe (stages 01–07), or **generic** ICM workflow (listed stages only)?
Wait. This is the project type. Record as `product` (`website` | `generic`).


- Website → ask experience gate (next), then generate website ICM spine (stages 01–07) from answers + inlined stubs.
- Generic → **skip** experience gate in v1. Generate `_config` / `setup` / `shared` + only the stage folders they list. Do not clone a product workspace.

Optionally **read** captain SoT (workbench / `_core`) while interviewing for shape cues — do not copy those folders into the target.

## 1b. Experience gate (website only)

Ask immediately after product shape = website, **before** intake Q1:

> How experienced are you with this kind of website build? Reply with an integer **0–5** only (0 = plain language / shallow; 5 = expert terms / deep probes).

Wait. Accept integer 0–5 only. Re-ask if not in range. **Do not clamp** mid levels to 0 or 5.

Then **load session expert** = read `skills/forge-interview/packs/website/v1.yaml` **levels["N"]** for the chosen integer N into this session (every of 0–5 is explicit in the pack):
- Record raw `experience_level` (the HIL integer), `pack_id` (`website`), `pack_version` (`v1`) in answers — do **not** rewrite 1→0 or 3→5.
- Phrase subsequent questions with that level entry's `vocabulary` / `phrase_hints`.
- Ask **core_slots** at every level (same ICM slots).
- Ask that level's **probes** only (additive when non-empty). Pack map:
  - **0–2**: plain vocab, shallow, `probes: []` (core 8 only)
  - **3–4**: expert vocab / deep phrasing, still `probes: []` (no L5 deep probe slots)
  - **5**: expert vocab / deep + full L5 probes list
- Do **not** write the pack YAML body into the target. Apply may write `setup/session-expert.md` as a pointer (id / version / level only).

## 2. Website intake (only if website)

Ask one at a time. **Phrase by pack level entry** (plain at 0–2; expert terms at 3–5). Same ICM slots:

Core 8 (always):

1. Brief, live rebuild, or both? *(L0–2: rebuild vs new)*
2. Existing URL and who owns DNS / hosting today? *(L0–2: where the site lives)*
3. Astro or Next for this client?
4. Cloudflare / own VPS, or their host?
5. Markdown collections, headless CMS, or keep the old CMS? *(L0–2: files vs CMS)*
6. Figma: full file or key screens only? *(L0–2: whole vs few screens)*
7. What does "shipped live" mean (domain, staging first, analytics)?
8. Accessibility bar (default WCAG 2.2 AA)?

Deep probes when pack level entry lists them (level **5** only in v1; after core 8, still one at a time). Levels 3–4 use expert phrasing but **no** deep probe slots:

9. Redirect strategy (legacy URL map / keep equity)?
10. SEO equity notes (what rankings/content must survive cutover)?
11. CMS lock-in risk (can we leave the old CMS; export path)?
12. Staging hostname (who owns it; preview URL)?
13. Analytics owner (who has GA/Tag Manager / what must fire on go-live)?

No silent stack default for Astro vs Next.

## 3. Gated ICM adds

Ask one at a time (numbering continues after intake / probes):

- Brand vault needed? (yes → add `brand-vault/` outside `_config/`; no → brand notes only in `client.md`)
- Drop any default stages as a clear no-op? Prefer keep with thinner contract; delete folder only when answer is explicit no-op (ICM Remotion precedent).
- Bundle any domain `skills/<name>/`? (yes → name them; no → none).

## 4. Software rails toggle (separate)

Ask: also apply Forge **software** rails (task runner / host / data / IdP + greenfield or brownfield AGENTS stubs) as a **sibling** to ICM?

- If **no**: skip. ICM only.
- If **yes**: then ask one at a time — Turbo or Nx; host; data; IdP. No silent defaults. **Generate** `forge-software/STACK.md` + AGENTS stubs from answers — do **not** copytree `templates/greenfield` / `templates/brownfield` / `templates/software` into the project.

## 5. Spec this run? (continued interview, then to-spec)

Stay in Grow Me. One question at a time. Do not switch to grill frontier rounds.

- Overlay / brownfield: do not ask skip. Spec is required. Synthesize from the docs you already read plus answers. No extra spec questions unless a gap remains.
- Greenfield: ask write spec this run, or skip? Wait.
  - Skip → `write_spec: false`. Go to apply.
  - Yes → continue the interview (still one at a time):
    1. What problem should the spec state? Wait. Record `spec_problem`.
    2. What is out of scope for this run? Wait. Record `spec_out_of_scope`.
    Then apply. That is greenfield + continued interview → spec.

Write Problem, Solution, Scope, Out of scope, Interview. Default path: `<target>/docs/spec.md`. If they asked Forge `specs/`, set `spec_dest: forge`. Agent may open a GitHub issue from that file after apply. Apply itself does not call `gh`.



## 6. Apply rails

Run generate helper (or equivalent manual writes). Order is mandatory:

1. **Generate BASE** as fresh files from interview content: numbered stages with CONTEXT stubs, `_config/` process stubs, `setup/`, `shared/`. Website vs generic layout comes from answers + small generators — **not** cloning Captain SoT folders.
2. Persist answers into `setup/client.md` + `setup/answers.json` (website) or `setup/project-brief.md` + `setup/answers.json` (generic). Include `experience_level`, `pack_id`, `pack_version` when website gate ran. Optional `setup/session-expert.md` pointer only (never pack body).
3. **Gated adds only**: `brand-vault/`, `stages/02-scaffold/references/stack-astro.md` or `stack-next.md`, optional `shared/content-model.md`, optional `skills/`, keep/delete stage folders.
4. Software sibling stubs only if toggle yes (generated — no template tree dump).
5. Spec: overlay always; greenfield when `write_spec`/`spec` is yes after `spec_problem` and `spec_out_of_scope`.

6. Stop. Do not build features. Do not treat `agent-workflows/` one-liners as the ICM deliverable.



## 7. Close

Name: target path, mode (greenfield|overlay), project type, experience level + pack (if website), client intake picks (if website), probes asked (if any), gates (brand vault / stages kept|dropped / skills), software toggle (+ four picks if yes), spec path or skip, spec_problem if asked.


Stop.
