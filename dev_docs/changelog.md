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

## 2026-05-31 — Copilot integration design proposal

**Branch.** `chore/dev-docs-scaffold` (continued from earlier
session today).
**Commits.** _(commit SHA recorded after the design lands.)_

**What landed.**
- New `dev_docs/design/copilot_integration_plan.md`: full review of
  the two coupled asks (add Copilot CLI as a SkillOpt backend +
  expand SkillOpt to optimize complex copilot skills). Covers the
  backend integration surface (file-by-file map of changes,
  copilot CLI quirks, gotchas from existing exec backends, optimizer
  vs target side, effort estimate) and a per-skill compatibility
  matrix for every skill under `~/.copilot/skills/` (21 skills
  classified A/B/C/D against the four SkillOpt requirements).
- `dev_docs/ideas.md`: seeded `COPILOT-1..9` for the implementable
  slices.
- `dev_docs/plan.md`: filled in the **Active** section with the
  copilot-integration phases.
- `dev_docs/changelog.md`: SHA reference for the prior scaffold
  commit corrected from the pre-amend value.

No source code changes — this is read-only review + planning.

**Decisions.** None landed this round. The plan defers all
implementation-shape decisions to the user via the Open Questions
block (`design/copilot_integration_plan.md § C.3`).

**Lessons.** None.

**Bugs.** None.

**Ideas added.** `COPILOT-1` (target backend), `COPILOT-2`
(optimizer backend, deferred), `COPILOT-3` (stop_slop env),
`COPILOT-4` (ascii_align env), `COPILOT-5` (explain env, Tier B),
`COPILOT-6` (test env, Tier B), `COPILOT-7` (code-review env,
Tier B), `COPILOT-8` (Tier-C heavyweight bundle), `COPILOT-9`
(outputs reorganization for skill experiments).

**Open / deferred.** Waiting on user answers to the six Open
Questions in `design/copilot_integration_plan.md § C.3` before
starting `COPILOT-1`.

---

## 2026-05-31 — dev_docs scaffold + repo sweep

**Branch.** `chore/dev-docs-scaffold`
**Commits.** `0d3d0b1 docs: scaffold dev_docs/ and AGENTS.md for fork-internal narrative`

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
