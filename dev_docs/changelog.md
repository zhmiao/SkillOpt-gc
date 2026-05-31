# Changelog

> One entry per session that landed changes. Most recent first.
> Reference commit SHAs and `dev_docs/ideas.md` IDs where relevant.

## Format

```markdown
## YYYY-MM-DD — <session theme>

**Branch.** `<branch-name>`
**Commits.** `<sha1> <subject>`, `<sha2> <subject>`, ...
**What landed.** Bullet list of concrete deliverables.
**Decisions.** Pointers to new entries in `dev_docs/decisions.md`.
**Lessons.** Pointers to new entries in `dev_docs/lessons.md`.
**Bugs.** Pointers to new entries in `dev_docs/bugs.md`.
**Ideas added.** Cross-refs by ID to `dev_docs/ideas.md`.
**Open / deferred.** Anything not done that the next session should
pick up.
```

---

## 2026-05-31 — dev_docs scaffold + repo sweep

**Branch.** `chore/dev-docs-scaffold`
**Commits.** _(commit SHA will be recorded after the scaffold lands)_

**What landed.**
- Created `dev_docs/` with the standard suite: `README.md`,
  `architecture_overview.md`, `rules.md`, `plan.md`, `decisions.md`,
  `lessons.md`, `bugs.md`, `ideas.md`, `changelog.md`.
- Added `AGENTS.md` at the repo root pointing AI tools (Claude Code,
  Copilot CLI, Cursor, Codex CLI) at the rules + architecture
  overview.
- No source code changes; pipeline, configs, and the published
  mkdocs site (`docs/`) are untouched.

**Decisions.** See `dev_docs/decisions.md`:
- "Internal dev docs live under `dev_docs/`, not `docs/`"
- "`AGENTS.md` at repo root for AI-agent discovery"
- Reconstructed pre-existing decisions from the codebase:
  default slow-update mode, mandatory gate, default gate metric,
  `SLOW_UPDATE` protection, optimizer/target backend split.

**Lessons.** None recorded this session.

**Bugs.** None tracked this session.

**Ideas added.** `OBS-1`, `CLEAN-1`, `CLEAN-2`, `CI-1`, `REF-1`,
`REF-2`, `FEAT-1` — see `dev_docs/ideas.md`.

**Open / deferred.** None. The user said they would assign a task
next; `dev_docs/plan.md` is intentionally empty until then.
