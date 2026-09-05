# Forge

Framework repo for agentic rails. Not a product app. Do not bake a stack.

DOX contract copied from ~/Developer/AI/Skills/dox-framework. That skill repo is not vendored here.

## Codegraph

Use codegraph before guessing structure: query, explore, context, node.
Captain machine: /Users/ed/.bun/bin/codegraph. Else codegraph on PATH.

## Forge contracts

Interview first (`/forge-interview`). Grow Me, one question at a time.

ICM-as-standard for the deliverable:
- Always **generate** a minimal **ICM BASE** from interview answers (website stages 01–07 or generic listed stages). Do **not** copytree workbench / ICM-reuseable-template / product workspaces into the target.
- Interview answers → durable artifacts (`setup/client.md`, `setup/answers.json`, `CONTEXT.md`) + gated adds (brand-vault, stack ref stubs, optional skills, keep/delete stages).
- Stop after apply. No feature build.
- Captain SoT folders are **read-only reference** for the interviewing agent. `skills/forge-interview` + `apply_icm_base.py` generate the target; they do not dump SoT trees.

Software rails only on an **explicit separate toggle**. Sibling stubs under the target (e.g. `forge-software/STACK.md`), never a substitute for ICM BASE and never a wholesale greenfield/brownfield template copy. When that toggle is on: ask Turbo vs Nx, host, data, IdP — no silent defaults.

Legacy `agent-workflows/` one-liners are not the ICM apply target.

Each run may ask whether to write a short spec note. Social/blog packs later.

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

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md

## Child DOX Index

- skills/AGENTS.md
- templates/AGENTS.md
- agent-workflows/AGENTS.md
- specs/AGENTS.md
- .claude/AGENTS.md
- .github/AGENTS.md
- .cursor/AGENTS.md
