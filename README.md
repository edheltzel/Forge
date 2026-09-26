```
███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

# Forge

> [!NOTE]
> EdHeltzel's ICM Rails

Forge is the rails for agentic ICM workspaces you keep in `~/Developer`. It is a framework, not the product you are building.

`/forge-interview` runs an adaptive invent-and-branch until enough-to-structure, then **generates** a thin generic ICM BASE from answers (no workbench/template copytree). Software rails are an optional later pack — not the core interview.

First run: [Getting started](docs/getting-started.md).

## Spec

Apply writes `docs/spec.md` unless you say you do not want one. Forge does not ask. If you say no, the agent sets `write_spec` to false and skips the file.

The file is a handoff, not the app and not the workflow. Sections: Problem, Solution, Scope, Out of scope, Interview. Problem is your `spec_problem` if you gave one, otherwise `what`. Solution is a stock sentence unless you set `spec_solution`. `done` is only inside the Interview JSON. There is no Done section.

`spec_dest: forge` writes the same file to this repo at `specs/<slug>.md` instead of the target.

## Greenfield

A new folder. Forge asks until it has what, who, done, and constraints, then lays the workflow and stops. It does not build the app.

```mermaid
flowchart TD
  A[You say what you want to make] --> B[Forge asks one question]
  B --> C{Four facts filled?}
  C -->|No| B
  C -->|Yes| D{Ready to structure it?}
  D -->|Not yet| B
  D -->|Yes| E[You name the new folder]
  E --> F[Write the workflow]
  E --> G[Write a short AGENTS.md at the root]
  E --> H[Write docs/spec.md]
  F --> K[Stop]
  G --> K
  H --> K
```

Say you do not want a spec and that last write is skipped.

The workflow lives in `forge/`. Root `AGENTS.md` only points there.

## Brownfield

An existing app. Forge reads `AGENTS.md`, `README.md`, and `docs/`, asks only what those files do not already say, and adds the workflow beside the code.

```mermaid
flowchart TD
  A[You point Forge at an existing project] --> B[Forge reads AGENTS.md, README, and docs]
  B --> C[Forge asks only what those files do not already say]
  C --> D{Four facts filled?}
  D -->|No| C
  D -->|Yes| E{Ready to structure it?}
  E -->|Not yet| C
  E -->|Yes| F[Add the workflow next to the app]
  E --> G{Root AGENTS.md already exists?}
  G -->|Yes| N[Append one pointer note]
  G -->|No| M[Write a short AGENTS.md that points at forge/]
  E --> H[Write docs/spec.md]
  F --> I[Stop. src/ is unchanged.]
  N --> I[Stop. src/ is unchanged.]
  M --> I
  H --> I
```

Your README and app stay. If `AGENTS.md` was already there, Forge appends one pointer note. If it was missing, Forge writes a short one. The workspace contract stays in `forge/`. Running apply twice replaces that note. It does not stack. Say you do not want a spec and `docs/spec.md` is skipped. `src/` is still untouched.

