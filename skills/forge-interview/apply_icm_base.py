#!/usr/bin/env python3
"""Generate ICM BASE skeleton from interview answers JSON.

HARD (FM-304): mkdir + write markdown only. Never shutil.copytree / copy2 from
workbench, ICM-reuseable-template, or ICM/workspaces into the target. Captain
SoT (icm-website-workbench / ICM/_core) may inform the *shape* of this
generator while coding — it is never a runtime copy source.

Does not build product features. Software rails are opt-in sibling only (not the core interview).

FM-606: generic apply lays a thin skeleton only after enough-to-structure
(what/who/done/constraints all non-empty) AND ready yes. Ready-yes alone refuses.

FM-325: persist experience_level (raw HIL int 0-5) + pack_id + pack_version;
optional setup/session-expert.md pointer (id/version/level only — never pack body
dump). Do not clamp/alias mid levels (1→0 / 3→5); resolve behavior from pack
levels["N"] entry when interviewing.
"""
from __future__ import annotations

import argparse
import re
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import grill as _grill

FORGE_ROOT = Path(__file__).resolve().parents[2]

# Website pipe stage slugs (Captain workbench shape — generated, not copied).
WEBSITE_STAGES: list[tuple[str, str, str]] = [
    (
        "01-audit-ia",
        "Audit + IA",
        "## Inputs\n"
        "- `setup/client.md` complete enough to start\n"
        "- Existing site URL if start mode is live rebuild or both\n"
        "- Client brief / goals\n\n"
        "## Process\n"
        "1. If a live URL exists: crawl IA (nav, templates, key pages, forms, SEO basics). Note what to keep vs replace.\n"
        "2. If brief only: derive IA from goals and audience.\n"
        "3. Draft sitemap (pages + templates) and content types.\n"
        "4. List risks (CMS lock-in, SEO equity, redirects).\n\n"
        "## Outputs (this stage `output/` only)\n"
        "- `audit.md` — findings (or \"no live site\")\n"
        "- `ia.md` — sitemap + information architecture\n"
        "- `risks.md` — redirects, SEO, CMS\n\n"
        "## Stop\n"
        "Do not design or scaffold the repo here.\n",
    ),
    (
        "02-scaffold",
        "Scaffold / workflow",
        "## Inputs\n"
        "- Stage 01 `ia.md`\n"
        "- `setup/client.md` stack + content + host\n\n"
        "## Process\n"
        "1. Create the app repo (Astro or Next as selected).\n"
        "2. Mirror IA in routes / content collections (or CMS schema stubs).\n"
        "3. Add GitHub Actions **CI** from `_config/ci-cd.md` (test + production build). CD job can be a stub until stage 07.\n"
        "4. `.gitignore` includes `dist/`, `.next/`, and any ICM `output/`.\n"
        "5. Write `repo` into `setup/client.md`.\n\n"
        "## Outputs\n"
        "- `scaffold-notes.md` — what was created\n"
        "- `workflow.md` — branch + Actions summary\n\n"
        "## Stop\n"
        "No visual design. No feature UI beyond a hello route that builds.\n",
    ),
    (
        "03-ux-ui",
        "UX / UI",
        "## Inputs\n"
        "- Stage 01 IA\n"
        "- Figma mode from `setup/client.md` (full-handoff | key-screens)\n"
        "- Brand notes (not in `_config/`)\n\n"
        "## Process\n"
        "1. Full handoff: produce or receive a complete Figma file mapped to IA templates.\n"
        "2. Key-screens: Figma for home + 1–2 inner templates; remaining screens specified as tokens + notes for code.\n"
        "3. Record component list (nav, card, form, footer) for stage 04.\n\n"
        "## Outputs\n"
        "- `figma.md` — link + which screens are source of truth\n"
        "- `components.md` — list for build\n"
        "- optional screenshots in `references/` (keep under size; prefer the Figma URL)\n\n"
        "## Stop\n"
        "Do not implement production pages here.\n",
    ),
    (
        "04-build",
        "Build",
        "## Inputs\n"
        "- Stage 02 repo\n"
        "- Stage 03 Figma + component list\n"
        "- `setup/client.md` content source\n\n"
        "## Process\n"
        "1. Create a **feature branch** (`feat/<short-name>`). One feature per branch when the change is large.\n"
        "2. Implement against IA + Figma. Content from markdown or the chosen CMS.\n"
        "3. Keep the production build green locally before handing to 05.\n"
        "4. Repeat this stage for the next feature; do not pile unrelated features on one branch if review will suffer.\n\n"
        "## Outputs\n"
        "- `branch.md` — branch name, commits, what shipped in this slice\n"
        "- `build-notes.md` — leftover gaps\n\n"
        "## Stop\n"
        "No merge. No production deploy. QA is the next stage.\n",
    ),
    (
        "05-qa",
        "QA",
        "## Inputs\n"
        "- Stage 04 branch\n"
        "- `_config/qa-checklist.md`\n\n"
        "## Process\n"
        "1. Walk the checklist. Design, function, and accessibility are **one gate**.\n"
        "2. File failures as a punch list. Blockers stay in this stage.\n"
        "3. Re-run after fixes.\n\n"
        "## Outputs\n"
        "- `qa-report.md` — pass/fail per checklist item\n"
        "- `punch-list.md` — open items (empty means go to 06)\n\n"
        "## Stop\n"
        "Do not open the PR until blockers are gone (or explicitly waived in the report).\n",
    ),
    (
        "06-ci-pr",
        "CI + PR",
        "## Inputs\n"
        "- Green stage 05\n"
        "- `_config/ci-cd.md`\n\n"
        "## Process\n"
        "1. Open PR from the feature branch.\n"
        "2. GitHub Actions must **test** and **production-build**. Both required.\n"
        "3. Accept the PR **only if** CI is green.\n"
        "4. If CI fails: fix on the branch (treat as a return to 04/05), do not merge.\n\n"
        "## Outputs\n"
        "- `pr.md` — PR URL, CI run URLs, merge SHA\n\n"
        "## Stop\n"
        "Do not touch production. That is stage 07.\n",
    ),
    (
        "07-cd",
        "CD",
        "## Inputs\n"
        "- Merged main (or release branch) from stage 06\n"
        "- Host from `setup/client.md`\n\n"
        "## Process\n"
        "1. Deploy **staging** first. Smoke home + one inner path.\n"
        "2. Promote to production on Cloudflare, own VPS, or the client host.\n"
        "3. Confirm DNS / TLS. Write the live URL into `setup/client.md`.\n"
        "4. If production hiccups: roll back or fix forward; do not leave a half-deploy undocumented.\n\n"
        "## Outputs\n"
        "- `deploy.md` — staging URL, production URL, host, time\n"
        "- Done when the site is live.\n\n"
        "## Stop\n"
        "This is the last stage. New work starts a new feature at 04 (or a new client at setup).\n",
    ),
]

AGENTS_MD = """# Website workbench (ICM factory)

You are executing the Interpretable Context Methodology for **client website** work.

## Rules
- Read this file, then `CONTEXT.md`, then the current stage `CONTEXT.md` only.
- Do not load other stages unless the contract says to.
- Per-client facts live in `setup/client.md`. If a field is empty, stop and ask.
- Treat `stages/*/output/` as throwaway. Never commit it. Improve `_config/` and contracts instead.
- Stack is **Astro or Next**, host is **Cloudflare / own VPS or client host**, content is **markdown or headless**. Decide per client in setup.
- Feature work happens on a **feature branch**. CI (GitHub Actions) must **test and build** before a PR is accepted. CD runs only after merge.

## Stages
01 audit + IA → 02 scaffold → 03 UX/UI → 04 build (feature branch) → 05 QA (includes a11y) → 06 CI + PR → 07 CD.

## Factory vs run
Factory (`_config/`, this file, stage contracts): process and QA/a11y checklists.
Run (`setup/client.md`, `output/`): brand, content, stack, host, CMS answers.
"""

CONTEXT_MD = """# Workflow: client website

Goal: ship a **live site** for one client. Start from a brief **and** (when they have one) the existing live site.

## Setup (every run)
Fill `setup/client.md` before stage 01. Required: client name, start mode (brief / live rebuild / both), stack, host, content source.

## Pipe
1. `01-audit-ia` — audit + sitemap / information architecture
2. `02-scaffold` — repo, routes, content model, workflow
3. `03-ux-ui` — Figma: full handoff **or** key screens, rest in code
4. `04-build` — implement on a feature branch
5. `05-qa` — design + function + accessibility (combined)
6. `06-ci-pr` — GitHub Actions: tests + production build must pass, then PR accept
7. `07-cd` — deploy staging then production (avoid prod hiccups)

## Done
The site is live on the chosen host. Stage 07 output names the URL.

## Do not
Commit `output/`. Mix factory checklists with one client's brand. Accept a PR on a red build.
"""

WORKFLOW_MAP_MD = """# Website workbench — workflow map

Generated by forge-interview apply (FM-304). Factory for **process + QA/a11y**. Brand and content are per client.

```
setup/client.md
        │
        v
01  Audit + IA  ──────── first artifact: site audit + sitemap/IA
        │
        v
02  Scaffold / workflow  ── repo, routes, content model
        │
        v
03  UX / UI  ────────────── Figma (full or key screens)
        │
        v
04  Build  ──────────────── feature branch (each feature can be its own 04-run)
        │
        v
05  QA  ─────────────────── design + function + a11y (combined)
        │
        v
06  CI + PR  ────────────── GitHub Actions: test AND build must succeed
        │                     PR accepted only if green
        v
07  CD  ─────────────────── staging, then production
        │
        v
      LIVE SITE
```

## Per-client variables (not factory)
- Brand, copy, imagery
- Stack: Astro **or** Next
- Host: Cloudflare / own VPS **or** client host
- Content: markdown collections **or** headless CMS; "keep old CMS" is an intake question

## Feature-branch rule
A feature is not "done in 04" until 05 is clean **and** 06 is green. Do not merge on a failed build.
"""


CONFIG_README = """# Factory (Layer 3)

Durable. Commit this. Edit here when the **process** changes.

- `qa-checklist.md` — design + function + a11y (combined per interview)
- `ci-cd.md` — GitHub Actions gates: test, build, then CD
- `intake-questions.md` — questions to ask before a run

Do not put a client's hex codes, logos, or copy here.
"""

INTAKE_QUESTIONS = """# Intake (ask before stage 01)

1. Brief, live rebuild, or both?
2. Existing URL and who owns DNS / hosting today?
3. Astro or Next for this client?
4. Cloudflare / own VPS, or their host?
5. Markdown collections, headless CMS, or keep the old CMS?
6. Figma: full file or key screens only?
7. What does "shipped live" mean (domain, staging first, analytics)?
8. Accessibility bar (default WCAG 2.2 AA)?
"""

QA_CHECKLIST = """# QA (design + function + a11y)

Run in stage 05. Failures block stage 06.

## Design
- [ ] Matches Figma key screens (or signed exceptions)
- [ ] Type, space, color consistent with brand notes
- [ ] Breakpoints: mobile, tablet, desktop
- [ ] Empty / error / loading states exist

## Function
- [ ] Primary user paths complete (nav, forms, CTAs)
- [ ] Forms validate and show errors
- [ ] 404 and required legal pages exist
- [ ] No console errors on primary paths
- [ ] Images have dimensions / no layout shift on hero

## Accessibility (combined here)
- [ ] Keyboard: all interactive elements reachable, visible focus
- [ ] Skip link or equivalent landmark nav
- [ ] Headings in order; one h1 per page
- [ ] Images: meaningful alt or empty alt if decorative
- [ ] Form labels + error text associated
- [ ] Color contrast ~ WCAG 2.2 AA
- [ ] `prefers-reduced-motion` respected where motion is decorative
- [ ] Target size usable on touch
- [ ] Page `lang` set; title unique
"""

CI_CD = """# CI / CD (GitHub Actions)

Default runner: GitHub Actions. Feature branch → CI → PR → CD.

## CI (must pass before PR accept)
1. Install + lint (if the stack has one)
2. Unit / component tests if the repo has them
3. **Production build must succeed** (`astro build` or `next build`)
4. Optional: Playwright smoke on preview

A red build means the PR is not accepted. No "merge anyway."

## CD (after merge only)
1. Deploy **staging** (or preview URL) first
2. Smoke the staging URL (home + one inner path)
3. Promote to **production** on the host from `setup/client.md`
4. Record the live URL in `setup/client.md`

## Host adapters (choose one per client)
- cloudflare: Pages / Workers for Astro or Next
- own-vps: build artifact + reverse proxy
- client-host: hand them the artifact or connect their pipeline; still require green CI
"""

SETUP_README = """# Per-run setup

`client.md` is written by forge-interview from answers JSON. Stage 01 refuses to start if `client.md` is missing.

Do not put brand tokens in `_config/`.
"""

SHARED_README = """# Shared (optional)

Cross-stage notes that are still factory (rare). Prefer `_config/` for process and `setup/` for the client.
"""

OUTPUT_GITIGNORE = "*\n!.gitignore\n!.gitkeep\n"

BRAND_VAULT_CONTEXT = """# Brand Vault

Brand identity and voice rules for this workspace. Agents load specific sections as directed by stage CONTEXT.md files.

## Files

| File | Load When |
|------|-----------|
| `identity.md` | Understanding who you are writing for |
| `voice-rules.md` | Writing any content |

Do not put brand tokens in `_config/`.
"""

BRAND_VAULT_IDENTITY = """# Brand Identity

## One-Sentence Brand

(fill)

## Audience

**Primary audience:** (fill)

## Positioning

(fill)

## Content Mission

(fill)
"""

BRAND_VAULT_VOICE = """# Voice Rules

## Voice Rules

(fill)

## What the Voice Is NOT

(fill)
"""

STACK_ASTRO = """# Stack reference — Astro

Selected at interview. Stage 02 scaffold uses Astro for the app repo.
Fill host/content details from `setup/client.md`.
"""

STACK_NEXT = """# Stack reference — Next

Selected at interview. Stage 02 scaffold uses Next for the app repo.
Fill host/content details from `setup/client.md`.
"""

CONTENT_MODEL = """# Content model (stub)

Interview selected headless or keep-old CMS. Expand collections / schema here before stage 02 closes.
"""

# Banned runtime copy sources (path fragments). Generator never copies these trees.
_BANNED_COPY_MARKERS = (
    "icm-website-workbench",
    "ICM-reuseable-template",
    "ICM/workspaces",
    "icm/workspaces",
)


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def write_text(path: Path, body: str, *, clobber: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not clobber and path.exists():
        return
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")



def assert_not_banned_copy_source(path: Path | None) -> None:
    """Defense in depth — apply never treats Captain trees as copy sources."""
    if path is None:
        return
    text = str(path)
    for marker in _BANNED_COPY_MARKERS:
        if marker in text:
            die(
                f"refusing copy/source path containing banned marker {marker!r}: {path} "
                "(FM-304: generate only; Captain SoT is reference-while-coding, not runtime dump)"
            )


def render_client_md(answers: dict) -> str:
    a = answers
    lines = [
        "# Client (from forge-interview)",
        "",
        f"- Client name: {a.get('client_name', '')}",
        f"- Start mode: {a.get('start_mode', '')}",
        f"- Existing site URL (if any): {a.get('existing_url', '')}",
        f"- Brief / goals (what \"live\" means for them): {a.get('shipped_live', '')}",
        f"- Stack: {a.get('stack', '')}",
        f"- Host: {a.get('host', '')}",
        f"- Host notes (account, domain, DNS): {a.get('host_notes', a.get('dns_owner', ''))}",
        f"- Content: {a.get('content', '')}",
        f"- CMS name / API (if headless or keep-old): {a.get('cms', '')}",
        f"- Figma: {a.get('figma', '')}",
        f"- Brand notes (or link to a brand folder **outside** `_config/`): {a.get('brand_notes', '')}",
        f"- Accessibility target: {a.get('a11y', 'WCAG 2.2 AA')}",
    ]
    # Optional deep probes (FM-325 L5+) — only when answered
    for key, label in (
        ("redirect_strategy", "Redirect strategy"),
        ("seo_equity_notes", "SEO equity notes"),
        ("cms_lockin_risk", "CMS lock-in risk"),
        ("staging_hostname", "Staging hostname"),
        ("analytics_owner", "Analytics owner"),
    ):
        if a.get(key) not in (None, ""):
            lines.append(f"- {label}: {a.get(key)}")
    if a.get("experience_level") is not None:
        lines.append(f"- Experience level: {a.get('experience_level')}")
    if a.get("pack_id") or a.get("pack_version"):
        lines.append(
            f"- Session pack: {a.get('pack_id', '')}@{a.get('pack_version', '')}"
        )
    lines.extend(
        [
            "- Repo (empty until stage 02):",
            "- Production URL (empty until stage 07):",
            "",
        ]
    )
    return "\n".join(lines)


def pack_yaml_path(pack_id: str = "website", pack_version: str = "v1") -> Path:
    return Path(__file__).resolve().parent / "packs" / pack_id / f"{pack_version}.yaml"


def assert_pack_has_level(pack_path: Path, level_i: int) -> None:
    """Require explicit levels[\"N\"] for N in 0..5 (no clamp). Light parse — no PyYAML."""
    if not pack_path.is_file():
        die(f"pack not found: {pack_path}")
    body = pack_path.read_text(encoding="utf-8")
    # Collect quoted level keys under a top-level `levels:` block.
    keys: set[str] = set()
    in_levels = False
    for line in body.splitlines():
        if re.match(r"^levels:\s*$", line):
            in_levels = True
            continue
        if in_levels:
            if re.match(r"^[A-Za-z_][\w-]*:\s*", line) and not line.startswith(" "):
                break
            m = re.match(r'^\s+"(\d+)":\s*$', line)
            if m:
                keys.add(m.group(1))
    missing = [str(i) for i in range(6) if str(i) not in keys]
    if missing:
        die(f"pack {pack_path} missing explicit level keys: {missing}")
    if str(level_i) not in keys:
        die(f"pack {pack_path} has no levels[{level_i!r}] entry")


def normalize_pack_meta(answers: dict, product: str) -> dict:
    """Ensure website answers carry pack pointer fields when experience_level set.

    Keeps raw HIL experience_level (0-5). Does not rewrite mid levels to endpoints.
    Interview resolves vocab/depth/probes from pack levels[str(level)].
    """
    out = dict(answers)
    if product != "website":
        return out
    level = out.get("experience_level")
    if level is None or level == "":
        return out
    if type(level) is int:
        level_i = level
    elif isinstance(level, str) and level.isdigit():
        level_i = int(level)
    else:
        die(f"experience_level must be integer 0-5, got {level!r}")
    if level_i < 0 or level_i > 5:
        die(f"experience_level must be integer 0-5, got {level!r}")

    out["experience_level"] = level_i  # persist raw; never alias 1→0 / 3→5
    out.setdefault("pack_id", "website")
    out.setdefault("pack_version", "v1")
    pack_path = pack_yaml_path(str(out["pack_id"]), str(out["pack_version"]))
    assert_pack_has_level(pack_path, level_i)
    return out


def write_session_expert_pointer(target: Path, answers: dict) -> None:
    """Optional setup/session-expert.md — id/version/level only (never pack body)."""
    level = answers.get("experience_level")
    pack_id = answers.get("pack_id")
    pack_version = answers.get("pack_version")
    if level is None or not pack_id:
        return
    body = (
        "# Session expert (pointer)\n\n"
        "Interview loaded a domain pack into the **session** as expert context.\n"
        "This file is a pointer only — pack body is not dumped into the workspace.\n\n"
        f"- pack_id: `{pack_id}`\n"
        f"- pack_version: `{pack_version or ''}`\n"
        f"- experience_level: `{level}`\n"
        f"- pack_path: `skills/forge-interview/packs/{pack_id}/{pack_version or 'v1'}.yaml`\n"
    )
    write_text(binder(target) / "setup" / "session-expert.md", body)

def _flag(val: object) -> bool:
    if val is True:
        return True
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _declined(val: object) -> bool:
    if val is False:
        return True
    if isinstance(val, str):
        return val.strip().lower() in {"0", "false", "no", "n", "skip", "off"}
    return False


def is_overlay(answers: dict | None) -> bool:
    mode = str((answers or {}).get("mode") or "").strip().lower()
    return mode in {"overlay", "brownfield"}


_STAGE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def resolve_stages(answers: dict, cli_stages: str) -> list[str]:
    """Stages the interview invented for this project win; CLI value is the fallback.

    No type-to-stages table here: the interviewing agent infers the type and
    names the stages, apply lays exactly what it is handed.
    """
    raw = answers.get("stages")
    if raw is None:
        return [s.strip() for s in cli_stages.split(",") if s.strip()]
    if not isinstance(raw, list):
        die(f"answers stages must be a list of slugs, got {raw!r}")
    stages = [str(s).strip() for s in raw]
    if not stages:
        die("answers stages is empty - name the stages from the interview or drop the key")
    for slug in stages:
        if not _STAGE_SLUG.match(slug):
            die(f"answers stages entry is not a slug: {slug!r}")
    return stages


ICM_POINTER_START = "<!-- forge-icm:start -->"
ICM_POINTER_END = "<!-- forge-icm:end -->"


def spec_pointer_line(target: Path, answers: dict, forge_root: Path) -> str | None:
    if not want_spec(answers):
        return None
    path = spec_out_path(target, answers, forge_root)
    try:
        shown = path.relative_to(target).as_posix()
        return f"- Spec: `{shown}`."
    except ValueError:
        shown = path.relative_to(forge_root).as_posix()
        return f"- Spec: Forge `{shown}`."


def icm_pointer_block(target: Path, answers: dict, forge_root: Path) -> str:
    ptype = str(answers.get("project_type") or "").strip()
    made = f"an ICM binder ({ptype})" if ptype else "an ICM binder"
    lines = [
        ICM_POINTER_START,
        "## ICM layer",
        "",
        f"This repo carries {made} generated by forge-interview.",
        "",
        "- Read `forge/AGENTS.md`, then `forge/CONTEXT.md`, then the current stage `CONTEXT.md` under `forge/stages/` - nothing else.",
        "- Interview answers: `forge/setup/answers.json`.",
    ]
    spec_line = spec_pointer_line(target, answers, forge_root)
    if spec_line:
        lines.append(spec_line)
    lines.extend(
        [
            "- Existing project files stay yours. ICM documents the work; it does not edit `src/`.",
            ICM_POINTER_END,
        ]
    )
    return "\n".join(lines)


def attach_icm_pointer(target: Path, answers: dict, forge_root: Path) -> None:
    """Root AGENTS.md points at forge/. Create a thin file when missing."""
    agents = target / "AGENTS.md"
    block = icm_pointer_block(target, answers, forge_root)
    if not agents.is_file():
        title = str(answers.get("project_type") or answers.get("client_name") or target.name)
        write_text(agents, f"# {title}\n\n{block}\n")
        return
    text = agents.read_text(encoding="utf-8")
    start = text.find(ICM_POINTER_START)
    end = text.find(ICM_POINTER_END)
    if start != -1 and end > start:
        text = text[:start] + block + text[end + len(ICM_POINTER_END) :]
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    write_text(agents, text)


def want_spec(answers: dict) -> bool:
    """Write the spec unless they said no. Missing keys still write."""
    if _declined(answers.get("write_spec")) or _declined(answers.get("spec")):
        return False
    return True



def spec_out_path(target: Path, answers: dict, forge_root: Path) -> Path:
    dest = str(answers.get("spec_dest") or "target").strip().lower()
    raw = str(answers.get("spec_slug") or answers.get("client_name") or target.name)
    slug = "".join(ch if ch.isalnum() else "-" for ch in raw.lower()).strip("-") or "spec"
    if dest == "forge":
        return forge_root / "specs" / f"{slug}.md"
    return target / "docs" / "spec.md"


def write_spec(target: Path, answers: dict, product: str, forge_root: Path) -> Path | None:
    if not want_spec(answers):
        return None
    path = spec_out_path(target, answers, forge_root)
    title = str(
        answers.get("spec_title")
        or answers.get("client_name")
        or answers.get("project_type")
        or target.name
    )
    mode = str(answers.get("mode") or "greenfield")
    problem = str(
        answers.get("spec_problem")
        or answers.get("what")
        or answers.get("shipped_live")
        or answers.get("goal")
        or "(from interview)"
    ).strip()

    extra_oos = str(answers.get("spec_out_of_scope") or "").strip()
    oos = [
        "- Feature build after apply",
        "- Workbench or template copytree",
    ]
    if extra_oos:
        oos.append(f"- {extra_oos}")
    solution = str(
        answers.get("spec_solution")
        or f"ICM BASE generated at `{target}` ({product}, {mode})."
    )
    body = "\n".join(
        [
            f"# {title}",
            "",
            "## Problem",
            problem,
            "",
            "## Solution",
            solution,
            "",
            "## Scope",
            f"- Product type: {answers.get('project_type') or product}",
            f"- Mode: {mode}",
            f"- Stack: {answers.get('stack') or ''}",
            f"- Host: {answers.get('host') or ''}",
            "",
            "## Out of scope",
            *oos,
            "",
            "## Interview",
            "```json",
            json.dumps(answers, indent=2, sort_keys=True).rstrip(),
            "```",
            "",
        ]
    )
    write_text(path, body)
    return path




def make_stage_dir(stage_dir: Path, title: str, body: str) -> None:
    (stage_dir / "references").mkdir(parents=True, exist_ok=True)
    (stage_dir / "output").mkdir(parents=True, exist_ok=True)
    write_text(stage_dir / "references" / ".gitkeep", "")
    write_text(stage_dir / "output" / ".gitkeep", "")
    write_text(stage_dir / "output" / ".gitignore", OUTPUT_GITIGNORE)
    write_text(stage_dir / "CONTEXT.md", f"# Stage — {title}\n\n{body}")


def render_website_agents(answers: dict) -> str:
    client = answers.get("client_name") or "this client"
    return (
        "# Website ICM workspace\n\n"
        f"Generated by `/forge-interview` for **{client}**.\n\n"
        "You are executing the Interpretable Context Methodology for **client website** work.\n\n"
        "## Rules\n"
        "- Read this file, then `CONTEXT.md`, then the current stage `CONTEXT.md` only.\n"
        "- Paths in this folder are relative to `forge/`. Product code lives at the repo root, not here.\n"
        "- Do not load other stages unless the contract says to.\n"
        "- Per-client facts live in `setup/client.md` and `setup/answers.json`. If a field is empty, stop and ask.\n"
        "- Treat `stages/*/output/` as throwaway. Never commit it. Improve `_config/` and contracts instead.\n"
        "- Stack is **Astro or Next**, host is **Cloudflare / own VPS or client host**, content is **markdown or headless**. Decide per client in setup.\n"
        "- Feature work happens on a **feature branch**. CI (GitHub Actions) must **test and build** before a PR is accepted. CD runs only after merge.\n\n"
        "## Stages\n"
        "01 audit + IA → 02 scaffold → 03 UX/UI → 04 build (feature branch) → 05 QA (includes a11y) → 06 CI + PR → 07 CD.\n\n"
        "## Factory vs run\n"
        "Factory (`_config/`, this file, stage contracts): process and QA/a11y checklists.\n"
        "Run (`setup/client.md`, `setup/answers.json`, `output/`): brand, content, stack, host, CMS answers.\n"
    )


def render_website_context(answers: dict) -> str:
    client = answers.get("client_name") or "(fill)"
    stack = answers.get("stack") or "(fill)"
    host = answers.get("host") or "(fill)"
    content = answers.get("content") or "(fill)"
    start = answers.get("start_mode") or "(fill)"
    return (
        "# Workflow: client website\n\n"
        f"Goal: ship a **live site** for **{client}**. "
        "Start from a brief **and** (when they have one) the existing live site.\n\n"
        "## Setup (every run)\n"
        "Fill `setup/client.md` before stage 01. Required: client name, start mode "
        "(brief / live rebuild / both), stack, host, content source.\n\n"
        "## Interview lock\n"
        f"- Start mode: `{start}`\n"
        f"- Stack: `{stack}`\n"
        f"- Host: `{host}`\n"
        f"- Content: `{content}`\n"
        "- Answers file: `setup/answers.json`\n\n"
        "## Pipe\n"
        "1. `01-audit-ia` — audit + sitemap / information architecture\n"
        "2. `02-scaffold` — repo, routes, content model, workflow\n"
        "3. `03-ux-ui` — Figma: full handoff **or** key screens, rest in code\n"
        "4. `04-build` — implement on a feature branch\n"
        "5. `05-qa` — design + function + accessibility (combined)\n"
        "6. `06-ci-pr` — GitHub Actions: tests + production build must pass, then PR accept\n"
        "7. `07-cd` — deploy staging then production (avoid prod hiccups)\n\n"
        "## Done\n"
        "The site is live on the chosen host. Stage 07 output names the URL.\n\n"
        "## Do not\n"
        "Commit `output/`. Mix factory checklists with one client's brand. Accept a PR on a red build.\n"
        "Do not clone Captain SoT workbench trees into this workspace — this tree was generated from interview answers.\n"
    )


def binder(target: Path) -> Path:
    """Workflow home. --target stays the project root."""
    return target / "forge"


def generate_website_base(target: Path, answers: dict) -> None:
    """Materialize website ICM BASE under forge/ (no tree dump)."""
    home = binder(target)
    home.mkdir(parents=True, exist_ok=True)
    clobber = not is_overlay(answers)
    write_text(home / "AGENTS.md", render_website_agents(answers), clobber=clobber)
    write_text(home / "CONTEXT.md", render_website_context(answers), clobber=clobber)
    write_text(home / "workflow-map.md", WORKFLOW_MAP_MD, clobber=clobber)

    banner = (
        "<!-- generated by forge-interview apply_icm_base.py — not a SoT copy -->\n\n"
    )
    write_text(home / "_config" / "README.md", banner + CONFIG_README)
    write_text(home / "_config" / "intake-questions.md", banner + INTAKE_QUESTIONS)
    write_text(home / "_config" / "qa-checklist.md", banner + QA_CHECKLIST)
    write_text(home / "_config" / "ci-cd.md", banner + CI_CD)

    write_text(
        home / "setup" / "README.md",
        "# Setup\n\nPer-run answers live here (`client.md`, `answers.json`).\n",
    )
    write_text(
        home / "shared" / "README.md",
        "# Shared\n\nCross-stage notes generated with this ICM workspace.\n",
    )

    for slug, title, body in WEBSITE_STAGES:
        note = (
            f"_Generated stage stub (`{slug}`) from forge-interview. "
            "Edit freely; Captain workbench is reference-only._\n\n"
        )
        make_stage_dir(home / "stages" / slug, title, note + body)


def render_project_brief(answers: dict) -> str:
    """Thin generic brief from enough-slots (FM-606). Not a template dump."""
    notes = answers.get("notes") or answers.get("freeform") or ""
    if isinstance(notes, list):
        notes = "\n".join(str(n) for n in notes)
    return (
        "# Project brief\n\n"
        f"- Type: {answers.get('project_type', '')}\n"
        f"- What: {answers.get('what', '')}\n"
        f"- Who: {answers.get('who', '')}\n"
        f"- Done: {answers.get('done', '')}\n"
        f"- Constraints: {answers.get('constraints', '')}\n"
        f"- Notes: {notes}\n"
    )


def generate_generic_base(target: Path, stages: list[str], answers: dict | None = None) -> None:
    """Minimal ICM spine under forge/ — generated blanks, not a product workspace clone."""
    home = binder(target)
    home.mkdir(parents=True, exist_ok=True)
    answers = answers or {}
    clobber = not is_overlay(answers)
    write_text(
        home / "AGENTS.md",
        "# ICM workspace\n\nFolder structure is the workflow architecture. "
        "Read this file, then CONTEXT.md, then the current stage CONTEXT.md only.\n"
        "Paths in this folder are relative to `forge/`. The project lives at the repo root, not in this folder.\n",
        clobber=clobber,
    )
    what = answers.get("what") or answers.get("goal") or answers.get("client_name") or "(fill from interview)"
    who = answers.get("who") or ""
    done = answers.get("done") or ""
    constraints = answers.get("constraints") or ""
    ptype = answers.get("project_type") or ""
    write_text(
        home / "CONTEXT.md",
        f"# Workflow\n\nGoal: {what}\n\n"
        f"- Type: {ptype}\n"
        f"- Who: {who}\n"
        f"- Done: {done}\n"
        f"- Constraints: {constraints}\n\n"
        "Fill setup before stage 01. Answers: `setup/answers.json`.\n",
        clobber=clobber,
    )
    write_text(
        home / "workflow-map.md",
        "# Workflow map\n\n"
        f"- What: {what}\n"
        f"- Type: {ptype}\n"
        f"- Who: {who}\n"
        f"- Done: {done}\n"
        f"- Constraints: {constraints}\n",
        clobber=clobber,
    )

    write_text(home / "_config" / "README.md", "# Factory\n\nDurable process docs. No client brand here.\n")
    write_text(home / "setup" / "README.md", "# Setup\n\nPer-run answers live here.\n")
    write_text(home / "setup" / "questionnaire.md", "# Questionnaire\n\n(fill)\n")
    write_text(home / "shared" / "README.md", "# Shared\n")
    for slug in stages:
        make_stage_dir(
            home / "stages" / slug,
            slug,
            "## Inputs\n\n## Process\n\n## Outputs\n\n## Stop\n",
        )


def apply_gates(target: Path, answers: dict) -> None:
    home = binder(target)
    if answers.get("brand_vault"):
        bv = home / "brand-vault"
        write_text(bv / "CONTEXT.md", BRAND_VAULT_CONTEXT)
        write_text(bv / "identity.md", BRAND_VAULT_IDENTITY)
        write_text(bv / "voice-rules.md", BRAND_VAULT_VOICE)

    stack = (answers.get("stack") or "").strip().lower()
    if stack in ("astro", "next"):
        scaffold = home / "stages" / "02-scaffold"
        if scaffold.is_dir():
            ref = scaffold / "references" / f"stack-{stack}.md"
            write_text(ref, STACK_ASTRO if stack == "astro" else STACK_NEXT)

    content = (answers.get("content") or "").strip().lower()
    if content in ("headless", "keep-old-cms", "keep_old_cms"):
        write_text(home / "shared" / "content-model.md", CONTENT_MODEL)

    drop = answers.get("drop_stages") or []
    if isinstance(drop, str):
        drop = [s.strip() for s in drop.split(",") if s.strip()]
    for slug in drop:
        path = home / "stages" / slug
        if path.is_dir():
            shutil.rmtree(path)

    skills = answers.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    for name in skills:
        safe = name.replace("/", "-").strip()
        if not safe:
            continue
        skill_dir = home / "skills" / safe
        write_text(
            skill_dir / "SKILL.md",
            f"---\nname: {safe}\ndescription: Domain skill bundled at interview.\n---\n\n"
            f"# {safe}\n\n(fill — captain/domain SoT; interview only gated the folder)\n",
        )


def apply_software_sibling(target: Path, answers: dict) -> None:
    """Opt-in sibling rails — generated stubs only (no template tree dump)."""
    if not answers.get("software_rails"):
        return
    sibling = target / "forge-software"
    sibling.mkdir(parents=True, exist_ok=True)
    mode = (answers.get("software_mode") or "greenfield").strip().lower()
    picks = {
        "task_runner": answers.get("task_runner", ""),
        "host": answers.get("software_host", answers.get("sw_host", "")),
        "data": answers.get("data", ""),
        "idp": answers.get("idp", ""),
        "mode": mode,
    }
    write_text(
        sibling / "README.md",
        "# Forge software rails (sibling)\n\n"
        "Generated at interview. Sibling to ICM — not a substitute. "
        "Fill AGENTS/STACK; do not dump product templates here.\n",
    )
    write_text(
        sibling / "AGENTS.md",
        f"# Software rails ({mode})\n\nInterview-gated sibling. Implement against STACK.md.\n",
    )
    write_text(
        sibling / "STACK.md",
        "# Software stack (interview)\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in picks.items())
        + "\n\nSibling to ICM — not a substitute.\n",
    )


def load_answers(path: Path | None, inline: str | None) -> dict:
    if inline:
        return json.loads(inline)
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", required=True, help="Destination workspace path")
    p.add_argument("--product", choices=("website", "generic"), default="website")
    p.add_argument(
        "--workbench",
        type=Path,
        default=None,
        help="Ignored (FM-304). Kept for CLI compat; never used as a copy source.",
    )
    p.add_argument(
        "--icm-core",
        type=Path,
        default=None,
        help="Ignored (FM-304). Kept for CLI compat; never used as a copy source.",
    )
    p.add_argument("--forge-root", type=Path, default=FORGE_ROOT)
    p.add_argument("--answers", type=Path, help="JSON answers file")
    p.add_argument("--answers-json", help="Inline JSON answers")
    p.add_argument(
        "--generic-stages",
        default="01-intake,02-discovery,03-build,04-review",
        help="Comma stage slugs for generic product",
    )
    args = p.parse_args()
    answers = load_answers(args.answers, args.answers_json)
    answers = normalize_pack_meta(answers, args.product)
    target = Path(args.target).expanduser().resolve()

    # Refuse if caller tries to point banned trees at us as sources.
    assert_not_banned_copy_source(args.workbench)
    assert_not_banned_copy_source(args.icm_core)

    home = binder(target)

    if args.product == "website":
        generate_website_base(target, answers)
        write_text(home / "setup" / "client.md", render_client_md(answers))
        write_session_expert_pointer(target, answers)
    else:
        refusal = _grill.structure_refusal(answers)
        if refusal:
            die(refusal)
        stages = resolve_stages(answers, args.generic_stages)
        generate_generic_base(target, stages, answers)
        write_text(home / "setup" / "project-brief.md", render_project_brief(answers))

    forge_root = Path(args.forge_root).expanduser().resolve()
    attach_icm_pointer(target, answers, forge_root)

    # Durable machine-readable answers (alongside human client.md / brief).
    # Includes experience_level / pack_id / pack_version when website gate ran.
    write_text(
        home / "setup" / "answers.json",
        json.dumps(answers, indent=2, sort_keys=True) + "\n",
    )

    apply_gates(target, answers)
    apply_software_sibling(target, answers)
    spec_path = write_spec(target, answers, args.product, forge_root)

    print(f"generated ICM BASE ({args.product}) → {target}")
    print(
        "gates:",
        json.dumps(
            {
                k: answers.get(k)
                for k in (
                    "brand_vault",
                    "stack",
                    "content",
                    "drop_stages",
                    "skills",
                    "software_rails",
                    "experience_level",
                    "pack_id",
                    "pack_version",
                    "write_spec",
                    "mode",
                )
            },
            sort_keys=True,
        ),
    )
    if spec_path is not None:
        print(f"spec → {spec_path}")
    print("stop: no feature build; no template dump")



if __name__ == "__main__":
    main()
