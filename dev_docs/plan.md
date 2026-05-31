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
- [ ] User signs off on dataset before Phase 1 begins.

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
