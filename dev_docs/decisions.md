# Decisions Log

> One entry per architectural / design / config choice that isn't
> obvious from the code itself. Append-only; do not edit past
> decisions in place — record reversals as new entries.

## Format

```markdown
## YYYY-MM-DD — <decision title>

**Context.** What problem prompted the choice.
**Options considered.** At least two.
**Decision.** What was picked.
**Why.** The deciding factors.
**Trade-offs / costs.** What this gives up.
**Reversal cost.** What it would take to undo.
**Code refs.** Files / lines that implement it.
```

---

## 2026-05-31 — Internal dev docs live under `dev_docs/`, not `docs/`

**Context.** `docs/` is the public mkdocs site that publishes to
`microsoft.github.io/SkillOpt`. Putting internal AI/dev narrative
under `docs/` would either leak into the published site or require
mkdocs exclude rules.

**Options considered.**
1. `docs/internal/` — nested under existing docs.
2. `notes/` — neutral top-level folder.
3. `dev_docs/` — explicit top-level folder.

**Decision.** `dev_docs/` at repo root.

**Why.** Names the role exactly; impossible to confuse with the
public site; matches the user's `sparrow-x-dev ↔ sparrow-x` pattern
in spirit ("the dev companion of the public-shape repo").

**Trade-offs / costs.** Adds a new top-level folder. Mild churn if
upstream ever adopts a different convention.

**Reversal cost.** Low. `git mv dev_docs <new_name>` and update
`AGENTS.md`.

**Code refs.** `AGENTS.md`, `dev_docs/README.md`.

---

## 2026-05-31 — `AGENTS.md` at repo root for AI-agent discovery

**Context.** Multiple AI tools (Claude Code, Copilot CLI, Cursor,
Codex CLI, etc.) auto-discover `AGENTS.md` at repo root. Without
one, each tool starts cold and re-derives project conventions.

**Decision.** Ship a thin `AGENTS.md` that points at
`dev_docs/rules.md` and `dev_docs/architecture_overview.md`.

**Why.** Single source of truth for project rules stays in
`dev_docs/`; `AGENTS.md` is the discovery shim. Avoids duplication.

**Trade-offs / costs.** One more top-level markdown file.

**Reversal cost.** Delete the file.

**Code refs.** `AGENTS.md`.

---

# Pre-existing decisions documented from the codebase

The entries below are reconstructed from existing code and prior
commit history — they record decisions that were already made before
this dev-docs scaffold existed, so future agents can understand the
*why*.

---

## (pre-2026-05-31) — `slow_update_gate_with_selection` defaults to `false` on `main`

**Context.** The paper protocol uses gated slow-update acceptance
(Section 3.6): the slow-update candidate is evaluated on the
selection split and accepted only if it passes the same validation
gate as a step-level edit. Post-submission a force-accept variant
was added.

**Decision.** `_base_/default.yaml` defaults the flag to `false`
(force-accept).

**Why.** Force-accept is the newer post-submission behavior and was
chosen as the `main` default. Paper-aligned reproduction is opt-in
via the flag.

**Trade-offs / costs.** The default no longer reproduces paper
numbers exactly. Mitigated by:
- README explicitly calls this out.
- The provided `ckpt/<bench>/gpt5.5_skill.md` artifacts were trained
  with the paper-aligned gated mode and remain reproducible by
  flipping the flag.

**Code refs.**
- `configs/_base_/default.yaml:81` (`slow_update_gate_with_selection: false`)
- `skillopt/optimizer/slow_update.py` (implementation)
- `README.md` "Slow-update acceptance mode" section.

---

## (pre-2026-05-31) — Gate validation is mandatory

**Context.** Earlier code allowed `use_gate: false` to disable
validation. That made it possible to ship skills that never
improved on the held-out set.

**Decision.** This branch rejects `use_gate: false` outright.

**Why.** Without the gate, accept/reject is meaningless and the
"trained" skill could be strictly worse than the initial.
Reproducibility and the paper claims depend on the gate.

**Trade-offs / costs.** Removes a knob. Users who want
gate-disabled behavior must fork.

**Code refs.**
- `skillopt/config.py:flatten_config` raises if
  `evaluation.use_gate is False`.
- `skillopt/engine/trainer.py` re-checks at startup.

---

## (pre-2026-05-31) — Default `gate_metric` is `hard` (paper); `soft` / `mixed` are opt-in

**Context.** PR #25 added support for soft and mixed gate metrics
to handle the small-selection-set + continuous-reward edge case
where the hard gate rejects every candidate and training stalls.

**Decision.** `hard` remains the default. The `soft` / `mixed`
modes ship as an opt-in feature config at
`configs/features/soft_gate.yaml`.

**Why.** Paper-reported numbers were produced under `hard`. The
soft variants are useful but should not silently change the default
behavior of stock configs.

**Code refs.**
- `skillopt/evaluation/gate.py:select_gate_score`
- `configs/features/soft_gate.yaml` (with header comment listing
  when to use and when not to)
- `README.md` "Gate metric" section.

---

## (pre-2026-05-31) — `SLOW_UPDATE` block in skill is protected from step-level edits

**Context.** The slow-update writes a free-form guidance block into
the skill document at epoch boundaries. Step-level analyst edits
could in principle target / overwrite that block, destroying
cross-epoch information.

**Decision.** A pair of HTML comment markers (`SLOW_UPDATE_START` /
`SLOW_UPDATE_END`) delimits the block. Edit application skips any
edit whose target falls inside the block; `append` / `insert_after`
fallbacks route around it.

**Code refs.**
- `skillopt/optimizer/skill.py:_is_in_slow_update_region`
- `skillopt/optimizer/slow_update.py:replace_slow_update_field`
- Each analyst prompt under `skillopt/prompts/analyst_*.md` carries
  an `IMPORTANT:` warning about the protected region.

---

## (pre-2026-05-31) — Optimizer and target backends are decoupled

**Context.** A strong optimizer (e.g. GPT-5.5) reasoning about a
smaller / cheaper target (e.g. Qwen-3.5-4B, MiniMax) is a common
production setup. Earlier code shared one backend for both roles.

**Decision.** `set_optimizer_backend` and `set_target_backend` are
independent. `set_backend` becomes a legacy convenience that sets
both. Per-vendor `configure_*` functions exist for both roles.

**Code refs.**
- `skillopt/model/backend_config.py:set_optimizer_backend`,
  `set_target_backend`.
- `skillopt/model/__init__.py:set_backend` (legacy adapter).
