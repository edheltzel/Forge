#!/usr/bin/env python3
"""Apply ICM BASE from captain SoT, then gated folders from interview answers.

Captain folders remain layout SoT. This script copies the workbench (or builds a
minimal _core-shaped spine) and applies gates — it does not invent topology.

Does not build product features. Software rails are opt-in sibling only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKBENCH = Path(
    os.environ.get(
        "FORGE_ICM_WORKBENCH",
        "/Users/ed/Developer/ForgeTemplates/icm-website-workbench",
    )
)
DEFAULT_ICM_CORE = Path(
    os.environ.get(
        "FORGE_ICM_CORE",
        "/Users/ed/Developer/AI/Standards/ICM/_core",
    )
)

WEBSITE_BASE_FILES = [
    "AGENTS.md",
    "CONTEXT.md",
    "workflow-map.md",
    "README.md",
    ".gitignore",
]
WEBSITE_BASE_DIRS = ["_config", "setup", "shared", "stages"]

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


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")


def render_client_md(answers: dict) -> str:
    a = answers
    return "\n".join(
        [
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
            "- Repo (empty until stage 02):",
            "- Production URL (empty until stage 07):",
            "",
        ]
    )


def apply_website_base(target: Path, workbench: Path) -> None:
    if not workbench.is_dir():
        die(f"workbench SoT missing: {workbench}")
    target.mkdir(parents=True, exist_ok=True)
    for name in WEBSITE_BASE_FILES:
        src = workbench / name
        if not src.is_file():
            die(f"workbench missing file: {src}")
        copy_file(src, target / name)
    for name in WEBSITE_BASE_DIRS:
        src = workbench / name
        if not src.is_dir():
            die(f"workbench missing dir: {src}")
        copy_tree(src, target / name)


def apply_generic_base(target: Path, core: Path, stages: list[str]) -> None:
    """Minimal ICM spine from _core conventions — not a product workspace clone."""
    target.mkdir(parents=True, exist_ok=True)
    write_text(
        target / "AGENTS.md",
        "# ICM workspace\n\nFolder structure is the workflow architecture. "
        "Read this file, then CONTEXT.md, then the current stage CONTEXT.md only.\n",
    )
    write_text(
        target / "CONTEXT.md",
        "# Workflow\n\nGoal: (fill from interview). Fill setup before stage 01.\n",
    )
    write_text(target / "workflow-map.md", "# Workflow map\n\n(fill)\n")
    write_text(target / ".gitignore", "stages/*/output/*\n!stages/*/output/.gitkeep\n")
    (target / "_config").mkdir(exist_ok=True)
    write_text(target / "_config" / "README.md", "# Factory\n\nDurable process docs. No client brand here.\n")
    (target / "setup").mkdir(exist_ok=True)
    write_text(target / "setup" / "README.md", "# Setup\n\nPer-run answers live here.\n")
    write_text(target / "setup" / "questionnaire.md", "# Questionnaire\n\n(fill)\n")
    (target / "shared").mkdir(exist_ok=True)
    write_text(target / "shared" / "README.md", "# Shared\n")
    stage_tpl = core / "templates" / "stage-context-template.md"
    for slug in stages:
        stage_dir = target / "stages" / slug
        (stage_dir / "references").mkdir(parents=True, exist_ok=True)
        (stage_dir / "output").mkdir(parents=True, exist_ok=True)
        write_text(stage_dir / "references" / ".gitkeep", "")
        write_text(stage_dir / "output" / ".gitkeep", "")
        write_text(stage_dir / "output" / ".gitignore", "*\n!.gitignore\n!.gitkeep\n")
        if stage_tpl.is_file():
            copy_file(stage_tpl, stage_dir / "CONTEXT.md")
        else:
            write_text(
                stage_dir / "CONTEXT.md",
                f"# Stage — {slug}\n\n## Inputs\n\n## Process\n\n## Outputs\n\n## Stop\n",
            )


def apply_gates(target: Path, answers: dict) -> None:
    if answers.get("brand_vault"):
        bv = target / "brand-vault"
        write_text(bv / "CONTEXT.md", BRAND_VAULT_CONTEXT)
        write_text(bv / "identity.md", BRAND_VAULT_IDENTITY)
        write_text(bv / "voice-rules.md", BRAND_VAULT_VOICE)

    stack = (answers.get("stack") or "").strip().lower()
    if stack in ("astro", "next"):
        ref = target / "stages" / "02-scaffold" / "references" / f"stack-{stack}.md"
        if (target / "stages" / "02-scaffold").is_dir():
            write_text(ref, STACK_ASTRO if stack == "astro" else STACK_NEXT)

    content = (answers.get("content") or "").strip().lower()
    if content in ("headless", "keep-old-cms", "keep_old_cms"):
        write_text(target / "shared" / "content-model.md", CONTENT_MODEL)

    drop = answers.get("drop_stages") or []
    if isinstance(drop, str):
        drop = [s.strip() for s in drop.split(",") if s.strip()]
    for slug in drop:
        path = target / "stages" / slug
        if path.is_dir():
            shutil.rmtree(path)

    skills = answers.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    for name in skills:
        safe = name.replace("/", "-").strip()
        if not safe:
            continue
        skill_dir = target / "skills" / safe
        write_text(
            skill_dir / "SKILL.md",
            f"---\nname: {safe}\ndescription: Domain skill bundled at interview.\n---\n\n"
            f"# {safe}\n\n(fill — captain/domain SoT; interview only gated the folder)\n",
        )


def apply_software_sibling(target: Path, answers: dict, forge_root: Path) -> None:
    if not answers.get("software_rails"):
        return
    sibling = target / "forge-software"
    sibling.mkdir(parents=True, exist_ok=True)
    soft = forge_root / "templates" / "software"
    if soft.is_dir():
        copy_tree(soft, sibling / "software")
    mode = (answers.get("software_mode") or "greenfield").strip().lower()
    src = forge_root / "templates" / ("greenfield" if mode == "greenfield" else "brownfield")
    if src.is_dir():
        # Copy AGENTS/STACK markers only as sibling rails — not a product build.
        for name in ("AGENTS.md", "CLAUDE.md", "STACK.md", "README.md"):
            f = src / name
            if f.is_file():
                copy_file(f, sibling / name)
    picks = {
        "task_runner": answers.get("task_runner", ""),
        "host": answers.get("software_host", answers.get("sw_host", "")),
        "data": answers.get("data", ""),
        "idp": answers.get("idp", ""),
    }
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
    p.add_argument("--workbench", type=Path, default=DEFAULT_WORKBENCH)
    p.add_argument("--icm-core", type=Path, default=DEFAULT_ICM_CORE)
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
    target = Path(args.target).expanduser().resolve()

    if args.product == "website":
        apply_website_base(target, args.workbench.resolve())
        write_text(target / "setup" / "client.md", render_client_md(answers))
    else:
        stages = [s.strip() for s in args.generic_stages.split(",") if s.strip()]
        apply_generic_base(target, args.icm_core.resolve(), stages)
        write_text(
            target / "setup" / "project-brief.md",
            "# Project brief\n\n"
            + json.dumps(answers, indent=2, sort_keys=True)
            + "\n",
        )

    apply_gates(target, answers)
    apply_software_sibling(target, answers, args.forge_root.resolve())

    print(f"applied ICM BASE ({args.product}) → {target}")
    print("gates:", json.dumps({k: answers.get(k) for k in (
        "brand_vault", "stack", "content", "drop_stages", "skills", "software_rails"
    )}, sort_keys=True))
    print("stop: no feature build")


if __name__ == "__main__":
    main()
