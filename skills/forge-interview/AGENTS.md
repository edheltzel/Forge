# forge-interview

## Purpose

ICM-first interview skill for `/forge-interview`. Adaptive invent-and-branch until enough-to-structure, then generate a thin generic ICM BASE from answers (no SoT copytree). Domain-agnostic.

## Ownership

Parent: `skills/AGENTS.md`. Grill machine: `grill.py`. Apply helper: `apply_icm_base.py`.

## Local Contracts

- Home question, asked once before the opener. `home_mode` is `none`, `folder`, or `repo`. A `folder` or `repo` answer also saves `home_path` (resolved; must already exist and hold `AGENTS.md`; never created here), `home_pointer`, `home_pointer_text`, `home_skills_link`, `home_wiki` (`link`, `create`, or `no`), and `home_wiki_page`. An unclear answer saves nothing. A saved answer is reused with no question unless its path has vanished. Applied with `--home`: the home line, the wiki page (create never overwrites), and the `Shared skills:` and `Wiki:` lines in the forge-icm block.
- Folder docs: with `home_mode` folder or repo, apply adds or refreshes a `<!-- foundry-docs:start -->` block at the end of the project's AGENTS.md pointing at `<home_path>/docs/self-updating-docs.md`. `home_folder_docs` in answers.json records `on`, or `off` once the user deleted the block; a deleted block comes back only with `--add-folder-docs` ("add the folder-docs rule"). A missing rule file refuses the block. Never creates FOLDER.md or a docs/ tree. `--refresh-docs --home <home> --project <project>` refreshes only the block.
- Invent the next question from empty enough-slots. No fixed Q1–Q5 / core-8 product spine. No project-type menu.
- Enough-to-structure (day one): **what**, **who**, **done**, **constraints** all non-empty after trim. Ready-yes alone does not lay the binder.
- Offer ready gate only after gap check passes. Exact: "Are you ready for us to structure this project, or is there anything else you want to add?"
- Max **12** invent rounds after the opener. Past cap: chase empty slots only. Cap does not waive the gap check.
- Suggestions only when the human asks; ground in industry standards. No always-recommend.
- Typed pack floors (website 0–5 included) are a **hook for later**. Day one does not load packs as the interview spine. Never dump pack body into the target.
- Software four-pack is not this interview. Optional later pack branch only if they explicitly ask.
- No template dump / no copytree of workbench. Generate via mkdir + write.
- If an existing repo is already obvious from context, read its `AGENTS.md`, `README.md`, and `docs/` and do not re-ask those facts. Otherwise ask the four slots. Do not replace `src/`. Both modes keep an existing root `AGENTS.md` and add one marker-guarded pointer (`<!-- forge-icm:start -->`) aimed at `forge/`. If root `AGENTS.md` is missing, apply writes a thin one. A later apply replaces that block when both markers are still there. Before the exact ready question, say the workflow goes under `forge/` after they name the folder, that `docs/spec.md` will be written unless they refuse that write, and that an existing spec is replaced. Apply writes `docs/spec.md` unless `write_spec` is false in the answers before apply. The interview path sets that key explicitly. Setting the flag after apply does not skip a file already written. The pointer is written to `AGENTS.md`, not into `CONTEXT.md`. It names `docs/spec.md` only when that file is written, names Forge `specs/<slug>.md` when `spec_dest` is `forge`, and omits the spec line when they declined.
- The binder's shape comes from the interview: `project_type` and a `stages` slug list in answers, laid verbatim. No type-to-stages table in the generator. Absent `stages` falls back to the generic four; a non-list, empty, or non-slug `stages` refuses before anything is written.
- Generic apply refuses unless gap check passes and `ready` is yes. Persist slots in `forge/setup/answers.json` + `forge/setup/project-brief.md`. `--target` stays the project root.

## Work Guidance

- One question at a time. Their words on the page; map to slots behind the scenes.
- Infer project type privately. Do not force software menus.
- Do not invent weight training or self-learning marketing.

## Verification

- `python3 skills/forge-interview/grill.py --help`
- `python3 skills/forge-interview/apply_icm_base.py --help`
- `python3 skills/forge-interview/prove_fm606.py`
- `python3 skills/forge-interview/prove_fm325.py` (website apply / pack pointer — later typed pack, not the day-one grill)
- `python3 skills/forge-interview/prove_issue1.py` (issue 1: type-shaped greenfield, brownfield overlay, spec)
- `python3 skills/forge-interview/prove_home_question.py` (change 1: home question asked once and saved)
- `python3 skills/forge-interview/prove_add_pointer.py` (change 2: apply adds or refreshes this project's line in the home repo)
- `python3 skills/forge-interview/prove_remove_pointer.py` (change 3: `--remove-pointer` drops one line on request only)
- `python3 skills/forge-interview/prove_skills_link.py` (change 4: `home_skills_link` adds a text-only skills line inside the forge-icm block)
- `python3 skills/forge-interview/prove_wiki.py` (change 5: `home_wiki` create writes the page once and lists it; link adds the `Wiki:` line)
- `python3 skills/forge-interview/prove_pointer_note.py` (refreshing a home line keeps any note written after it)
- `python3 skills/forge-interview/prove_marker_lines.py` (block markers count only as whole lines; a marker quoted in prose is left alone)
- `python3 skills/forge-interview/prove_home_docs.py` (change 7: the foundry-docs block, refresh, drift, deletion, missing rule file, no FOLDER.md)
- `python3 skills/forge-interview/prove_snapshot.py` (change 0: generic apply on `fixtures/sample-project` and an empty folder matches `fixtures/snapshots/before/` byte for byte; a second apply on the same folders changes nothing; a fresh rerun matches; temp HOME left empty). `--update --reason "<why>"` writes `snapshots/after/` only; `snapshots/before/` is never rewritten.

## Child DOX Index

- packs/AGENTS.md — versioned domain pack contract (later hook)

