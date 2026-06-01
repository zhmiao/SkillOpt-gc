# Current Plan

> Update this at the start of any non-trivial task. Strike through
> items as they complete; archive completed plans by moving the
> section to `dev_docs/changelog.md` and resetting this file.

## Active

### Goal
Land Copilot CLI as a SkillOpt backend and start optimizing the
user's own `~/.copilot/skills/*` with SkillOpt. The full design
lives at `dev_docs/design/copilot_integration_plan.md`; the
implementable slices are `COPILOT-1..9` in `dev_docs/ideas.md`.

### Acceptance
- [ ] User has confirmed (a) which Copilot model is the default for
      the new backend, (b) Tier-A skill order, (c) whether to ship
      optimizer-side copilot support in slice 1 or defer.
- [ ] `COPILOT-1` (`copilot_cli_exec` target backend) lands with a
      smoke that round-trips `copilot -p "say hello"` through the
      harness.
- [ ] `COPILOT-3` (`stop_slop` env) trains end-to-end on the new
      backend and produces a `best_skill.md` that beats the initial
      skill on `valid_unseen`.

### Phase 0 — Design review (active now)
- [x] Sweep `~/.copilot/skills/` and classify each skill A/B/C/D
      against SkillOpt requirements.
- [x] Write `dev_docs/design/copilot_integration_plan.md`.
- [x] Seed `dev_docs/ideas.md` with `COPILOT-1..9`.
- [x] User answered the six Open Questions (see `dev_docs/decisions.md`
      entry "2026-05-31 — Copilot integration first-slice parameters").
- [x] User chose source corpus for `stop_slop` env: `/home/miao/repos/HumanEmbedding`
      with dataset_option=max, both pattern sources, 60/20/20 split, negatives included.

### Phase 0.5 — `stop_slop` dataset construction (DONE 2026-05-31)
Mine `/home/miao/repos/HumanEmbedding` for a labeled
`(prose_in, banned_patterns, gold_rewrite?, source)` dataset.
Four parallel extraction streams dispatched as background agents
(see `dev_docs/design/dataset_construction_plan.md`).

- [x] Stream 1 (hand-labeled before/after): 83 high-quality positives,
      commit `5d28aad`.
- [x] Stream 2 (auto-extracted diffs + LLM-judge filter): 147
      medium-quality positives, commit `701616a`.
- [x] Stream 3 (negative examples from worktrees): 30 negative items,
      commit `2225241`. Worktree-uniqueness check found 31/63 files
      uniquely divergent from `main`; the rest fell back to
      `inquisitor_review.md` notes.
- [x] Stream 4 (banned-pattern catalog union): 47 canonical patterns
      (16 from `ai_writing_tells_only` + 23 from `stop_slop_only` +
      8 from both), 43 regex + 4 llm_judge matchers, commit `2050f07`.
- [x] Merge + dedupe + assign 60/20/20 splits, write to
      `data/stop_slop_split/{train,val,test}/items.json` and
      `data/stop_slop_split/banned_patterns.json`. Final: 252 unique
      items (train=151, val=50, test=51); 18/6/6 negatives per split;
      catalog extended from 47 → 57 with 10 new canonical patterns
      surfaced by streams 1/2/3 (anaphora, metaphor_overuse,
      q_and_a_pair, staccato_fragmentation, etc.). Commit `534a18b`.
- [x] User signed off after seeing 14 sample items spanning the top
      patterns (chat 2026-05-31).

### Phase 1 — Backend (`COPILOT-1`, DONE 2026-05-31)
Scope: **target-side only** (per user `copilot_scope=target_only_first`).
Optimizer-side support deferred to `COPILOT-2`.

Per `dev_docs/design/copilot_integration_plan.md § A.1`, ~430 LOC
across ~10 files mirroring the existing `claude_code_exec` pattern.

- [x] 1.1 — Per-backend constants + `configure_*` / `get_*` in
      `skillopt/model/backend_config.py`. Added `COPILOT_CLI_EXEC_*`
      env-backed vars, `configure_copilot_cli_exec()`,
      `get_copilot_cli_exec_config()`.
- [x] 1.2 — Validation set + alias + default model:
      `backend_config.py:set_target_backend` allow-list,
      `is_target_exec_backend` set, `common.py:_BACKEND_DEFAULT_MODELS`
      (default = `claude-opus-4.7-1m-internal` per user — fork-only),
      `common.py:_BACKEND_ALIASES` (adds `copilot`, `copilot_cli`,
      `github_copilot` → `copilot_cli_exec`).
- [x] 1.3 — Harness implementation in `skillopt/model/codex_harness.py`:
      added `_build_copilot_trace_summary`, `_persist_copilot_artifacts`,
      `_run_copilot_cli_exec`, `run_copilot_cli_exec`. CLI-only path
      (no SDK — see `dev_docs/decisions.md`).
- [x] 1.4 — Dispatcher: added `if backend == "copilot_cli_exec":`
      branch in `codex_harness.py:run_target_exec`.
- [x] 1.5 — Public re-exports in `skillopt/model/__init__.py`:
      `configure_copilot_cli_exec`, `get_copilot_cli_exec_config`.
- [x] 1.6 — Config flatten map in `skillopt/config.py:_FLATTEN_MAP`:
      6 new `model.copilot_cli_exec_*` keys.
- [x] 1.7 — Defaults YAML: added `copilot_cli_exec_*` block to
      `configs/_base_/default.yaml`.
- [x] 1.8 — Trainer wiring: `skillopt/engine/trainer.py` import,
      backend resolution (`copilot`/`copilot_cli`/`copilot_cli_exec`/
      `github_copilot` aliases), and `configure_copilot_cli_exec(...)`
      call.
- [x] 1.9 — Eval-only wiring: `scripts/eval_only.py` import, CLI
      `--backend` choices, 6 new CLI flags, cfg-key map, backend
      dispatch, configure call.
- [x] 1.10 — Env template: `.env.example` Copilot CLI block.
- [x] 1.11 — Smoke test: `scripts/smoke_copilot_cli_exec.py` ran the
      real `copilot -p "say hello"` through the harness end-to-end.
      Returned "hello" in ~5s, exit 0, artifacts persisted.
      **STATUS: PASS**.
- [x] 1.12 — Public docs: README "Configure API Credentials" section
      gets a GitHub Copilot CLI subsection mirroring the MiniMax
      pattern. Uses `claude-sonnet-4.5` as the public example model
      (fork-only default `claude-opus-4.7-1m-internal` not surfaced
      publicly). `docs/guide/new-backend.md` is stale and NOT touched
      here — filed as `CLEAN-3` for a separate rewrite.
- [x] 1.13 — Internal docs: `dev_docs/architecture_overview.md`
      backend matrix updated with copilot row.
      `dev_docs/decisions.md` got the CLI-only-no-SDK choice entry.
- [x] 1.14 — Commit. Done in chore/dev-docs-scaffold branch.

User sign-off needed before Phase 2.

### Phase 2 — First env (`COPILOT-3` stop_slop)
_Pending Phase 1 sign-off._

Per user direction, will pause before any actual training. Plan to
flesh out at start of Phase 2.

### Phase 3+ — Second env onward
_Per user direction at end of Phase 2._

## Backlog (high level)

See `dev_docs/ideas.md` for the open backlog with stable IDs. The
plan file references those IDs once they become active work.

## How to use this file

1. When the user assigns a task, write a short "Goal" + "Acceptance"
   block at the top of the **Active** section.
2. Break into phases. Each phase is a checkbox list with files
   touched, commands to run, and a verification step.
3. As phases complete, check them off. Keep notes in the same phase
   block (timing surprises, scope changes, things deferred).
4. When the task is fully done, move the whole block into
   `dev_docs/changelog.md` under today's date and clear it from here.

## Template

```markdown
## Active

### Goal
<one-sentence goal>

### Acceptance
- [ ] <observable criterion 1>
- [ ] <observable criterion 2>

### Phase 1 — <name>
- [ ] <step>
- [ ] Verification: <command + expected output>

### Phase 2 — <name>
- [ ] ...
```
