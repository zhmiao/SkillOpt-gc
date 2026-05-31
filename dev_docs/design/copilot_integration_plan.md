# Copilot Integration Plan

> **Status.** Proposal — pending user direction on scope and order.
> **Created.** 2026-05-31.
> **Owner.** SkillOpt-gc tech lead.
> **Linked ideas.** `COPILOT-1`..`COPILOT-9` in `dev_docs/ideas.md`.

## What the user asked for

Two coupled asks:

1. **Add Copilot CLI as a backend** in SkillOpt. Today the supported
   target backends are `openai_chat`, `claude_chat`, `qwen_chat`,
   `minimax_chat`, `codex_exec`, `claude_code_exec`. There is no
   `copilot_cli_exec` (or similar). The user wants parity so the
   `copilot` CLI can be used as the *target* harness during rollout
   (and possibly the *optimizer* harness too).

2. **Expand SkillOpt to optimize "complicated skills"** like those
   under `~/.copilot/skills/`. To do this, every candidate skill
   document must be plugged into a target that can actually exercise
   the skill end-to-end. For copilot-CLI-native skills (which use
   `task` background agents, `read_agent`, `write_agent`,
   `ask_user`, `manage_schedule`, etc.) that target IS the copilot
   CLI — so ask #1 is a prerequisite for the interesting half of
   ask #2.

This doc covers both parts so the user can see the dependency graph
before choosing what to build first.

---

# Part A — Copilot CLI as a SkillOpt backend

## A.1 Reference shape (how the existing exec backends look)

`codex_exec` and `claude_code_exec` already follow a uniform
pattern. Mirroring it for `copilot_cli_exec` is the cheapest
delivery path.

| Layer | File | What changes |
|---|---|---|
| Per-backend constants + `configure_*` / `get_*` | `skillopt/model/backend_config.py` | Add `COPILOT_CLI_EXEC_*` env-backed vars, `configure_copilot_cli_exec()`, `get_copilot_cli_exec_config()` |
| Backend validation set | `skillopt/model/backend_config.py:67` (`set_target_backend`) | Add `"copilot_cli_exec"` to the allowed set; add to `is_target_exec_backend()` |
| Alias / default-model registry | `skillopt/model/common.py:19` (`_BACKEND_DEFAULT_MODELS`) + `:31` (`_BACKEND_ALIASES`) | Add `copilot_cli_exec → "gpt-5.5"` (or whatever default is sensible); add `copilot`, `copilot_cli` aliases |
| Harness implementation | `skillopt/model/codex_harness.py` (or new `copilot_harness.py`) | Add `run_copilot_cli_exec(...)` modeled on `run_claude_code_exec`. Add CLI-only path first; SDK path later if `@github/copilot-cli` ships one |
| Dispatcher | `skillopt/model/codex_harness.py:1019` (`run_target_exec`) | Add `if backend == "copilot_cli_exec": return run_copilot_cli_exec(...)` |
| Public re-exports | `skillopt/model/__init__.py:11-23` | Re-export `configure_copilot_cli_exec`, `get_copilot_cli_exec_config` |
| Config flatten map | `skillopt/config.py:_FLATTEN_MAP` | Add `model.copilot_cli_exec_path`, `_effort`, `_allow_all_tools`, `_session_state_root`, etc. |
| Defaults YAML | `configs/_base_/default.yaml` (model section) | Add `copilot_cli_exec_*` knobs mirroring the claude_code_exec block |
| Trainer wiring | `skillopt/engine/trainer.py:599` (backend resolution) and `:625` (`configure_*` calls) | Add `elif backend in {"copilot_cli", "copilot_cli_exec"}: target_backend = "copilot_cli_exec"` + a `configure_copilot_cli_exec(...)` call |
| Eval-only wiring | `scripts/eval_only.py` | Same as trainer.py for the backend-resolution and configure path |
| Env template | `.env.example` | Add a `# ── GitHub Copilot CLI (for copilot_cli_exec backend) ──` block |
| User docs | `docs/guide/new-backend.md`, `README.md` "Configure API Credentials" | Document the new backend in the same format as MiniMax |
| Internal docs | `dev_docs/architecture_overview.md § Backend matrix` | Add the new row |

## A.2 Copilot CLI quirks worth knowing now

From `copilot --help` (the binary at `/run/user/1001/fnm_multishells/.../bin/copilot`, version 1.0.57-3 in this environment):

- **Non-interactive mode**: `copilot -p "<prompt>" --allow-all-tools`
  (the `--yolo` alias is also available). This is the rollout shape
  SkillOpt needs.
- **Permissions**: `--allow-all` = `--allow-all-tools` +
  `--allow-all-paths` + `--allow-all-urls`. SkillOpt rollouts must
  pass `--allow-all` (or equivalent) because they run unattended.
  Granular knobs (`--allow-tool=...`, `--deny-tool=...`) exist for
  tighter sandboxing.
- **Reasoning**: `--effort none|low|medium|high|xhigh|max` — maps
  cleanly to SkillOpt's `reasoning_effort` knob.
- **Model selection**: `--model <name>` — list of available models
  comes from `copilot providers` / `copilot model`. Defaults vary
  by user account.
- **Session**: `--session-id <uuid>` lets you give each rollout a
  named session (good for output dir naming + post-hoc retrieval).
- **Working directory**: there is **no** `--cwd` flag visible in
  `--help`; copilot uses `process.cwd()`. Each rollout must `chdir`
  into a clean per-task scratch dir before spawning copilot, OR pass
  `--add-dir <path>` and tell the skill to operate on that subdir.
  The codex backend handles this via
  `_default_working_directory()` and `--add-dir`; copilot will
  follow the same pattern.
- **Attachments**: `--attachment <path>` for images / native docs.
  Same role as codex/claude's `--image` / `--data-dir`.
- **Custom agents**: `--agent <agent>` selects a user-defined agent.
  Relevant if SkillOpt wants to drive a specific custom agent rather
  than the default copilot persona.
- **MCP**: `--additional-mcp-config <json|@file>` augments
  `~/.copilot/mcp-config.json`. Useful if a rollout needs special
  MCP servers (e.g. markitdown for doc conversion). Default is to
  inherit the user's MCP config — fine for most cases.

## A.3 Gotchas surfaced by the existing exec backends

These bit the codex / claude-code backends and will bite copilot too
unless designed in from day one:

1. **Empty-response retries.** Both existing exec backends ship an
   `EXEC_EMPTY_RESPONSE_RETRIES` knob (default 1) because CLIs
   occasionally return an empty assistant message under network /
   model flake. Copilot CLI needs the same handling — see
   `run_claude_code_exec` for the pattern (re-prompt with attempt
   counter).
2. **SDK vs CLI mode.** `claude_code_exec` and `codex_exec` both
   support `use_sdk: auto|sdk|cli`. Copilot may or may not have an
   SDK; check `npm view @github/copilot-cli` or equivalent. Start
   with CLI only; add SDK path later if it materializes.
3. **Output parsing.** Codex exec uses a JSON output schema
   (`ANSWER_SCHEMA`) so the rollout can extract a deterministic
   answer. Copilot CLI is free-form by default. SkillOpt either:
   (a) instructs the skill to wrap its answer in
   `<answer>...</answer>` tags, or (b) parses the last assistant
   message and trusts the format. The codex path is more robust.
4. **Sandbox.** Codex has `--sandbox workspace-write|read-only`.
   Copilot has `--allow-all-paths` (off by default). For SkillOpt
   rollouts that don't need to write files, run with `--allow-tool`
   only (no `--allow-all-paths`).
5. **Artifact persistence.** Both existing backends call a
   `_persist_*_artifacts(work_dir, raw, response)` helper to dump
   the full trace under `outputs/<run>/steps/.../rollout/.../`.
   Copilot must do the same so reflect / debugging has the full
   tail.
6. **Token accounting.** The existing harnesses do NOT push token
   counts into `skillopt/model/common.py:tracker` for exec
   backends (the trace gives raw output but no usage block). This
   is a known limitation that carries forward to copilot. If we
   want token tracking for copilot rollouts, we'd have to parse the
   transcript or wait for a CLI flag exposing usage.

## A.4 Optimizer-side support

The asks say "support to copilot" — the obvious interpretation is
**target-side**. But copilot CLI can also run as the *optimizer*
(producing analyst patches, merging, ranking). For that:

- `set_optimizer_backend` (in `backend_config.py:49`) currently
  allows only `openai_chat | claude_chat | minimax_chat`. To allow
  copilot CLI as optimizer, add `copilot_cli_exec` to that set, and
  wire `chat_optimizer` / `chat_optimizer_messages` in
  `skillopt/model/__init__.py` to call a copilot path when
  `get_optimizer_backend() == "copilot_cli_exec"`.
- This is a strictly bigger change than target-side because the
  optimizer flow is *message-list* based (multi-turn) and uses
  structured tool calls (analyst → patch JSON). The copilot CLI's
  non-interactive `-p` mode is single-prompt; it does not have a
  message-list API. We'd need to either serialize the message list
  into one giant prompt or build a per-turn shim. Recommend
  deferring optimizer-side support until target-side is shipped and
  the user actually wants to use copilot as optimizer.

## A.5 Implementation effort estimate

| Slice | Files touched | LOC ballpark | Risk |
|---|---|---|---|
| A1: target-only `copilot_cli_exec` (CLI path, no SDK) | backend_config.py (+~70), common.py (+~5), codex_harness.py (+~200), config.py (+~10), trainer.py (+~30), eval_only.py (+~20), default.yaml (+~12), .env.example (+~6), docs (+~50), dev_docs (+~30) | ~430 | Low — straight clone of `run_claude_code_exec` |
| A2: optimizer-side `copilot_cli_exec` | __init__.py dispatcher (+~80), common.py validation (+~5), backend_config.py expand allow-list (+~5), tests | ~100 | Medium — needs a message-list-to-prompt serialization |
| A3: SDK path (if @github/copilot-cli ships one) | copilot_harness.py (+~250) | ~250 | Medium — depends on SDK shape |

Minimum viable: A1 alone. A2 / A3 are deferrable.

---

# Part B — Copilot skills compatibility review

## B.1 What "optimizable by SkillOpt" actually requires

SkillOpt's training loop requires four things per task item:

1. **Bounded input.** A discrete task that the target can execute.
2. **Deterministic-enough rollout.** Same `(skill, task)` → similar
   output on retry. Skills that depend on huge external state
   (user clarification, multi-day sessions, live data) are weak
   fits.
3. **Scoreable output.** A `hard ∈ {0,1}` and `soft ∈ [0,1]` grader
   that runs without human intervention. Without this, the gate
   has nothing to compare and training cannot accept/reject.
4. **A non-trivial "skill" surface.** The skill document must
   meaningfully change what the target produces. Skills that are
   thin wrappers over a script (the LLM just decides which flag to
   pass) have little for SkillOpt to optimize.

## B.2 Per-skill matrix

Reading every `~/.copilot/skills/<skill>/SKILL.md` and classifying
against the four criteria above.

| Skill | LOC (SKILL.md) | Input shape | Output shape | Grader available? | Verdict | Notes |
|---|---:|---|---|---|---|---|
| **stop-slop** | 68 | prose blob | rewritten prose | YES — regex on banned patterns + LLM judge for naturalness | ★ **A — direct fit** | Canonical example. Already user-confirmed. Tiny dataset of input prose → cleaned prose can drive training in hours. |
| **ascii-align** | 255 | markdown with diagrams | same markdown, aligned | YES — `python3 ~/dotfiles/scripts/ascii-align.py check <file>` returns 0/1 | ★ **A — direct fit** | Better than stop-slop: deterministic linter. Per-item dataset = mis-aligned markdown files; binary hard score from the linter; soft score from per-diagram column-error count. |
| **explain** | 550 | source doc / topic | structured explain report w/ Source Coverage appendix | PARTIAL — fidelity ("every source point covered") is checkable via the appendix; aesthetic quality needs LLM judge | **B — needs adapter work** | The skill itself enforces "every source point gets an ID and a location" — that's the grader. Dataset = (source doc, expected appendix entries). |
| **session-init** | 211 | project name | "where we are / what's next" briefing with citations | PARTIAL — citation correctness is checkable (file/line must exist); content correctness vs ground truth is harder | **B — needs adapter work** | Per-project ground-truth state required. Niche. |
| **test** | 67 | code diff + optional test pattern | shell of test commands actually run | PARTIAL — "did the right tests run?" needs ground-truth label per item | **B — needs adapter work** | Dataset = (diff, expected_test_files). Grader = jaccard(actual_tests_run, expected_tests). |
| **check-scope** | 123 | ledger op + args | mutated JSON ledger | YES — JSON state assertion | **B — possible but small surface** | Mostly deterministic. SkillOpt would only optimize the natural-language summarization the skill emits to the user, not the JSON ops themselves. Probably not worth the bench setup. |
| **doc-fix** | 605 | docs dir | applied doc edits + converged report | YES — second iteration of doc-fix on the output should report 0 findings; also a fidelity check against source | **C — heavyweight** | Multi-agent iterative skill. One rollout = one full doc-fix run. Expensive (~minutes per item) and hard to seed determinism. Possible but big lift. |
| **audit-fix** | 938 | code dir | applied edits + tests + converged report | YES — final state should pass `pytest` + linters AND a second iteration converges immediately | **C — heavyweight** | Same shape as doc-fix. One rollout costs minutes. Possible. |
| **code-review** | 587 | code dir / diff | review report | PARTIAL — "did the review catch the planted bug?" requires curated bug-injection dataset (rust-bench / SWE-bench-style) | **C — heavyweight** | Optimization target is the *review prompt* (what to look for). Dataset = (diff_with_bug, bug_description). Per-item LLM judge: did the review mention the bug? |
| **design** | 513 | design task | design proposals from N architects + consensus | NO obvious automatic grader — design quality needs human judgment or a strong LLM judge | **C — heavyweight, weak grader** | Best to defer. The grader is the bottleneck, not the harness. |
| **research** | 486 | research question | research report w/ citations | PARTIAL — citation existence (URLs resolve, files exist) is checkable; factual accuracy needs LLM judge w/ ground-truth corpus | **C — heavyweight** | Per-item dataset = (question, expected_findings). Niche unless you have a research benchmark on hand. |
| **implement** | 602 | task description | applied code + tests passing | YES — `pytest` (or whatever test command the task ships) | **C — heavyweight** | This is essentially SWE-bench. The "skill" being optimized would be the implement-team SKILL.md itself. Possible but the existing SWE-bench adapter in SkillOpt registry already targets this problem at the model level — optimizing the team-coordination skill is a separate axis. |
| **session-init / wrap-up** | 211 / 341 | session state | tech-lead briefing + git ops | PARTIAL — ledger correctness is checkable; the prose briefing needs LLM judge | **B/C border** | Bookkeeping-heavy; the optimizable surface is small. Defer. |
| **skill-creator** | 483 | "make me a skill that does X" | a new SKILL.md + supporting files | PARTIAL — meta-skill; grader would compare generated skill against curated reference skills | **C — heavyweight, very self-referential** | Optimizing skill-creator means SkillOpt is optimizing the thing that creates the things SkillOpt optimizes. Theoretically interesting; deferral recommended. |
| **aml** | 91 | subcommand + args | shell calls + status text | NO meaningful "skill" surface — it's a CLI wrapper. The LLM picks the subcommand but the rest is the AML SDK | **D — out of scope** | |
| **benchmark** | 77 | result file paths | comparison table | NO — deterministic data processing | **D — out of scope** | |
| **ablation** | 118 | plan/track/report args | yaml/json/csv operations | NO meaningful skill surface | **D — out of scope** | |
| **experiment** | 93 | config op args | YAML mutations | NO meaningful skill surface | **D — out of scope** | |
| **si-promote / si-review** | 81 / 88 | memory file ops | memory file mutations | NO — workflow UI | **D — out of scope** | |

## B.3 Why the user's intuition on `stop-slop` is right

`stop-slop` is the simplest legitimate target:

- **Bounded task** — paragraph of prose in, paragraph of prose out.
- **Cheap rollout** — single chat call to the target. Sub-second.
- **Hard grader** — regex against `stop-slop/references/phrases.md`
  banned list. `hard = (no banned phrases)`.
- **Soft grader** — fraction of banned-phrases-removed +
  LLM-judge-as-readability.
- **Meaningful skill** — the existing `SKILL.md` is 68 lines of
  rules. Plenty of room to evolve heuristics (when to keep an
  intensifier, when to break a "throat-clearing opener" rule for
  flow, etc.).

This is the canonical first benchmark. ETA: env adapter scaffold
(based on `skillopt/envs/searchqa/`) + a dataset of ~200 input
paragraphs + the grader = a working `stop_slop` env in a few hours.

## B.4 Tier-A vs Tier-B recommendation

| Tier | Skills | Why first |
|---|---|---|
| Tier A (build now) | `stop-slop`, `ascii-align` | Both have automatic graders, cheap rollouts, well-bounded tasks. Two envs cover prose-edit and structure-edit. |
| Tier B (build next, after A is shipped + Copilot backend exists) | `explain`, `test`, `code-review` | Each has a defensible automatic grader if a curated dataset is built. Each exercises the copilot harness in a different way (long-form generation, tool-use, judgment). |
| Tier C (research-grade, defer) | `doc-fix`, `audit-fix`, `implement`, `research`, `design` | Heavyweight rollouts (minutes each), or weak automatic graders, or both. Worth doing once Tier A+B prove the pipeline. |
| Tier D (out of scope) | `aml`, `benchmark`, `ablation`, `experiment`, `si-*`, `check-scope`, `session-init`, `wrap-up`, `skill-creator` | Either no meaningful LLM-skill surface, or pure workflow UI. |

---

# Part C — Roadmap

## C.1 Critical path

```
Step 1.  Add copilot_cli_exec target backend (A.1)
            ↓
Step 2.  Build stop-slop env adapter under skillopt/envs/stop_slop/
         + tiny dataset + regex+judge grader (Tier A)
            ↓
Step 3.  Smoke run: train a stop-slop skill on copilot_cli_exec target
         end-to-end. This is the integration test that proves both
         pieces fit together.
            ↓
Step 4.  Build ascii-align env adapter (Tier A, second target).
            ↓
Step 5.  Update docs (README, dev_docs/architecture_overview.md,
         dev_docs/decisions.md) once the first env trained
         successfully. Decision: do we add a copilot-cli-exec
         optimizer-side path (A.2)? Decide here, not before.
            ↓
Step 6.  Tier B environments (in any order based on user priority).
```

## C.2 Smallest standalone deliverables

Each can be shipped independently; the rest unblock as each lands.

| Slice | Deliverable | Acceptance |
|---|---|---|
| S1 | `copilot_cli_exec` target backend (Part A.1) | A unit-style smoke that calls `copilot -p "say hello" --allow-all-tools` via the harness and gets a non-empty string back. |
| S2 | `stop_slop` env adapter + 50-item dataset + grader | `python scripts/eval_only.py --config configs/stop_slop/default.yaml --skill skillopt/envs/stop_slop/skills/initial.md --split valid_unseen` returns `hard` score with the initial skill. |
| S3 | `stop_slop` end-to-end training run on copilot_cli_exec | `outputs/<run>/best_skill.md` exists, non-empty, and `valid_unseen` hard score ≥ baseline hard score. |
| S4 | `ascii_align` env adapter + dataset of mis-aligned md files + linter-based grader | Same shape as S2/S3. |

## C.3 Open questions for the user

1. **Which model under copilot?** Copilot CLI's `--model` flag
   supports several. Pick one for `_BACKEND_DEFAULT_MODELS["copilot_cli_exec"]`
   in `common.py`. Suggestion: `claude-opus-4.7-1m-internal`
   (matches what the user runs interactively) — but defaults should
   not lock to internal-only models. Likely better default:
   `claude-sonnet-4.5` or `gpt-5.5`. Needs user input.
2. **Optimizer-side copilot support (A.2)** — build it in S1, or
   defer? Recommend defer; revisit after S3.
3. **Dataset sourcing for `stop_slop`** — the user could provide
   real AI-generated prose snippets they've corrected, OR we
   synthesize a 200-item dataset from public LLM outputs +
   reference rewrites. Which?
4. **`ascii-align` dataset** — pull mis-aligned md files from the
   user's own git repos (sparrow-engine-dev / bongo / etc.) under
   `data/ascii_align_split/`, or curate synthetic ones?
5. **Where do training outputs live?** Today the trainer writes
   `outputs/<run>/`. For the experiments we'd be running on the
   user's own skills, those outputs may be large and noisy. Do we
   want a per-skill subdir under `outputs/skills/<skill>/<run>/`?
6. **Branch / commit strategy for the eventual edits to
   `~/.copilot/skills/<skill>/SKILL.md`** — when a SkillOpt run
   produces a new `best_skill.md` for `stop-slop`, do we want a
   script that copies it back to the live skill (with git
   versioning under `~/dotfiles/copilot/...`), or keep them
   separate and let the user copy manually?

## C.4 What this doc does NOT propose

- No source code changes yet. This is a plan; the user picks order
  and scope.
- No public-facing `docs/` changes. Once a slice ships, the public
  `docs/guide/new-backend.md` and README get updated as part of
  that slice.
- No commits to upstream `microsoft/SkillOpt`. The personal-fork
  rules in `dev_docs/rules.md` still apply — if a slice would be
  cherry-pickable upstream, we keep public surfaces clean of
  fork-only details.
