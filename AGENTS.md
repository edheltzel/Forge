# Forge

Framework repo for agentic rails. Not a product app. Do not bake a stack.

DOX contract copied from ~/Developer/AI/Skills/dox-framework. That skill repo is not vendored here.

## Codegraph

Use codegraph before guessing structure: query, explore, context, node.
Captain machine: /Users/ed/.bun/bin/codegraph. Else codegraph on PATH.

## Forge contracts

Interview first (`/forge-interview`). Adaptive invent-and-branch, one question at a time. Domain-agnostic.
Enough-to-structure: **what**, **who**, **done**, **constraints** (all non-empty after trim). Ready-yes alone does not lay the binder. Offer ready only after the gap check passes. Max **12** invent rounds after the opener; cap does not waive the gap check.

Typed packs (website 0–5 experience gate, probe depth, vocab) are a **later hook** — not the day-one interview spine. When a pack exists, load it as session expert; never dump pack body into the target.

ICM-as-standard for the deliverable:
- Always **generate** a minimal **ICM BASE** from interview answers. Stage shape comes from the interview: the agent records the type it inferred (`project_type`) and the stage slugs that project actually has (`stages`), and apply lays exactly those; absent `stages` falls back to the generic four, and website 01–07 only when a later typed pack applies. No type-to-stages table in the generator. Do **not** copytree workbench / ICM-reuseable-template / product workspaces into the target.
- The binder is a visible workspace at `forge/`, never `.forge/`, never `docs/icm/`, never a root `icm/`, and never loose ICM files at the target root. `forge/` is the workflow. `docs/` is only the prose shelf: `docs/spec.md` stays a sibling, not a file inside `forge/`. Do not flatten stage files into `docs/`. Project root keeps the project's own `AGENTS.md` (thin file on greenfield if missing) plus one marker-guarded pointer (`<!-- forge-icm:start -->`) to `forge/`. Binder entry: `forge/AGENTS.md`. Workflow contract: `forge/CONTEXT.md`. Answers: `forge/setup/answers.json`, `forge/setup/project-brief.md`. Stages, `_config/`, `shared/`, `setup/`, and any gated `brand-vault/` or workspace `skills/` live under `forge/`. Inside `forge/`, links stay relative (`setup/`, `stages/`, `_config/`). Do not write `CONTEXT.md`, `workflow-map.md`, `stages/`, `_config/`, `setup/`, `shared/`, or an ICM `README.md` at the target root. Do not replace the target `README.md` or `.gitignore`. Do not hide the binder. `forge-software/` stays a project-root sibling, not inside `forge/`. Website gated adds (brand-vault, stack refs) are later pack, not the day-one grill.
- Apply writes that binder under `forge/` while `--target` stays the project root. Do not pass `--target` at `forge/`. Spec stays `docs/spec.md` unless `spec_dest` is `forge`.
- Stop after apply. No feature build.
- Captain SoT folders are **read-only reference** for the interviewing agent. `skills/forge-interview` (`grill.py` + `apply_icm_base.py`) generate the target; they do not dump SoT trees.

Software rails only on an **explicit separate toggle** (optional later pack branch — not the core interview). Sibling stubs under the target (e.g. `forge-software/STACK.md`), never a substitute for ICM BASE and never a wholesale greenfield/brownfield template copy. Do not ask Turbo vs Nx / host / data / IdP as required interview questions.

Legacy `agent-workflows/` one-liners are not the ICM apply target.

Each run writes a spec unless `write_spec` is false in the answers before apply. The interview says that default immediately before the ready question, and sets the key explicitly. A missing key still writes for a call that is not this interview. Setting the flag after apply does not skip a file already written. Default path is `docs/spec.md` on the target. `spec_dest: forge` writes Forge `specs/<slug>.md` instead. Problem is `spec_problem`, else `what`. Overlay/brownfield keeps the repo's own `AGENTS.md` and writes or replaces one ICM pointer block. The pointer targets `forge/` and names the spec when one is written, not a root `CONTEXT.md` and not `docs/icm/`. Social/blog packs later.

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

## User Preferences

Track durable work as a GitHub issue. Mirror in-flight work with `npx -y tasks-axi`. Link the issue or PR on `tasks-axi done`. Close the GitHub issue when the task ships.


## Child DOX Index

- skills/AGENTS.md
- templates/AGENTS.md
- agent-workflows/AGENTS.md
- specs/AGENTS.md
- .claude/AGENTS.md
- .github/AGENTS.md
- .cursor/AGENTS.md
