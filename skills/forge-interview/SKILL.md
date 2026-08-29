---
name: forge-interview
description: Interview for Forge greenfield or brownfield. Always asks what they are building and which stack they want. Use for /forge-interview.
---

# Forge interview

Grow Me style. One question at a time. Short. No forms. Do not implement the product. Do not pick a stack for them.

HARD: no default stack. Never silently choose Turbo, Nx, Vercel, Cloudflare, Supabase, Convex, Clerk, or Better Auth.

## 1. Mode

Ask: new repo (greenfield) or convert/manage existing (brownfield)? Wait.

## 2. What they are building

Ask what they are building. Forge is rails, not the product. Wait.

## 3. Stack (always)

Ask one at a time: Turbo or Nx; host Vercel/Cloudflare/named; data Supabase/Convex/own API; IdP Better Auth/Clerk/named. No silent default. TanStack is app libs, not a task runner. Do not scaffold until all four answers exist.

## 4. Spec this run?

Ask: write a spec into specs/ this run, or skip? Optional per run. Wait.

## 5. Apply rails

Greenfield uses templates/greenfield. Brownfield overlays next to src/ only.

## 6. Close

Name path, mode, four stack picks, spec yes/no. Stop. Do not build features.
