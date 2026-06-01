# SkillOpt — Architecture Overview

This is the ground-truth map of the codebase as of the
`chore/dev-docs-scaffold` branch off `main` (commit `8ebede0`,
2026-05-31). Update this file when the structure changes; do not let
it drift.

## What SkillOpt does (one paragraph)

SkillOpt treats a Markdown **skill document** as the trainable state
of an otherwise-frozen target LLM. A separate optimizer model
analyzes scored rollouts and proposes bounded `append` /
`insert_after` / `replace` / `delete` edits to the skill document. A
candidate edit set is accepted only when it strictly improves a
held-out validation score on a selection split. A textual learning
rate (max edits per step), a cosine / linear / constant / autonomous
LR schedule, an epoch-level slow-update that writes a protected
guidance block, and an optimizer-side "meta-skill" memory make the
loop stable. The shipped artifact is `best_skill.md` — a 300–2,000
token Markdown file that the unchanged target model uses at inference
with zero added model calls.

## Top-level layout

```
SkillOpt-gc/
├── README.md                 # Public user-facing entry point
├── CONTRIBUTING.md           # Public contribution guide
├── SECURITY.md               # Microsoft security policy
├── LICENSE                   # MIT
├── pyproject.toml            # Package metadata + optional deps
├── requirements.txt          # Pinned runtime deps
├── mkdocs.yml                # Public docs site config
├── .env.example              # API credential template
├── .gitignore                # Includes a block of "internal-only" docs/
├── index.html / skillopt.html / skillopt-assets/   # Static project page
│
├── scripts/                  # CLI entry points
│   ├── train.py              # Main training entry
│   ├── eval_only.py          # Evaluate a fixed skill on a split
│   └── run_*.sh              # Bench-specific shell wrappers
│
├── skillopt/                 # The Python package
│   ├── config.py             # YAML loader with _base_ inheritance + flatten
│   ├── types.py              # Dataclasses for pipeline I/O
│   ├── engine/trainer.py     # The 2,071-line training loop
│   ├── gradient/             # Reflect + Aggregate (stages ② + ③)
│   ├── optimizer/            # Select, Update, LR sched, slow-update, meta-skill
│   ├── evaluation/gate.py    # Pure accept/reject decision (stage ⑥)
│   ├── envs/                 # Per-benchmark adapters + abstract base
│   ├── model/                # Backend router + per-vendor modules
│   ├── prompts/              # Shared optimizer-side prompt templates
│   ├── datasets/             # Generic split dataloader
│   └── utils/                # JSON utils + scoring + skill hash
│
├── skillopt_webui/           # Optional Gradio dashboard
│
├── configs/                  # YAML configs (one folder per benchmark)
│   ├── _base_/default.yaml   # Single source of truth for all knobs
│   ├── searchqa/, alfworld/, docvqa/, livemathematicianbench/,
│   │   officeqa/, spreadsheetbench/   # Per-benchmark overrides
│   └── features/soft_gate.yaml       # Opt-in feature config
│
├── data/                     # Tracked split manifests (currently only searchqa_id_split/)
├── ckpt/                     # Paper-aligned GPT-5.5 reference skills
│
├── docs/                     # PUBLIC mkdocs site (microsoft.github.io/SkillOpt)
│   ├── index.md, contributing.md
│   ├── guide/                # Installation, first-experiment, configuration, etc.
│   └── reference/            # config.md, cli.md, api.md
│
└── dev_docs/                 # INTERNAL dev narrative (this folder)
```

## The per-step pipeline (the 6 stages)

```
┌───────────────────────────────────────────────────────────────────────┐
│                    Per training step (called STEP)                    │
│                                                                       │
│  current_skill ──► [Target model]                                     │
│                       │                                               │
│                       ▼                                               │
│  ① ROLLOUT      run B tasks against current_skill → results           │
│                   results = [{id, hard∈{0,1}, soft∈[0,1], traj}, …]   │
│                       │                                               │
│                       ▼                                               │
│  ② REFLECT       split into minibatches of size M (default 8)         │
│                   per-minibatch error analyst → failure RawPatch      │
│                   per-minibatch success analyst → success RawPatch    │
│                       │                                               │
│                       ▼                                               │
│  ③ AGGREGATE     hierarchical merge: failure patches first, then       │
│                   success patches; merge_batch_size at a time          │
│                       │                                               │
│                       ▼                                               │
│  ④ SELECT        rank merged edits; clip to scheduler.step() edits     │
│                   (the "learning rate" / edit budget)                  │
│                       │                                               │
│                       ▼                                               │
│  ⑤ UPDATE        apply ranked edits to current_skill → candidate_skill │
│                   (slow-update block is protected; edits inside are    │
│                    silently skipped)                                  │
│                       │                                               │
│                       ▼                                               │
│  ⑥ GATE          evaluate candidate on the selection split             │
│                   metric ∈ {hard, soft, mixed}                         │
│                   ▲                                                    │
│                   │ strictly > current_score?                          │
│                   │                                                    │
│        ┌──────────┴──────────┐                                         │
│        │ accept              │ reject                                  │
│        ▼                     ▼                                         │
│  current_skill =       current_skill unchanged                         │
│   candidate_skill      (rejected edits → step buffer)                  │
│  if > best_score:                                                      │
│   best_skill =                                                         │
│   candidate_skill                                                      │
└───────────────────────────────────────────────────────────────────────┘
```

## Epoch-level extras (between epochs, not between steps)

```
End of epoch K:

  ┌─── SLOW UPDATE (optional, on by default) ──────────────────────────┐
  │  • Re-roll a sample of prev_epoch_skill and curr_epoch_skill on    │
  │    the SAME items.                                                 │
  │  • Build longitudinal pairs (improved / regressed / persistent     │
  │    failure / stable success).                                      │
  │  • Optimizer reads the pairs and writes guidance into the          │
  │    protected SLOW_UPDATE_START..SLOW_UPDATE_END block of the skill.│
  │  • Acceptance modes:                                               │
  │     - force-accept (current main default; `slow_update_gate_with_  │
  │       selection: false`).                                          │
  │     - gated (paper protocol; `slow_update_gate_with_selection:     │
  │       true`). Slow-update candidate is gate-validated like a       │
  │       step-level edit.                                             │
  └────────────────────────────────────────────────────────────────────┘

  ┌─── META SKILL (optional, on by default) ───────────────────────────┐
  │  • Optimizer-side memory distilled from the same longitudinal      │
  │    pairs. Does NOT modify the skill document.                      │
  │  • Stored under outputs/<run>/meta_skill/epoch_XX/.                │
  │  • Loaded at the start of epoch K+1 and injected into the          │
  │    optimizer's reflect / merge / rank prompts for that epoch.      │
  └────────────────────────────────────────────────────────────────────┘
```

## Module responsibilities (where to make changes)

| Concern | Module | Key entry points |
|---|---|---|
| CLI parsing + env registry | `scripts/train.py`, `scripts/eval_only.py` | `_register_builtins`, `get_adapter`, `main` |
| Config YAML + `_base_` inheritance | `skillopt/config.py` | `load_config`, `flatten_config`, `apply_overrides` |
| Pipeline I/O dataclasses | `skillopt/types.py` | `Edit`, `Patch`, `RawPatch`, `RolloutResult`, `SlowUpdateResult` |
| Main training loop | `skillopt/engine/trainer.py` | `run_training` (2,071 LOC; refactor candidate) |
| Stage ① ROLLOUT | `skillopt/envs/<bench>/rollout.py` | Per-bench: spawns target backend calls |
| Stage ② REFLECT | `skillopt/gradient/reflect.py` | `run_minibatch_reflect`, `run_error_analyst_minibatch`, `run_success_analyst_minibatch` |
| Stage ③ AGGREGATE | `skillopt/gradient/aggregate.py` | `merge_patches` (hierarchical; failure-first) |
| Stage ④ SELECT | `skillopt/optimizer/clip.py`, `lr_autonomous.py`, `scheduler.py` | `rank_and_select`, `decide_autonomous_learning_rate`, `build_scheduler` |
| Stage ⑤ UPDATE | `skillopt/optimizer/skill.py` | `apply_patch_with_report`; respects `SLOW_UPDATE_START`/`END` markers |
| Stage ⑥ GATE | `skillopt/evaluation/gate.py` | `evaluate_gate`, `select_gate_score` (pure decision functions) |
| Slow update | `skillopt/optimizer/slow_update.py` | `run_slow_update`, `build_comparison_pairs` |
| Meta skill | `skillopt/optimizer/meta_skill.py` | `run_meta_skill`, `format_meta_skill_context` |
| Skill rewrite (`rewrite_from_suggestions` mode) | `skillopt/optimizer/rewrite.py` | `rewrite_skill_from_suggestions` |
| Env adapter contract | `skillopt/envs/base.py` | `EnvAdapter` (abstract: `build_*_env`, `rollout`, `reflect`, `get_task_types`) |
| Backend routing | `skillopt/model/__init__.py`, `backend_config.py`, `common.py` | `chat_optimizer`, `chat_target`, `set_*_backend`, `set_*_deployment`, `configure_*` |
| Per-vendor backends | `skillopt/model/{azure_openai,claude_backend,codex_backend,qwen_backend,minimax_backend}.py` | One `chat_target` / `chat_optimizer` pair each |
| Data splits | `skillopt/datasets/base.py` | `BaseDataLoader`, `SplitDataLoader` (modes: `split_dir`, `ratio`) |
| Scoring + hashing | `skillopt/utils/scoring.py` | `compute_score`, `skill_hash` |
| Prompts | `skillopt/prompts/*.md` + `skillopt/envs/<bench>/prompts/*.md` | Two-level priority: env-specific override → generic default |

## Environment registry

`scripts/train.py` lazy-imports adapters so an environment whose
optional deps are not installed simply does not register. As of
`main`, the registered names are:

```
alfworld, searchqa, livemathematicianbench, babyvision,
spreadsheetbench, mmrb, docvqa, mathverse, officeqa,
sealqa, swebench
```

Of those, only six have corresponding `configs/<name>/` directories.
The others have adapters in the registry but no shipped config —
expected, since they were used internally for the paper and the
configs are being cleaned + released gradually (per the README
"first artifact batch" note).

## Backend matrix

| Backend key | Vendor / runtime | Role(s) | Module | Status |
|---|---|---|---|---|
| `openai_chat` | Azure OpenAI or OpenAI-compatible REST | optimizer & target | `azure_openai.py` | legacy (opt-in via `--backend azure_openai`) |
| `claude_chat` | Anthropic Messages API | optimizer & target | `claude_backend.py` | legacy |
| `qwen_chat` | local vLLM with OpenAI-compatible API | target | `qwen_backend.py` | legacy |
| `minimax_chat` | MiniMax REST API | target | `minimax_backend.py` | legacy |
| `codex_exec` | `codex` CLI (agentic harness) | target only | `codex_backend.py` (+ `codex_harness.py`) | legacy |
| `claude_code_exec` | `claude` CLI (agentic harness) | target only | configured via `backend_config.py` | legacy |
| `copilot_cli_exec` | `copilot` CLI (GitHub Copilot CLI agentic harness) | optimizer & target | `codex_harness.py:run_copilot_cli_exec` + `chat_optimizer_via_copilot` (COPILOT-1 + COPILOT-2) | **default** since 2026-06-01 |

Optimizer and target backends are independent — the common
production split is `optimizer_backend=openai_chat` +
`target_backend=codex_exec` or `claude_code_exec`.

## Data flow at one glance

```
configs/<bench>/default.yaml  (inherits configs/_base_/default.yaml)
        │
        ▼
load_config() → flatten_config() → flat dict
        │
        ▼
get_adapter(cfg)  →  EnvAdapter subclass instance
        │                       │
        ▼                       ▼
configure_azure_openai(...)   adapter.setup(cfg)
configure_codex_exec(...)         │
configure_claude_code_exec(...)   ▼
configure_qwen_chat(...)      dataloader (split_dir or ratio)
configure_minimax_chat(...)       │
        │                         │
        ▼                         ▼
run_training(cfg, adapter)  ──────┘
        │
        ├─► per-step: rollout → reflect → aggregate → select → update → gate
        ├─► per-epoch: slow_update → meta_skill (next epoch)
        └─► outputs/<run>/{config.json, history.json, runtime_state.json,
                           best_skill.md, skills/, steps/, slow_update/,
                           meta_skill/}
```

## Output directory schema

```
outputs/<run_name>/
├── config.json              # Flattened + redacted config (passwords masked)
├── history.json             # Per-step record: scores, edit counts, timings, tokens
├── runtime_state.json       # Resume checkpoint (last_completed_step + best/current ptrs)
├── best_skill.md            # The validated best skill — the shipping artifact
├── lr_history.jsonl         # Per-step autonomous LR decisions (when autonomous)
├── skills/skill_vXXXX.md    # One snapshot per step (XXXX = global_step, zero-padded)
├── steps/step_XXXX/         # Per-step artifacts (rollouts, merged patches, ranked, applied)
├── selection_eval_baseline/ # Selection-split eval of initial skill
├── slow_update/epoch_XX/    # Slow-update inputs (pairs) + optimizer output
├── meta_skill/epoch_XX/     # Meta-skill optimizer output
└── _generated_splits/<bench>_<ratio>_seed<N>/   # When split_mode=ratio
```

Re-running the same command auto-resumes from `runtime_state.json`.

## Cross-cutting design decisions worth knowing

| Decision | Why | Code reference |
|---|---|---|
| YAML configs are flattened to a single flat dict before reaching the trainer | Keep `trainer.py` agnostic to YAML structure; structured configs are a UX layer | `skillopt/config.py:_FLATTEN_MAP` |
| `EnvAdapter.reflect()` lives on the adapter, not in the gradient package | Each environment may have its own reference text, task types, and prompt overrides; the abstract base ships a sane default | `skillopt/envs/base.py:get_error_minibatch_prompt` |
| Prompts use a two-level priority (env-specific override → generic) | Per-env customization without forking the generic templates | `skillopt/envs/base.py:_load_env_prompt` |
| Gate decision is a pure function | Easy to test and audit; trainer owns all side effects | `skillopt/evaluation/gate.py:evaluate_gate` |
| `SLOW_UPDATE_START` / `SLOW_UPDATE_END` block is protected | Step-level edits must not stomp on cross-epoch guidance | `skillopt/optimizer/skill.py:_is_in_slow_update_region` |
| `use_gate: false` is forbidden in this branch | Gate validation is mandatory by policy | `skillopt/config.py:flatten_config` and `trainer.py` startup |
| Backend split (optimizer ≠ target) | Decoupling lets a strong optimizer run a smaller / cheaper target | `skillopt/model/__init__.py` `chat_optimizer` vs `chat_target` |
| Splits standardized as `train/`, `val/`, `test/` JSON arrays | One adapter API across QA, embodied, code-gen, math, etc. | `skillopt/datasets/base.py:SPLIT_NAMES` |
| Deterministic per-epoch seed shuffling | Reproducibility across resume + replay | `skillopt/datasets/base.py:make_base_seeds`, `shuffle_epoch_seeds` |

## Public vs internal surfaces

Public-facing (ships to end users):
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`
- `docs/` (mkdocs site → `microsoft.github.io/SkillOpt`)
- `ckpt/README.md` and the paper-aligned skill artifacts
- `configs/_base_/default.yaml` + per-benchmark configs
- `pyproject.toml` console scripts (`skillopt-train`, `skillopt-eval`)

Internal / personal-fork-only:
- `dev_docs/` (this folder)
- `AGENTS.md` (AI-agent entry point — also useful to other devs)
- Anything matching the `# Internal docs (not for open-source release)`
  block in `.gitignore`

Treat the boundary as a contract: anything that goes into the public
surfaces should not assume internal docs exist, and vice versa.
