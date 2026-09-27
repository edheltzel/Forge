---
title: "Run your first Forge interview"
description: "Learn Forge by completing one adaptive ICM interview until enough-to-structure, then laying a thin generic binder"
---

# Run Your First Forge Interview

In this tutorial, we'll run Forge's interview until the enough-to-structure gate passes and we say ready. By the end, we'll have a close that names the four slots in our words and a generated generic ICM skeleton. We will not pick a project-type menu, we will not answer a Turbo/Nx quiz, and we will not treat software monorepo rails as the ICM deliverable.

This tutorial takes about 10 minutes.

## What you'll build

A finished Forge interview close that:
- Started from "what are you trying to make or figure out?" (not a type menu)
- Filled **what**, **who**, **done**, **constraints** in your words
- Got the ready gate only after those four were non-empty
- Generated a thin generic ICM BASE at a path you chose
- Did **not** run a fixed Q1–Q5 / website core-8 spine

## Prerequisites

- Cursor
- The Forge repo at `~/Developer/forge`
- Captain workbench at `~/Developer/ForgeTemplates/icm-website-workbench` (interview reference only — not copied into targets)

## Step 1: Open Forge

Open `~/Developer/forge` in Cursor.

You should see `skills/forge-interview/SKILL.md` and `skills/forge-interview/grill.py`.

## Step 2: Start the interview

In chat, run:

```
/forge-interview
```

You should see the opener: what are you trying to make or figure out?

If the slash command is not wired, paste this instead:

```
Read skills/forge-interview/SKILL.md and run it now.
```

## Step 3: Answer in your words

Reply with a real project — software, branding, research, or DIY. Example (kitchen remodel):

1. What: **A contractor packet for the back-of-house kitchen remodel**
2. Who: **Our household**
3. Done: **Signed packet and a room that passes inspection**
4. Constraints: **Keep the existing plumbing wall**

Forge invents the next question from whatever is still empty. One at a time. If you get stuck, *ask* for suggestions — it will cite industry practice, not dictate a stack.

You should **not** see a website-vs-generic menu, an Astro-vs-Next quiz, or Turbo/Nx as required asks.

## Step 4: Ready gate

When the four slots are filled, Forge asks:

> Are you ready for us to structure this project, or is there anything else you want to add?

Add a note if you want, then say ready. If you say ready while a slot is empty, Forge refuses, names the empty slots in plain words, and keeps grilling.

## Step 5: Apply (or watch the agent apply)

Name a target path when asked. The agent should **generate** a thin generic ICM BASE from the four slots, then stop. It writes `docs/spec.md` unless they said no. If they said no, `write_spec` false has to be in the answers before apply. Setting it after does not delete the file. Contract home for the workflow is `forge/` per root `AGENTS.md`. No workbench copytree.

Non-interactive prove from the Forge repo:

```bash
python3 skills/forge-interview/prove_fm606.py

python3 skills/forge-interview/apply_icm_base.py \
  --target /tmp/fm606-demo-icm \
  --product generic \
  --answers-json '{"what":"Kitchen remodel packet","who":"Our household","done":"Signed packet + inspection","constraints":"Keep plumbing wall","ready":true}'
```

Apply writes the workflow under `forge/` and a short pointer in root `AGENTS.md`. That pointer names `docs/spec.md` when the spec is written. This prove should show `forge/AGENTS.md`, `forge/_config/`, `forge/setup/project-brief.md`, `forge/stages/…`, and `docs/spec.md`. You should **not** see `stages/` or `CONTEXT.md` at the target root, `apps/` monorepo rails, or a mass-identical dump of the workbench SoT.

Generic apply **refuses** if any of the four slots is empty or `ready` is not yes.

## What you've learned

- Start Forge with `/forge-interview`
- Interview is invent-and-branch until enough-to-structure, then ready
- ICM BASE is generated from answers (SoT is interview reference only)
- Software rails are not the core interview

## Next steps

- Typed packs (website 0–5, branding, …) come later; they are not this tutorial
- How-to: run a stage after humans edit the brief (`forge/setup/project-brief.md`) (not this tutorial)
