# AGENTS.md

Entry point for AI coding agents (Claude Code, Copilot CLI, Cursor,
Codex CLI, and similar tools) working in this repository.

## Repository identity

`zhmiao/SkillOpt-gc` — a personal working fork of the public
`microsoft/SkillOpt` project. Public surfaces (the `README.md`,
`docs/` mkdocs site, `configs/`, `pyproject.toml` metadata) stay
clean of personal-fork-only assumptions so changes can be cherry-
picked upstream.

## Read these first

Before any non-trivial edit, read these in order:

1. **`dev_docs/rules.md`** — project-specific conventions that
   apply on top of any user-level / agent-level rules you already
   have. Highest precedence for *project* decisions.
2. **`dev_docs/architecture_overview.md`** — the ground-truth map
   of the codebase: directory layout, the 6-stage per-step pipeline,
   epoch-level slow-update + meta-skill, module responsibilities,
   backend matrix, output directory schema.
3. **`dev_docs/plan.md`** — the current active task (if any).
4. **`dev_docs/lessons.md`** — past corrections; avoid repeating
   mistakes someone else already paid for.
5. **`dev_docs/ideas.md`** — open backlog with stable IDs. If your
   work touches an item here, reference its ID.

## How to work in this repo

| Concern | Where to look |
|---|---|
| Branching / commits / style | `dev_docs/rules.md § Branching and commits`, `§ Style` |
| Pipeline modifications | `dev_docs/architecture_overview.md § The per-step pipeline`, `dev_docs/rules.md § Pipeline I/O` |
| Config changes | `dev_docs/rules.md § Configuration system` |
| New backend | `dev_docs/rules.md § Backends`; reference: `skillopt/model/minimax_backend.py` |
| New benchmark | `dev_docs/rules.md § Environments`; reference: `skillopt/envs/_template/` + `skillopt/envs/searchqa/` |
| Verification before claiming done | `dev_docs/rules.md § Verification gate (project-specific)` |

## Branch protection

`main` is protected. The user's PreToolUse hook blocks direct
commits to `main`/`master`. Always work on a feature branch:
`feat/...`, `fix/...`, `docs/...`, `refactor/...`, `chore/...`,
`test/...`.

## Public vs internal surfaces

| Public (ships to end users / upstream) | Internal (this fork only) |
|---|---|
| `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` | `dev_docs/`, `AGENTS.md` |
| `docs/` (mkdocs → `microsoft.github.io/SkillOpt`) | Files matching the internal-docs block in `.gitignore` |
| `pyproject.toml`, `configs/`, `skillopt/`, `scripts/`, `ckpt/` | Personal notes, scratch artifacts |

If a change would also be appropriate upstream, keep public surfaces
clean of personal-fork-only details so the diff can be cherry-picked.

## After landing changes

Per `dev_docs/rules.md`:
- Update `dev_docs/changelog.md` with the session entry.
- Append to `dev_docs/lessons.md` if you were corrected or learned
  something non-obvious.
- Append to `dev_docs/bugs.md` if you fixed (or even just found) a
  bug.
- Append to `dev_docs/decisions.md` for any non-obvious architectural
  / design choice.
- Update `dev_docs/architecture_overview.md` if you changed the
  codebase shape.
- Update `dev_docs/ideas.md` (strike or add) for backlog drift.

## Quick reference

- Train: `python scripts/train.py --config configs/<bench>/default.yaml ...`
- Eval only: `python scripts/eval_only.py --config configs/<bench>/default.yaml --skill <path> ...`
- WebUI: `python -m skillopt_webui.app` (after `pip install -e ".[webui]"`)
- Lint: `ruff check . && ruff format --check .`
- Docs site preview: `mkdocs serve` (after `pip install -e ".[docs]"`)
