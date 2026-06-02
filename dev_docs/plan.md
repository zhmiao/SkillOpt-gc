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

### Phase 2 — First env (`COPILOT-3` stop_slop, DONE 2026-06-01)
Built `skillopt/envs/stop_slop/` end-to-end. Smoke test against real
Copilot CLI: 5/5 items succeeded, with real grading signal
(3 hard=1, 2 hard=0; one caught `em_dash_overuse`, one caught
introduced `rule_of_three`).

- [x] 2.1 Grader semantics (`grader.py`): regex pass + batched LLM-judge
      pass + severity-weighted soft score (high=3, medium=2, low=1) +
      strict hard for positives (`input_tags absent AND no new patterns`)
      and `prose_in != rewrite` for negatives.
- [x] 2.2 `JudgeCache` (sha256-keyed in-process LRU, default 4096
      entries) — collapses repeat judge calls during selection-set
      re-evals.
- [x] 2.3 `StopSlopDataLoader` (subclasses `SplitDataLoader`, reads
      `items.json` per split).
- [x] 2.4 `rollout.py`: prompt builder + `extract_rewrite` (strict —
      requires `<rewrite>` tag, no fallback) + per-item `process_one` +
      threaded `run_batch` + injectable `judge_fn` for tests.
- [x] 2.5 `reflect.py`: thin wrapper around generic
      `run_minibatch_reflect`.
- [x] 2.6 `StopSlopAdapter` (`adapter.py`): standard `EnvAdapter`
      subclass wiring dataloader + rollout + reflect; resolves
      `catalog_path` from split_dir or env override.
- [x] 2.7 `skills/initial.md`: copy of `~/.copilot/skills/stop-slop/SKILL.md`
      (2629 chars).
- [x] 2.8 `configs/stop_slop/default.yaml`: env-tuned defaults
      (`batch_size=16`, `workers=8`, `sel/test_env_num=0` for full
      splits, `catalog_path` auto-resolves).
- [x] 2.9 Registry wiring: `_ENV_REGISTRY["stop_slop"] = StopSlopAdapter`
      in both `scripts/train.py` and `scripts/eval_only.py`.
- [x] 2.10 `COPILOT-9`: `_SKILL_ENVS = {"stop_slop"}` in both scripts;
      out_root falls back to `outputs/skills/<env>/<run>/` when env is
      in the set (vs flat `outputs/<run>/` for benchmark envs).
- [x] 2.11 Smoke test (`scripts/smoke_stop_slop_env.py`): 5 train
      items via Copilot CLI with stub LLM-judge. STATUS: PASS,
      ~16s/rollout.
- [x] 2.12 Bug found and fixed during smoke: `extract_rewrite` was
      falling back to "treat entire response as rewrite" when no
      `<rewrite>` tag found — caused Copilot CLI error transcripts to
      be graded as perfect rewrites (hard=1 false positives). Now
      strict: no tag → `fail_reason="no_rewrite_tag_in_response"`.
- [x] 2.13 Bug found and worked around: `--effort low` rejected by
      `claude-sonnet-4.5` model. Smoke now uses `effort="none"`
      (skips the flag). Filed as `COPILOT-10` for a proper harness-side
      fix.
- [x] 2.14 Commit. Done in chore/dev-docs-scaffold branch.

User sign-off needed before Phase 2.5 (first training run).

### Phase 3 — Copilot-only mode (DONE 2026-06-01)
COPILOT-2 (optimizer-side `copilot_cli_exec`) + Azure-removal
cleanup. User direction: "the whole purpose of this project is to
make this skillopt fully and solely for copilot."

- [x] 3-A.1 Allow `copilot_cli_exec` in `set_optimizer_backend`
      allow-list. Add `is_optimizer_exec_backend()`.
- [x] 3-A.2 `chat_optimizer_via_copilot` + `chat_optimizer_messages_via_copilot`
      in `codex_harness.py`. Tool-call serializer + parser. Unit tests
      in `scripts/test_copilot_optimizer_helpers.py` pass.
- [x] 3-A.3 `__init__.py` dispatchers route to the copilot path when
      optimizer backend is `copilot_cli_exec`.
- [x] 3-A.4 Default flip: `OPTIMIZER_BACKEND` and `TARGET_BACKEND`
      env defaults now `copilot_cli_exec`. `configs/_base_/default.yaml`
      `model.backend` flipped likewise. `model.optimizer` and
      `model.target` default to `claude-opus-4.7-1m-internal`.
      `reasoning_effort` default flipped from `medium` to `none`
      (Claude models reject anything else).
- [x] 3-A.5 Live smoke `scripts/smoke_copilot_optimizer.py`:
      `chat_optimizer` returns `'Blue'` clean; `chat_optimizer_messages`
      with forced tool choice returns parsed tool call
      `name=report_color args={"color":"yellow"}`. STATUS: PASS.
- [x] 3-B.1 Trainer: `configure_azure_openai` is opt-in (only called
      when an Azure-consuming backend is active or an Azure endpoint
      is set in the cfg).
- [x] 3-B.2 `configs/_base_/default.yaml`: model.backend default
      flipped to `copilot_cli_exec`. Azure knobs left in place but
      no longer the happy path.
- [x] 3-B.3 README "Configure API Credentials" rewritten: Copilot CLI
      is the single documented happy path. Azure / OpenAI / Anthropic
      / Qwen / MiniMax collapsed into a "Legacy backends" disclosure
      block.
- [x] 3-B.4 `dev_docs/architecture_overview.md` backend matrix gets
      a "Status" column; copilot row marked **default since
      2026-06-01**; everything else marked `legacy`.
- [x] 3-B.5 `dev_docs/decisions.md` new entry: "Copilot-only
      direction; Azure OpenAI demoted to legacy" with full
      context/options/rationale/code-refs.

**Bugs surfaced and fixed during the live smoke:**
- The first optimizer-side smoke returned tool-exploration noise
  (`● List directory`, `Find markdown files`) because every prompt
  was being wrapped with `_exec_prompt` — the target-side wrapper
  that tells the model to read `task.md` / `.agents/skills/...`.
  Added `raw_prompt=True` parameter to bypass that wrapper for
  optimizer-side calls.
- Even with `--available-tools=` disabling tool access, the
  `_exec_prompt` wrapper was telling the model files would exist.
  Fixed at the same time as the previous bug.

### Phase 3.5 — Delete legacy backend modules (pending user sign-off)
_Pending Phase 3 sign-off + user-verified dry run._

Per user choice `backend_modules_fate=delete_after_smoke`:
`azure_openai.py`, `claude_backend.py`, `qwen_backend.py`,
`minimax_backend.py`, `codex_backend.py` will be deleted in a
separate commit once the user has run an end-to-end stop_slop
training cycle (or at least a dry run) on Copilot-only mode and
confirmed nothing broke. `codex_harness.py` stays — it contains the
Copilot-only path.

### Phase 4 — First training run (DONE 2026-06-01)
End-to-end training of stop_slop on Copilot-only mode against
`claude-opus-4.7-1m-internal` for both optimizer and target.

**Setup:** `configs/stop_slop/default.yaml` defaults (4 epochs × 38
steps × batch_size=16), full 151-item train pool, full 50-item val
gate, `--copilot_cli_exec_effort none`.

**Wall clock:** 21442s = 5h 57min.
**Total Copilot CLI calls:** 2491 (target rollouts + optimizer +
LLM judge, all routed through copilot_cli_exec).

**Headline result:** held-out test hard score
**0.2549 → 0.4706 (+21.57 absolute points)** — 13/51 baseline vs
24/51 best-skill on the test split. Selection-set gate peaked at
0.6600 (33/50) at step 13 of epoch 2 and stayed there for the
remaining 27 steps (4 accepts total across all 40 steps).

**Per-epoch accept/reject:**

| Epoch | Accepts | Rejects | Best after |
|---|---:|---:|---:|
| 1 | 3 | 7 | 0.5000 |
| 2 | 1 | 9 | 0.6600 (step 13) |
| 3 | 0 | 10 | 0.6600 (plateau) |
| 4 | 0 | 10 | 0.6600 (plateau) |

**Trained skill artifact:** `outputs/skills/stop_slop/claude-opus-4.7-1m-internal_20260601_144448/best_skill.md` — 27514 chars (vs 2629 chars initial). Now contains pattern-specific recipes, fix-priority ordering, and a 14-item pre-ship checklist. The skill went from generic "remove AI patterns" rules to a domain-specific playbook keyed against the 57-pattern canonical catalog.

**What worked:**
- All four COPILOT-1/2/3 + Phase 2 + Phase 3 components ran in
  concert without crashes for 6 hours.
- The analyst produced meaningful patches (4 accept-worthy in 40
  steps).
- The gate correctly rejected 36 candidates that didn't improve.
- Slow-update force-injected guidance that grew the skill from
  ~12KB (peak step-level acceptance) to 27KB (peak with slow-update
  guidance accumulated across epochs).
- LLM-judge cache: 571 hits / 2283 misses — caching across the 2491
  calls saved ~25% of judge calls.

**Open observations for the next run:**
- The plateau in epochs 3-4 suggests either the optimizer hit a
  local maximum given the current dataset / pattern catalog, OR
  the gate-strict-hard semantics rejected real improvements
  because the val set is only 50 items (each item flip = 2-point
  step change).
- Test improvement (+21.57) > val plateau movement after step 13
  (+0%) — the held-out test gained more than the gate-tracked val,
  suggesting the slow-update guidance generalizes better than
  step-level edits.
- 13 hours estimated -> 6 hours actual. Target rollouts on Opus
  averaged ~4s each; the bottleneck is reflect (30-130s per call).

### Phase 5 — What's next (pending user direction)
_Per user direction at end of Phase 4._

Possible next steps surfaced by the run:
- Phase 3.5 — delete legacy backend modules now that Copilot-only
  is proven (per `backend_modules_fate=delete_after_smoke`).
- Adopt the trained skill: copy `best_skill.md` into
  `~/.copilot/skills/stop-slop/SKILL.md` (with version control).
- Tune for a second run (longer training? bigger sel set? `soft`
  gate? autonomous LR?).
- Move to the next Tier-A skill (`ascii_align`).

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
