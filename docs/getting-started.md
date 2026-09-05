---
title: "Run your first Forge interview"
description: "Learn Forge by completing one ICM-first interview until it names path, gates, and optional software toggle"
---

# Run Your First Forge Interview

In this tutorial, we'll run Forge's interview once and stop when it names what we picked. By the end, we'll have a close that lists target path, ICM product shape, website intake (if any), gated folders, and whether software rails were opted in. We will not build a client site, and we will not treat software monorepo rails as the ICM deliverable.

This tutorial takes about 10 minutes.

## What you'll build

A finished Forge interview close that:
- Names greenfield ICM path or overlay-into-existing
- Names website workbench pipe vs generic ICM
- Names website intake picks (when website)
- Names gates: brand vault, stages kept/dropped, skills
- Names software toggle no (default for this tutorial) or yes + four stack picks
- Names spec yes or no for this run

## Prerequisites

- Cursor
- The Forge repo at `~/Developer/forge`
- Captain workbench at `~/Developer/ForgeTemplates/icm-website-workbench` (interview reference only — not copied into targets)

## Step 1: Open Forge

Open `~/Developer/forge` in Cursor.

You should see `skills/forge-interview/SKILL.md` and `skills/forge-interview/apply_icm_base.py`.

## Step 2: Start the interview

In chat, run:

```
/forge-interview
```

You should see the first question: new ICM workspace path, or overlay into an existing repo?

If the slash command is not wired, paste this instead:

```
Read skills/forge-interview/SKILL.md and run it now.
```

## Step 3: Answer mode + product

1. Reply with a new path, e.g. `~/Developer/demo-icm-site`.
2. Reply **website** for the website ICM pipe (stages 01–07).

You should then see website intake questions, one at a time.

## Step 4: Answer website intake

Answer one at a time (example set):

1. Start mode: **both**
2. URL / DNS: **none yet / we own DNS**
3. Stack: **Astro**
4. Host: **Cloudflare**
5. Content: **markdown**
6. Figma: **key screens**
7. Shipped live: **staging then production on our domain**
8. A11y: **WCAG 2.2 AA**

## Step 5: Gates + software toggle

1. Brand vault: **yes**
2. Drop stages: **none**
3. Bundle skills: **no**
4. Also apply Forge software rails: **no**
5. Spec this run: **skip**

## Step 6: Apply (or watch the agent apply)

The agent should **generate** ICM BASE from interview answers, write `setup/client.md` (+ `setup/answers.json`), add `brand-vault/` and `stages/02-scaffold/references/stack-astro.md`, then stop. No workbench copytree.

Non-interactive prove from the Forge repo:

```bash
python3 skills/forge-interview/apply_icm_base.py \
  --target /tmp/fm304-demo-icm \
  --product website \
  --answers-json '{"client_name":"Demo","start_mode":"both","stack":"astro","host":"cloudflare","content":"markdown","figma":"key-screens","shipped_live":"staging then prod","a11y":"WCAG 2.2 AA","brand_vault":true,"skills":[],"software_rails":false}'
```

You should see generated ICM folders under the target (`AGENTS.md`, `_config/`, `setup/client.md`, `stages/01-audit-ia` … `07-cd`, `brand-vault/`). You should **not** see `apps/` monorepo rails, and files must not be a mass-identical dump of the workbench SoT.

## What you've learned

- Start Forge with `/forge-interview`
- ICM BASE is generated from interview answers (SoT is interview reference only)
- Answers fill `client.md` and gate folders
- Software rails are a separate opt-in sibling

## Next steps

- Re-run with software toggle **yes** to add a `forge-software/` sibling
- How-to: run stage 01 after humans edit `setup/client.md` (not this tutorial)
