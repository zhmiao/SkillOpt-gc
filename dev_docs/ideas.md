# Ideas / Backlog

> Open work with stable IDs. When an item becomes active work, move
> it (don't copy) to `dev_docs/plan.md` and strike through here.
> When an item completes, strike through here and note the commit
> SHA. Stable IDs let other docs and commits reference items
> unambiguously.

ID prefixes:

- `OBS-` — observation from the repo sweep; may or may not need action.
- `CLEAN-` — cleanup / doc consistency work.
- `REF-` — refactor opportunity.
- `FEAT-` — new feature or capability.
- `TEST-` — test coverage.
- `CI-` — continuous integration work.
- `COPILOT-` — Copilot CLI integration (backend + skill envs).

---

## Items from the 2026-05-31 Copilot-integration review

See `dev_docs/design/copilot_integration_plan.md` for the full
design. The IDs below are the implementable slices.

### COPILOT-1 — Target backend: `copilot_cli_exec` (CLI mode)

**Where.** `skillopt/model/backend_config.py`, `codex_harness.py`,
`common.py`, `config.py`, `engine/trainer.py`, `scripts/eval_only.py`,
`configs/_base_/default.yaml`, `.env.example`.
**What.** Add a new target backend modeled on `claude_code_exec`.
Non-interactive `copilot -p "<prompt>" --allow-all-tools` is the
rollout shape.
**Impact.** Unblocks all copilot-CLI-native skill envs (stop-slop,
ascii-align, etc.) since those skills depend on copilot's
`task`/`read_agent`/`write_agent` tools that no other harness has.
**Effort.** ~430 LOC across ~10 files. Low risk — straight clone of
`run_claude_code_exec`.
**Related.** Part A.1 of the integration plan; blocks COPILOT-3..9.

### COPILOT-2 — Optimizer-side `copilot_cli_exec` (deferred)

**Where.** Same module set as COPILOT-1, plus
`skillopt/model/__init__.py:chat_optimizer*`.
**What.** Allow `optimizer_backend=copilot_cli_exec`. Requires a
message-list → single-prompt serializer because copilot CLI's `-p`
mode is single-shot.
**Impact.** Lets the same harness run both optimizer and target —
useful when only copilot is available, but not blocking anything.
**Effort.** ~100 LOC.
**Action.** Defer until after COPILOT-3 ships. Decide based on real
need.
**Related.** Part A.2 of the integration plan.

### COPILOT-3 — `stop_slop` env adapter

**Where.** New `skillopt/envs/stop_slop/{adapter,dataloader,rollout,reflect}.py`,
`skillopt/envs/stop_slop/skills/initial.md`,
`skillopt/envs/stop_slop/prompts/*.md`,
`configs/stop_slop/default.yaml`,
`data/stop_slop_split/{train,val,test}/items.json`.
**What.** First end-to-end target for SkillOpt-optimized copilot
skills. Per-item task = (prose blob, golden rewrite or banned-phrase
list). Hard grader = regex against `~/.copilot/skills/stop-slop/references/phrases.md`.
Soft grader = fraction of banned phrases removed + LLM judge for
naturalness.
**Impact.** Proves the pipeline. Also delivers an actual
better-than-baseline stop-slop skill for the user's own writing.
**Effort.** Adapter ~200 LOC, dataset 50–200 items.
**Related.** Part B.3 + C.2 S2. Blocked by COPILOT-1.

### COPILOT-4 — `ascii_align` env adapter

**Where.** `skillopt/envs/ascii_align/...` + `configs/ascii_align/...`
+ `data/ascii_align_split/...`.
**What.** Second target. Per-item task = (mis-aligned markdown,
expected linter rc=0 after fix). Hard grader = `python3 ~/dotfiles/scripts/ascii-align.py check <file>` rc.
Soft grader = `(N_diagrams - N_remaining_errors) / N_diagrams`.
**Impact.** Demonstrates SkillOpt on a *structure-edit* skill (vs
stop-slop's *prose-edit*). Diversifies the eval surface.
**Effort.** Adapter ~200 LOC, dataset 30–100 markdown files.
**Related.** Part B.2 + C.1 Step 4. Blocked by COPILOT-1.

### COPILOT-5 — `explain` env adapter (Tier B)

**Where.** `skillopt/envs/explain/...`
**What.** Per-item task = (source doc, expected Source Coverage
appendix entries). Grader checks that every source point gets a
mapped report entry (the skill already enforces stable IDs in the
appendix, so this is mechanically checkable).
**Effort.** Adapter ~250 LOC; dataset is the bottleneck (each item
needs a curated source + expected coverage list).
**Status.** Defer until Tier A is shipped.

### COPILOT-6 — `test` env adapter (Tier B)

**Where.** `skillopt/envs/test_runner/...` (naming: avoid
`tests/` collision).
**What.** Per-item task = (diff, expected_test_files). Grader =
jaccard(actual_tests_run, expected_tests). Dataset can be derived
from real git history (one commit = one item; expected tests =
tests changed in same commit or its follow-ups).
**Status.** Defer until Tier A is shipped.

### COPILOT-7 — `code-review` env adapter (Tier B)

**Where.** `skillopt/envs/code_review/...`
**What.** Per-item task = (diff with planted bug, bug description).
Grader = LLM judge "did the review mention this bug?". Dataset
from SWE-bench-style bug-injection or curated rust-bench items.
**Status.** Defer until Tier A is shipped.

### COPILOT-8 — Tier-C heavyweight envs (doc-fix, audit-fix, implement, research, design)

**Where.** `skillopt/envs/{doc_fix,audit_fix,implement_team,research_team,design_team}/...`
**What.** Each one rollout = one full multi-agent skill execution.
Minutes per item.
**Status.** Research-grade. Defer until Tier A+B prove the pipeline
and we know what we're paying for. May not be worth it for some.

### COPILOT-9 — `outputs/` reorganization for skill experiments

**Where.** `skillopt/engine/trainer.py:_resolve_out_root` (or
wherever `out_root` is finalized).
**What.** When training a copilot-skill env, organize outputs under
`outputs/skills/<skill>/<run>/` instead of flat `outputs/<run>/`.
Avoid mixing benchmark runs with skill-optimization runs.
**Effort.** ~30 LOC + doc update.
**Status.** Land alongside COPILOT-3 (the first copilot-skill env).
**Related.** Open question C.3.5 in the integration plan.

---

## Items from the 2026-05-31 sweep

### OBS-1 — `set_optimizer_deployment` only routes to OpenAI + Claude

**Where.** `skillopt/model/__init__.py:461-464`.
**What.** `set_optimizer_deployment(deployment)` calls
`_openai.set_optimizer_deployment(...)` and
`_claude.set_optimizer_deployment(...)` but not the Qwen or MiniMax
backends. `set_target_deployment` two functions above
(`skillopt/model/__init__.py:454-458`) routes to all four.
**Impact.** If anyone configures `optimizer_backend=qwen_chat` or
`optimizer_backend=minimax_chat`, the deployment name will not be
forwarded to that backend's module-level state. Low blast radius —
GPT/Claude as optimizer is the realistic case — but the asymmetry
is a code-smell that will eventually mislead someone.
**Action.** Either add the missing calls or document the constraint
in `backend_config.py`. Decide which when an upstream patch is being
prepared, since it would be a small standalone fix.

### COPILOT-10 — Harness-side handling of `--effort` rejected by model

**Where.** `skillopt/model/codex_harness.py:_run_copilot_cli_exec`
(also affects `_run_claude_code_cli_exec` to a lesser extent).
**What.** Copilot CLI's `--effort` flag is global but the model can
reject it (e.g., `claude-sonnet-4.5` returns `Error: Model "X" does
not support reasoning effort configuration`). Currently the harness
always passes `--effort` when configured to a non-empty value, and
the model error becomes the entire rollout output.
**Impact.** Anyone configuring `copilot_cli_exec_effort=medium`
(the default) with a non-reasoning model gets silently-failed
rollouts that look like normal CLI output.
**Action.** Detect the specific error message in the harness retry
loop, drop `--effort` from the second attempt, log the demotion to
the trace summary. Alternatively, maintain a static block-list of
models that don't support effort (`claude-sonnet-4.5`,
`claude-haiku-4.5`, ...) — but this is brittle.
**Workaround for now.** Set `copilot_cli_exec_effort=none` in the
config when using a non-reasoning model. The stop_slop smoke does
this (see `scripts/smoke_stop_slop_env.py`).
**Effort.** ~20 LOC + a smoke test fixture.

### CLEAN-3 — `docs/guide/new-backend.md` is a stale generic template

**Where.** `docs/guide/new-backend.md` (130 lines).
**What.** References file names that don't exist (`base.py`,
`openai_model.py`, `claude.py`, `qwen.py`). The real modules are
`azure_openai.py`, `claude_backend.py`, `qwen_backend.py`,
`minimax_backend.py`, `codex_backend.py`, and now also
`run_copilot_cli_exec` inside `codex_harness.py`. Surfaced while
adding `COPILOT-1` — the guide can't be patched in place; it needs
a rewrite against the real codebase shape.
**Impact.** Anyone following the guide hits "file does not exist"
errors. Public mkdocs site renders the stale content.
**Action.** Rewrite against the real layout. Use the
`backend_config.py` + per-vendor module + `codex_harness.py` exec
dispatcher pattern as the canonical example. Reference the
`copilot_cli_exec` slice as the most recent worked example.
**Effort.** ~2 hours.

### CLEAN-1 — README references `configs/swebench/` but the directory does not exist

**Where.** `docs/index.md:110` lists `configs/swebench/` under
"Supported Benchmarks". `scripts/train.py:92-95` registers a
`swebench` adapter, but `glob` confirms no `configs/swebench/`
directory ships.
**Impact.** Users following the docs will hit "config not found".
**Action.** Either ship the config or remove the reference. The
README at the repo root is already careful about this (it lists
only the six configs that exist) — the mkdocs `docs/index.md` is
the file that needs alignment.

### CLEAN-2 — No `tests/` directory despite `pytest` in `[dev]` extras

**Where.** `pyproject.toml:48` declares `pytest>=8.0.0` under
`dev`. `glob '**/test_*.py'` returns nothing.
**Impact.** Refactors land without safety net. New contributors
have nowhere to put regression tests.
**Action.** When the first bug fix lands that warrants a regression
test, create `tests/` with `test_<module>.py` files alongside it.
Don't scaffold an empty tree.

### CI-1 — No CI workflows in the repo

**Where.** `glob '.github/workflows/**'` returns nothing.
**Impact.** Linting + tests are not enforced on PRs to the personal
fork. (Upstream may have CI; this fork does not.)
**Action.** When tests exist (CLEAN-2), add a minimal workflow:
`ruff check`, `ruff format --check`, `pytest`. Keep it Python-only;
no model calls.

### REF-1 — `skillopt/engine/trainer.py` is 2,071 LOC monolith

**Where.** `skillopt/engine/trainer.py`.
**Impact.** Hard to extend without merge conflicts; hard to test
sub-flows in isolation; the per-step pipeline, epoch-boundary
slow-update, meta-skill, resume logic, and selection eval all share
one function scope.
**Action.** Candidate decomposition:
- `engine/runtime_state.py` (load/save runtime state + history + skills)
- `engine/baseline.py` (initial-skill selection eval)
- `engine/step.py` (one per-step pipeline iteration)
- `engine/epoch_boundary.py` (slow-update + meta-skill)
- `engine/trainer.py` (top-level loop orchestrating the above)

Do this only when there is a concrete reason — extending the loop,
fixing a cross-cutting bug, or adding meaningful tests. Don't
refactor for its own sake.

### REF-2 — `scripts/train.py` and `scripts/eval_only.py` duplicate the env registry

**Where.** `scripts/train.py:36-95` and `scripts/eval_only.py:45-100`
both declare `_ENV_REGISTRY` and `_register_builtins` with the same
list of optional adapter imports.
**Impact.** Adding a new benchmark requires editing both files; easy
to forget the second one.
**Action.** Lift the registry into `skillopt/envs/__init__.py` and
import from there. The current `skillopt/envs/__init__.py` is
empty, so the surface is greenfield.

### FEAT-1 — Optional feature configs need a flat directory pattern

**Where.** `configs/features/soft_gate.yaml` is the only example.
**Observation.** As contributors land more opt-in feature configs
(see PR #25 pattern), a flat directory with one yaml per feature
will scale, but each file must keep the standard header (when to
use / when NOT to use / which paper claim).
**Action.** When the second feature config lands, write a tiny
README under `configs/features/` formalizing the pattern.

---

## Template for new ideas

```markdown
### <ID> — <one-line title>

**Where.** Files / lines.
**Impact.** Why this matters; who hits it.
**Action.** What "done" looks like; rough effort estimate.
**Related.** Cross-refs to other dev_docs entries.
```
