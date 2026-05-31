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

### Phase 0.5 — `stop_slop` dataset construction (active now)
Mine `/home/miao/repos/HumanEmbedding` for a labeled
`(prose_in, banned_patterns, gold_rewrite?, source)` dataset.
Three parallel extraction streams dispatched as background agents
(see `dev_docs/design/dataset_construction_plan.md`).

- [ ] Stream 1 (hand-labeled before/after): mine
      `docs/research/slop_revision/round_02/researcher-plan_report.md`
      and `docs/review/round_*/auditor_change_plan.md`.
- [ ] Stream 2 (auto-extracted diffs): paragraph-level pairs from
      `git diff essay_vN.md essay_v(N+1).md` for N=2..21, then
      LLM-judge filter (keep only edits that actually reduce AI slop).
- [ ] Stream 3 (negative examples): mine `.claude/worktrees/`
      branches for proposed-but-rejected edits.
- [ ] Stream 4 (banned-pattern catalog): union
      `HumanEmbedding/docs/research/ai_writing_tells.md` with
      `~/.copilot/skills/stop-slop/references/phrases.md`.
- [ ] Merge + dedupe + assign 60/20/20 splits, write to
      `data/stop_slop_split/{train,val,test}/items.json` and
      `data/stop_slop_split/banned_patterns.json`.
- [ ] Hand-back report to user: per-stream item count, sample 5
      items, ask for sign-off before Phase 1 begins.

### Phase 1 — Backend (`COPILOT-1`)
_Pending Phase 0.5 sign-off._

Default model for `copilot_cli_exec`: `claude-opus-4.7-1m-internal`
(per user decision; documented in `dev_docs/decisions.md` as a
fork-only default that must NOT be propagated upstream).
Optimizer-side support: deferred to `COPILOT-2`.
Outputs layout: per-skill subdir (`COPILOT-9` lands alongside).

### Phase 2 — First env (`COPILOT-3` stop_slop)
_Pending Phase 1._

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
