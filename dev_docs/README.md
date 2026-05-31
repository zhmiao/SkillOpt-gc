# dev_docs/ — internal development docs for SkillOpt-gc

This folder holds the **internal development narrative** for
`zhmiao/SkillOpt-gc`, the personal working fork of the public
`microsoft/SkillOpt` project. The public `docs/` directory is the
mkdocs site that ships to `microsoft.github.io/SkillOpt`; that site is
user-facing and stays clean. This folder is for AI-agent
collaboration: planning, decisions, lessons, bugs, ideas, and the
ground-truth architecture reference.

## What lives where

| File | When to read it | When to write to it |
|---|---|---|
| `architecture_overview.md` | Onboarding a new task. The repo's source-of-truth map: directory layout, pipeline, the 6-stage loop, epoch stages, control planes. | Only when the codebase structure actually changes (new module, refactor, deleted subsystem). |
| `rules.md` | At the start of every coding session. Project-specific conventions that apply on top of the global rules in `~/.copilot/instructions/`. | When a new convention is established and the rule has been seen twice. |
| `plan.md` | At the start of every coding session, after `rules.md`. The current goal, its phases, and per-phase checklists. | At the start of any non-trivial task; update at each milestone. |
| `decisions.md` | When you need to know *why* a piece of code is the way it is. | When making any non-obvious architectural / design / config choice. |
| `lessons.md` | At the start of every coding session, before making assumptions. | After every user correction or after discovering a non-obvious failure mode. |
| `bugs.md` | When triaging anything that looks broken. Cross-references `lessons.md` when a bug taught us something general. | When a bug is found, even if it's not fixed yet. Track root cause + fix + similar patterns. |
| `ideas.md` | When picking up open work. Backlog of "should do" items with stable IDs. | When you notice something worth doing later but it's out of current scope. |
| `changelog.md` | When summarizing past sessions or before compaction. | At the end of every session that landed changes; one entry per session. |

## Relationship to the public `docs/`

`docs/` (mkdocs site) holds:
- User-facing tutorials (`docs/guide/`)
- Public API / CLI / config reference (`docs/reference/`)
- Project landing page (`docs/index.md`)
- Public CONTRIBUTING (`docs/contributing.md`)

`dev_docs/` (this folder) holds:
- Engineering narrative for the working fork
- AI-agent context (rules, lessons, plans)
- Internal design decisions and known issues

**Hard rule**: when the same fact would be useful to an end user, it
belongs in `docs/`. When it's only useful to the people maintaining the
fork, it stays here.

## Sibling files at the repo root

- `AGENTS.md` — entry point that AI tools (Claude Code, Copilot CLI,
  Cursor, etc.) auto-discover. Points at `dev_docs/rules.md` and
  `dev_docs/architecture_overview.md`.
- `README.md` — public-facing; ships with the upstream project.
- `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` — upstream project files;
  don't edit unless deliberately diverging from `microsoft/SkillOpt`.
