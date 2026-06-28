# `stop_slop` Dataset Construction Plan

> **Status.** Active execution (parallel extraction in progress).
> **Started.** 2026-05-31.
> **Source corpus.** `/home/miao/repos/HumanEmbedding`.
> **Target.** `data/stop_slop_split/{train,val,test}/items.json` plus
> `data/stop_slop_split/banned_patterns.json`.
> **Parameters (per user).** `dataset_option=max`, both
> banned-pattern sources unioned, negatives included, 60/20/20 split.

## Why this approach

The user's `HumanEmbedding` repo is an 8-week revision history of a
single ~25KB essay through 20 versions (`essay_v2.md` …
`essay_v22.md`) with full Claude Code audit / review trails under
`docs/review/round_{01..04}/` and `docs/research/slow_revision/`.
This corpus has three properties that no synthetic dataset can
match:

1. **Human-judged labels.** Every accepted edit reflects the user's
   own taste, not a synthetic rubric.
2. **Named patterns.** `docs/research/slop_revision/round_02/researcher-plan_report.md`
   explicitly tags every entry with the AI-tell it removes and runs
   a regression check ("did this fix introduce a different AI
   pattern?").
3. **Negative examples.** `.claude/worktrees/` retains agent
   transcripts that include proposed edits that were *not* accepted
   — direct training signal for the gate to penalize
   different-pattern regressions.

## Dataset item schema

Each item under `data/stop_slop_split/{train,val,test}/items.json`:

```json
{
  "id": "<stable_slug>",
  "prose_in": "<original paragraph(s) — what the target rewrites>",
  "context_before": "<optional preceding paragraph for cohesion>",
  "context_after": "<optional following paragraph for cohesion>",
  "banned_patterns": [
    {"pattern_id": "<e.g. 'em_dash_overuse'>", "evidence": "<short excerpt>"}
  ],
  "gold_rewrite": "<the human-accepted rewrite, if available>",
  "regression_check": "<did the gold rewrite introduce a different AI tell? (notes from source)>",
  "source": {
    "stream": "hand_labeled | auto_diff | worktree_mined",
    "path": "<file:line within HumanEmbedding>",
    "round": "<round number if applicable>"
  },
  "label_quality": "high | medium | low",
  "is_negative": false
}
```

A **negative** item has `is_negative: true`. Its `prose_in` is a
*proposed* rewrite that the user rejected; `banned_patterns` is the
NEW pattern the rejected edit introduced. The grader should
penalize the target for producing the same rewrite.

`data/stop_slop_split/banned_patterns.json`:

```json
{
  "patterns": [
    {
      "id": "em_dash_overuse",
      "regex": "...",
      "description": "...",
      "source": "ai_writing_tells.md | stop_slop_phrases.md | both"
    }
  ]
}
```

## Extraction streams

Four parallel work streams. Streams 1, 2, 3 produce candidate
items; stream 4 builds the banned-pattern catalog they tag against.

### Stream 1 — Hand-labeled before/after (highest signal)

**Sources.**
- `HumanEmbedding/docs/research/slop_revision/round_02/researcher-plan_report.md`
  — Tier 1 (deletions), Tier 2 (sentence-level rewrites), Tier 3
  (systematic passes). Each entry has `Before:` / `After:` /
  `Checks:` blocks.
- `HumanEmbedding/docs/review/round_{01..04}/auditor_change_plan.md`
  — per-round change plans with explicit (before, after, rationale)
  entries.
- `HumanEmbedding/docs/review/round_{01..04}/reviewer_report.md` —
  reviewer comments with sometimes-paired before/after.

**Expected output.** ~40–80 high-quality positive items
(`label_quality: high`, `is_negative: false`). Some Tier 1 entries
are pure deletions, not rewrites — those become items with
`gold_rewrite: ""` (i.e. "the correct output removes this text
entirely").

**Owner.** Background agent `dataset-stream1`.

### Stream 2 — Auto-extracted paragraph diffs + LLM-judge filter

**Sources.**
- `git -C /home/miao/repos/HumanEmbedding diff essay_vN.md essay_v(N+1).md`
  for N in {2..21} (skipping any missing versions).

**Pipeline.**
1. For each consecutive version pair, run `git diff` and split into
   paragraph-level (before, after) pairs.
2. Drop pure-structural moves (paragraph reordering with no text
   change).
3. For each surviving pair, ask an LLM judge: "Is this edit
   primarily an AI-slop reduction? If yes, which pattern(s)?" The
   judge classifies against the unified banned-pattern catalog.
4. Keep only edits that the judge says reduce ≥1 banned pattern.
5. Mark `label_quality: medium`.

**Expected output.** ~150–300 medium-quality positive items.

**Owner.** Background agent `dataset-stream2`.

### Stream 3 — Worktree-mined negative examples

**Sources.**
- `HumanEmbedding/.claude/worktrees/auditor-*/docs/review/round_*/auditor_change_plan.md`
- `HumanEmbedding/.claude/worktrees/reviewer-*/docs/review/round_*/reviewer_report.md`
- Worktree branches under `git branch -a | grep worktree-`

**Pipeline.**
1. Diff each worktree's change plan against the corresponding
   `main`-merged plan. Edits that appear in the worktree but NOT in
   `main` are candidate negatives (the user reviewed and rejected
   them).
2. For each rejected edit, identify the pattern it would have
   introduced (LLM judge against banned-pattern catalog).
3. Emit as `is_negative: true` items: `prose_in` = the rejected
   rewrite, `banned_patterns` = the pattern it introduces.

**Expected output.** ~50–200 negative items. Quality varies
(`label_quality: low | medium`).

**Risk.** Many worktree dirs may just be redundant snapshots of
`main`. If so, fall back to mining `docs/review/round_*/inquisitor_review.md`
for explicit "this proposed fix was rejected because X" notes.

**Owner.** Background agent `dataset-stream3`.

### Stream 4 — Banned-pattern catalog union

**Sources.**
- `HumanEmbedding/docs/research/ai_writing_tells.md`
- `~/.copilot/skills/stop-slop/references/phrases.md`
- (read-only support) `~/.copilot/skills/stop-slop/references/structures.md`
  and `examples.md` for additional pattern signatures.

**Pipeline.**
1. Parse both sources into named patterns.
2. For each pattern, write a regex / matcher rule (or note
   "requires-llm-judge" for patterns that can't be regexed —
   anaphora, triplets, "wise-sage register", etc.).
3. Dedupe patterns that appear in both sources; record
   `source: "both"`.
4. Output `data/stop_slop_split/banned_patterns.json`.

**Expected output.** ~30–60 patterns, ~half regex-matchable, half
needs LLM judge.

**Owner.** Background agent `dataset-stream4`.

## Merge phase (lead-owned)

After all four agents complete:

1. Load all stream outputs.
2. Dedupe across streams by `prose_in` hash (Stream 1 high-quality
   wins ties).
3. Re-tag every item's `banned_patterns` against the merged Stream 4
   catalog (so all items use the canonical pattern IDs).
4. Assign train/val/test = 60/20/20 with a deterministic seed (42).
   Splits stratified by `is_negative` so val/test have negatives.
5. Write `data/stop_slop_split/{train,val,test}/items.json` +
   `banned_patterns.json` + `split_manifest.json` (per
   `skillopt/datasets/base.py` convention).
6. Smoke-validate: open the JSON, count items, sample 5 random
   items, check schema.

## Acceptance for handing back to user

- All four streams reported.
- Per-stream item count + label distribution table.
- Sample 5 items (different sources + 1 negative) shown verbatim.
- Total counts + split sizes.
- Any stream that failed clearly noted with the failure mode.

User then either signs off to proceed to `COPILOT-1` (backend), or
asks for adjustments.

## File layout

```
SkillOpt-gc/
├── data/                                      # gitignored by default
│   └── stop_slop_split/
│       ├── train/items.json
│       ├── val/items.json
│       ├── test/items.json
│       ├── banned_patterns.json
│       └── split_manifest.json
└── dev_docs/design/dataset_construction/      # tracked
    ├── stream1_hand_labeled.md                # extraction notes
    ├── stream2_auto_diff.md
    ├── stream3_worktree_mined.md
    ├── stream4_patterns.md
    └── merge_report.md                        # final hand-back report
```

## Decisions deferred to merge phase

- **Negative-item weighting.** Should negatives be ~10% or ~30% of
  the dataset? Decide based on actual yield from Stream 3.
- **Context inclusion.** Should `context_before` / `context_after`
  always be filled when available, or only when the rewrite depends
  on cohesion? Default: always fill when ≤200 chars each.
- **Banned-pattern regex authorship.** Some patterns in
  `ai_writing_tells.md` are described in prose. Stream 4 converts
  them to regex/LLM-rules; some may need user review before locking
  in the catalog.
