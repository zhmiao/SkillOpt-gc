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
