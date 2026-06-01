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

## 2026-05-31 — `copilot_cli_exec` ships CLI-only; no SDK path

**Context.** The existing `codex_exec` and `claude_code_exec` backends
support a `use_sdk = "auto" | "sdk" | "cli"` knob so they can call
`openai-codex-sdk` / `claude-agent-sdk` Python clients in-process,
falling back to subprocess CLI if the SDK is missing.

**Options considered.**
1. Mirror the same `use_sdk` knob and stub the SDK path.
2. CLI-only — no `use_sdk` knob; always `subprocess.run(copilot -p ...)`.

**Decision.** Option 2 — CLI-only.

**Why.**
- GitHub Copilot CLI v1.0.57 (the version available on this machine)
  does not ship a Python SDK. `npm view @github/copilot-cli` shows
  only the CLI binary; there is no `import copilot_sdk` equivalent
  to `claude_agent_sdk` or `openai_codex_sdk`.
- Stubbing a non-existent SDK path adds dead code and a misleading
  `use_sdk` flag that does nothing.

**Trade-offs / costs.**
- CLI subprocess overhead per rollout (~hundreds of ms for process
  startup) vs in-process SDK calls. Acceptable for SkillOpt rollouts
  — the model call itself dominates.
- If Copilot ships an SDK later, we'll add the `use_sdk` knob then.
  The current `run_copilot_cli_exec` wrapper has the right shape to
  add an SDK branch without breaking the public signature.

**Code refs.**
- `skillopt/model/codex_harness.py:run_copilot_cli_exec` (CLI-only
  retry loop; docstring notes the no-SDK choice).
- `skillopt/model/backend_config.py:configure_copilot_cli_exec` (no
  `use_sdk` parameter, unlike `configure_claude_code_exec`).

---

## 2026-05-31 — `stop_slop` dataset source: `HumanEmbedding` repo

**Context.** The first SkillOpt-optimized copilot skill is
`stop-slop` (per user direction). It needs a labeled prose dataset.

**Options considered.**
1. Synthesize from public LLM outputs + reference rewrites
   (turnkey but low signal).
2. Hybrid: small real corpus + bulk synthetic.
3. Mine `/home/miao/repos/HumanEmbedding` — the user's 8-week
   essay revision history with full Claude Code audit/review trails.

**Decision.** Option 3 (`HumanEmbedding`) with `dataset_option=max`:
hand-labeled before/after + auto-extracted paragraph diffs +
worktree-mined negative examples. Both banned-pattern sources unioned
(`ai_writing_tells.md` + `stop-slop/references/phrases.md`).

**Why.** The repo contains:
- 20 essay versions (v2 → v22) with diffable revision history.
- A `docs/research/slop_revision/round_02/researcher-plan_report.md`
  with explicit, hand-curated (before, after, banned-pattern,
  regression-check) entries — perfect SkillOpt training items.
- 4 rounds of audit/reviewer reports under `docs/review/round_*/`
  with `auditor_change_plan.md` per round.
- `docs/research/ai_writing_tells.md` — the user's own catalog of
  AI tells, directly usable as the hard-gate banned list.
- 18MB of `.claude/worktrees/` — auditor/reviewer agent transcripts
  including proposed-but-rejected edits (negative examples).

This is human-labeled by the user, on the user's own writing, at
section-level fidelity. Nothing synthetic comes close.

**Trade-offs / costs.**
- Extraction is 6–8 hours of mining (delegated to parallel agents).
- The corpus is essay-domain prose — the resulting `stop_slop`
  skill will be tuned for long-form analytical prose; less so for
  e.g. PR descriptions or commit messages. Mitigated by including
  the general `stop-slop/references/phrases.md` patterns in the
  banned-list union.
- `HumanEmbedding` is private; the extracted dataset under
  `data/stop_slop_split/` is therefore also fork-private. Acceptable
  since `SkillOpt-gc` itself is the user's personal fork.

**Code refs.** `dev_docs/design/dataset_construction_plan.md`,
`dev_docs/plan.md § Phase 0.5`.

---

## 2026-05-31 — Copilot integration first-slice parameters

**Decisions captured from the Open Questions form in
`design/copilot_integration_plan.md § C.3`.**

| Question | Choice | Why |
|---|---|---|
| Default model for `copilot_cli_exec` | `claude-opus-4.7-1m-internal` | Matches what the user runs interactively. **Fork-only default — must NOT propagate upstream.** Add a guard in `dev_docs/rules.md`. |
| Optimizer-side `copilot_cli_exec` (`COPILOT-2`) | Defer | Adds ~100 LOC + a serializer; not blocking. Revisit after `COPILOT-3` smoke. |
| Tier-A first env | `stop_slop` | User picked over `ascii_align`. Higher real-world value (user's actual writing workflow). |
| `stop_slop` dataset | `/home/miao/repos/HumanEmbedding` with `dataset_option=max` | See separate decision entry above. |
| `ascii_align` dataset (when COPILOT-4 starts) | Pull from user's own repos | Real mis-aligned diagrams; high signal. |
| Output directory layout | Per-skill subdir (`outputs/skills/<skill>/<run>/`) | Cleaner separation from benchmark runs. Lands with `COPILOT-9` alongside `COPILOT-1`. |

**Code refs.** `dev_docs/plan.md § Phase 0.5..Phase 2`,
`dev_docs/design/copilot_integration_plan.md`,
`dev_docs/design/dataset_construction_plan.md`.

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
