---
title: "Run your first Forge interview"
description: "Learn Forge by completing one interview until it names your path, mode, stack, and spec choice"
---

# Run Your First Forge Interview

In this tutorial, we'll run Forge's interview once and stop when it names what we picked. By the end, we'll have a close that lists path, mode, four stack answers, and whether a spec will be written this run. We will not scaffold an app, and we will not let Forge pick a stack for us.

This tutorial takes about 10 minutes.

## What you'll build

A finished Forge interview close that:
- Names greenfield or brownfield
- Names what we are building (Forge is rails, not the product)
- Names all four stack picks (task runner, host, data, identity provider (IdP: the service that signs people in))
- Names spec yes or no for this run

## Prerequisites

- Cursor
- The Forge repo at `~/Developer/forge`

## Step 1: Open Forge

Open `~/Developer/forge` in Cursor.

You should see the Forge repo, including `skills/forge-interview/SKILL.md`.

## Step 2: Start the interview

In chat, run:

```
/forge-interview
```

You should see the first question: new repo (greenfield) or convert/manage existing (brownfield)?

If the slash command is not wired, paste this instead (same interview, not a different product):

```
Read skills/forge-interview/SKILL.md and run it now.
```

You should then see that same first question.

If nothing asks greenfield vs brownfield, stop. Stay in `~/Developer/forge` and use the Read-skill line above. Do not invent a stack. Do not start building.

## Step 3: Answer mode

Reply with **new repo**.

You should see a question about what we are building.

## Step 4: Answer what we are building

Reply that we are putting rails under a sample app called `demo-rails`. Forge is the rails, not the product.

You should see stack questions, one at a time: task runner, host, data, then identity provider (IdP).

## Step 5: Answer stack (all four)

Answer in this order, waiting between questions. Do not skip. Do not accept a silent default.

1. Task runner: **Turbo**
2. Host: **Vercel**
3. Data: **Supabase**
4. Identity provider: **Better Auth**

You should see a question: write a spec into `specs/` this run, or skip?

If any of those four never got asked, stop. Return to Step 2 and run the interview again. Do not continue with a stack you did not name.

## Step 6: Spec this run

Reply **skip**.

You should see a close that names path, mode (greenfield), the four stack picks above, and spec no.

Stop there. Do not ask it to build features.

## What you've learned

- Start Forge with `/forge-interview`
- The interview always asks mode, what we're building, four stack picks, and spec yes/no
- We name the stack. Forge does not.

## Next steps

- Run `/forge-interview` again for a brownfield overlay
- How-to: apply rails after a close (not this tutorial)
