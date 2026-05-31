# Project Rules — SkillOpt-gc

Project-specific conventions for `zhmiao/SkillOpt-gc`. These rules
apply on top of the global rules under `~/.copilot/instructions/`.
Promote stable rules from here to the global instructions only via
the `/si-promote` flow (with explicit user approval) — never directly.

## Repo identity (do not blur)

- This repo is a **personal working fork** of `microsoft/SkillOpt`,
  not the upstream itself.
- `docs/` is the public mkdocs site that publishes to
  `microsoft.github.io/SkillOpt`. Treat it as user-facing.
- `dev_docs/` is internal narrative. Treat it as engineering-facing.
- When making a change that would also be appropriate for upstream,
  keep the public surfaces (README, `docs/`, `configs/`,
  `pyproject.toml` metadata) clean of personal-fork-only assumptions
  so the diff can be cherry-picked upstream.

## Branching and commits

- `main` is protected by the global PreToolUse hook — do not commit
  directly. Always work on a feature branch with a conventional
  prefix: `feat/...`, `fix/...`, `docs/...`, `refactor/...`,
  `chore/...`, `test/...`.
- Atomic commits. One logical change per commit.
- Conventional commit messages (`type(scope): short summary`). Body
  explains *why* when the *what* is not obvious from the diff.
- Include the Copilot co-author trailer on AI-assisted commits
  (the global rule already enforces this).

## Documentation discipline

- Update `dev_docs/changelog.md` at the end of every session that
  landed changes — one entry per session.
- Update `dev_docs/architecture_overview.md` whenever the codebase
  structure changes (new module, deleted subsystem, moved
  responsibility). This is the source-of-truth map; let it rot and
  every future agent starts from a wrong picture.
- Update `dev_docs/decisions.md` whenever a non-obvious choice is
  made. Cite the alternatives considered and why this one won.
- Public docs (`docs/`, `README.md`) must not reference paths or
  features that don't exist in the shipped package. Verify with
  `glob`/`grep` before merging changes there.

## Configuration system

- YAML configs live under `configs/<bench>/default.yaml` and inherit
  from `configs/_base_/default.yaml` via `_base_:`.
- Every knob in `_base_/default.yaml` must round-trip through
  `flatten_config()` in `skillopt/config.py`. When adding a new knob,
  add its dotted → flat mapping to `_FLATTEN_MAP`.
- Defaults in `_base_/default.yaml` must match the paper protocol
  *unless* the README explicitly calls out the divergence (currently
  only `slow_update_gate_with_selection: false` qualifies).
- New optional feature configs go under `configs/features/` with a
  header comment block that states (a) when to use it, (b) when NOT
  to use it, (c) which paper claims it affects. Pattern:
  `configs/features/soft_gate.yaml`.

## Pipeline I/O

- All dataclasses that flow between pipeline stages live in
  `skillopt/types.py`. Adding a new field requires:
  1. Update the dataclass.
  2. Update its `from_dict` / `to_dict` to round-trip.
  3. Update every producer and consumer.
- The 6-stage per-step pipeline order is fixed:
  rollout → reflect → aggregate → select → update → gate.
  Do not introduce a new stage without surfacing it in
  `dev_docs/decisions.md` first.

## Skill document conventions

- The skill is a single Markdown file. Keep it readable end-to-end.
- The `<!-- SLOW_UPDATE_START -->` / `<!-- SLOW_UPDATE_END -->`
  block is **protected**: step-level edits must never touch its
  interior. The check lives in `skillopt/optimizer/skill.py`. Do not
  loosen it.
- New marker blocks must be opaque to all step-level edits — same
  protection model as `SLOW_UPDATE`. Don't invent ad-hoc markers
  without updating the edit applier and writing a test.

## Backends

- Optimizer-side and target-side backends are independent. Any new
  backend module must:
  1. Live at `skillopt/model/<name>_backend.py`.
  2. Register in `skillopt/model/common.py` (alias + default model).
  3. Wire through `skillopt/model/backend_config.py`
     (`set_*_backend` + capability checks).
  4. Wire through `skillopt/model/__init__.py` dispatcher.
  5. Have a `configure_*` function for runtime config.
  6. Surface its env-vars in `.env.example`.
- Backends MUST NOT print secrets. The trainer redacts via
  `_redact_cfg` before writing `config.json`; new backends must keep
  secret keys out of any persistent log line.

## Environments

- New benchmarks follow `skillopt/envs/_template/` and the
  `EnvAdapter` contract in `skillopt/envs/base.py`. Required:
  `build_train_env`, `build_eval_env`, `rollout`, `reflect`,
  `get_task_types`.
- Datasets land under a `train/`, `val/`, `test/` split directory of
  JSON arrays. New shapes go through `SplitDataLoader.load_split_items`
  and `load_raw_items` overrides — do not invent a new split layout.
- Adapter must be lazy-importable in `scripts/train.py`'s registry so
  optional dependencies do not break unrelated runs.

## Determinism and reproducibility

- Every randomness call must take a seed derived from `cfg["seed"]`
  + epoch + step. Do not introduce ungated `random.random()` or
  `numpy` randomness without surfacing the seed source.
- The training loop is resume-aware via `runtime_state.json`. Any
  new persistent state must be added to `_persist_runtime_state` and
  consumed at startup.
- When changing a default that would alter previously-reproducible
  runs, document the change in `dev_docs/decisions.md` and update
  the public README's "Default settings and paper-reproduction
  knobs" section.

## Testing

- No `tests/` directory exists yet. When you add one, the entry
  point is `pytest` (already in the `dev` extras). Mirror the
  package layout: `tests/test_<module>.py`. Keep tests offline — no
  network, no real model calls. Mock the backends with fixtures.
- For any bug fix, write the regression test first. Track in
  `dev_docs/bugs.md` even if the test is the only evidence.

## Style

- Python ≥ 3.10. Use `from __future__ import annotations` at the
  top of every module. Use PEP-604 unions (`int | None`).
- Ruff is the linter and formatter (`pyproject.toml` `[tool.ruff]`).
  Run before committing: `ruff check . && ruff format .`.
- Type-hint every function signature. Internal helpers may omit
  return types when obvious, but public entry points must annotate.
- Docstrings: PEP-257 / NumPy-style. The trainer and pipeline-stage
  functions already follow this; keep it consistent.
- Comments explain *why*, not *what*. Strip a comment if the code
  it describes is already self-explanatory.

## Forbidden moves

- **Never** silently disable the gate. `use_gate: false` is rejected
  in `flatten_config` and at trainer startup; do not add a code path
  that skips it.
- **Never** edit inside `SLOW_UPDATE_START`/`END` from a step-level
  edit. Only `replace_slow_update_field` may write there.
- **Never** commit a real API key. `.env` is gitignored; `.env.example`
  ships templates only.
- **Never** call `store_memory` (global rule) — promote to
  `dev_docs/lessons.md` instead.
- **Never** chain multiple unrelated changes into one commit just
  because they were noticed together.
- **Never** propagate fork-only defaults upstream.
  `_BACKEND_DEFAULT_MODELS["copilot_cli_exec"] = "claude-opus-4.7-1m-internal"`
  is an internal-only model and a fork-private default. If a slice
  becomes cherry-pick-ready for `microsoft/SkillOpt`, replace this
  default with a publicly-available model (e.g. `claude-sonnet-4.5`
  or `gpt-5.5`) in the upstream-bound diff.

## When to ask the user vs. proceed

- Architectural changes (new pipeline stage, new backend type, new
  config schema): always present a short plan first.
- Routine bug fixes, doc updates, test additions, small refactors
  with clear scope: just do it; surface in the changelog.
- Anything that would diverge the fork from upstream in a way that
  blocks future cherry-picks: stop and ask.

## Verification gate (project-specific)

Before claiming "training works" on any change to the loop:

1. `python scripts/train.py --help` parses without error.
2. The smallest end-to-end run completes one full step on the
   SearchQA split (one epoch, batch_size small enough to fit).
3. `outputs/<run>/best_skill.md` is written and non-empty.
4. `python scripts/eval_only.py` succeeds on that `best_skill.md`.

If you cannot run all four, say so — do not claim verification.
