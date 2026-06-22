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

## 2026-06-01 — Copilot-only SkillOpt + first trained skill (Phases 0.5–4)

**Branch.** `chore/dev-docs-scaffold` (continued).
**Commits.** `534a18b` (dataset) · `c0f180f` (stop_slop env + COPILOT-9) ·
`861fbf7` (COPILOT-2 optimizer + Azure→legacy) · `bcddff7` (pipeline
fixes) · `1c67e7b` (Phase 4 results). Skill adoption committed in the
`~/dotfiles` repo as `7015e96`.

**What landed.**
- **Phase 0.5 — dataset.** Built `data/stop_slop_split/` (252 items:
  77 high + 145 medium positives + 30 negatives) by mining
  `~/repos/HumanEmbedding` via 4 parallel extraction streams
  (hand-labeled before/after, auto-diff + LLM-judge, worktree-mined
  negatives, 57-pattern canonical catalog). Merge script
  `scripts/merge_stop_slop_dataset.py`.
- **COPILOT-3 + COPILOT-9 — stop_slop env.** New
  `skillopt/envs/stop_slop/` package (grader / rollout / reflect /
  dataloader / adapter / initial skill) + `configs/stop_slop/`. Skill
  envs route outputs to `outputs/skills/<env>/<run>/`.
- **COPILOT-2 + Phase 3 — Copilot-only.** Copilot CLI now runs as
  BOTH optimizer and target. `chat_optimizer_via_copilot` +
  message-list serializer in `codex_harness.py`. Defaults flipped:
  `optimizer_backend` / `target_backend` / `model.backend` all
  default to `copilot_cli_exec`; default model
  `claude-opus-4.7-1m-internal`; `reasoning_effort` default `none`.
  Azure / OpenAI / Anthropic / Qwen / MiniMax demoted to opt-in
  legacy backends. `configure_azure_openai` is now opt-in. README
  rewritten Copilot-first.
- **Pipeline fixes (`bcddff7`).** Four bugs surfaced by 6 dry runs:
  (1) `train.py` missing `--copilot_cli_exec_*` flags; (2) vestigial
  import in the adapter; (3) ~13% of rollouts stuck in tool
  exploration → inline-prompt path with `available_tools=""` +
  `raw_prompt=True`; (4) analyst returned 0 edits because stop_slop
  didn't write the `conversation.json` the reflect formatter reads.
- **Phase 4 — first full training run.** 4 epochs × 38 steps,
  151-item train pool, 50-item val gate, both sides
  `claude-opus-4.7-1m-internal`, 5h57m, 2491 Copilot CLI calls.
  Held-out test hard **0.2549 → 0.4706 (+21.57 pts)**, 24/51 vs
  13/51. Best skill at step 13 of epoch 2; 4 accepts / 36 rejects;
  plateau in epochs 3–4. 14 test items flipped fail→pass.
- **Skill adoption.** Trained `best_skill.md` (235 lines) copied into
  `~/.copilot/skills/stop-slop/SKILL.md` (dotfiles `7015e96`). The
  pre-adoption original is preserved at
  `skillopt/envs/stop_slop/skills/initial.md`.

**Decisions.** `dev_docs/decisions.md`:
- "Copilot-only direction; Azure OpenAI demoted to legacy"
- "`copilot_cli_exec` ships CLI-only; no SDK path"
- "`stop_slop` dataset source: `HumanEmbedding` repo"
- "Copilot integration first-slice parameters"

**Lessons.** None requiring a `lessons.md` entry; bugs were surfaced
by the dry-run discipline working as intended.

**Bugs.** Four pipeline bugs found + fixed (see `bcddff7` body).

**Ideas added.** `COPILOT-10` (`--effort` harness retry for
non-reasoning models), `CLEAN-3` (stale `docs/guide/new-backend.md`).

**Open / deferred.**
- Phase 3.5 — delete the now-legacy backend modules
  (`azure_openai.py`, `claude_backend.py`, `qwen_backend.py`,
  `minimax_backend.py`, `codex_backend.py`). Unblocked by the passing
  full run; awaiting user go.
- The 0.66 val plateau (epochs 3–4) — candidate for a second tuned
  run (larger val, soft gate, autonomous LR, longer schedule).
- `COPILOT-10`, `CLEAN-3`, token tracking for Copilot calls.
- Next Tier-A skill: `ascii_align` (`COPILOT-4`).

---

## 2026-05-31 — COPILOT-1: Copilot CLI target backend (Phase 1)

**Branch.** `chore/dev-docs-scaffold`
**Commits.** `e6451b5 feat(model): add copilot_cli_exec target backend (COPILOT-1)`
plus the earlier-this-session helpers:
`270005f docs(plan): sign off Phase 0.5, expand Phase 1 into 14 sub-tasks`,
`ab7b459 docs: mark Phase 0.5 (stop_slop dataset) complete in plan`,
`534a18b feat(data): build stop_slop split + merge script`,
`701616a/2225241/2050f07/5d28aad` (the four agent extraction streams).

**What landed.**
- `copilot_cli_exec` is now a first-class target-side backend.
  Available as `--target_backend copilot_cli_exec` (or aliases
  `copilot`, `copilot_cli`, `github_copilot`) on both
  `scripts/train.py` and `scripts/eval_only.py`.
- ~10 files changed, 6 new YAML knobs, 6 new CLI flags, new harness
  function `run_copilot_cli_exec` in `skillopt/model/codex_harness.py`
  modeled on `run_claude_code_exec`.
- Smoke test `scripts/smoke_copilot_cli_exec.py` confirms a real
  `copilot -p` round-trip works end-to-end. PASS.
- README "Configure API Credentials" section now documents the new
  backend (using `claude-sonnet-4.5` as the public example —
  internal-only default model stays in code only).
- Architecture overview backend matrix updated.

**Decisions.** `dev_docs/decisions.md`:
- "`copilot_cli_exec` ships CLI-only; no SDK path" — Copilot CLI
  v1.0.57 does not ship a Python SDK; deferred until / if it does.

**Lessons.** None new this round.

**Bugs.** None.

**Ideas added.**
- `CLEAN-3` — `docs/guide/new-backend.md` is a stale generic
  template referencing file names that don't exist. Surfaced while
  adding `COPILOT-1`; not patched here, needs a rewrite (~2 hours).

**Reformatting note.** `~/.copilot/hooks/post-tool-use.sh` auto-runs
`ruff format` + `ruff check --fix` after every Python edit. The
COPILOT-1 commit therefore shows ~470 deletions in
`skillopt/engine/trainer.py` and ~90 in `scripts/eval_only.py` that
are pure style normalization (line-length 120, blank-line PEP 8,
import sort, removal of one unused `reset_token_tracker` import).
Semantic additions are surgical and listed in the commit body.

**Open / deferred.**
- Phase 2 (`COPILOT-3` — `stop_slop` env adapter) — waiting on user
  sign-off per agreed Phase 1 pause.
- Phase 2.5 (first training run) — explicitly pauses again before
  any training actually starts.
- `COPILOT-2` (optimizer-side copilot_cli_exec) — deferred per user.
- `COPILOT-9` (per-skill `outputs/skills/<skill>/<run>/` layout) —
  lands alongside `COPILOT-3` rather than `COPILOT-1` (no skill
  envs yet to use the new layout).
- `CLEAN-3` — stale `docs/guide/new-backend.md`.

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
