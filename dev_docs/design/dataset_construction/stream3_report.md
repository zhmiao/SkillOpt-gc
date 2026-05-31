# Stream 3 Report — Worktree-mined negative items

## Worktree uniqueness check

- Checked `.claude/worktrees/auditor-*` and `.claude/worktrees/reviewer-*` scoped review files with md5/hash comparisons before content mining.
- First required inspection: `.claude/worktrees/auditor-3605661-4804/docs/review/round_02/auditor_change_plan.md` matched `docs/review/round_02/auditor_change_plan.md` exactly by md5 (`2f5be9e352e7fc95142a9e39bc80da20`).
- Full scoped comparison outcome: 63 worktree review files checked; 32 identical to current-branch counterparts, 31 different/stale snapshots.
- `git branch -a | grep worktree-` listed 12 worktree branches. Branch tips had no scoped diffs versus current branch for `essay_v3.md`, `auditor_change_plan.md`, or `reviewer_report.md`; divergent useful signal was in stale worktree docs plus explicit main-tree rejection notes.

## Item counts by source

| Source | Count | Notes |
|---|---:|---|
| Round 1 auditor proposed rewrites rejected by inquisitor | 17 | Proposed text from worktree auditor plan; rejection rationale from `docs/review/round_01/inquisitor_review.md`. |
| Round 2 self-revised / Round 3 regression notes | 3 | Two self-rejected em-dash rewrites; one apposition regression later fixed. |
| Slop-revision fallback sources | 10 | Round 0 audit rewrites later flagged by slop-revision reports, plus explicit fabricated-specificity pitfall. |
| **Total** | **30** | All `is_negative: true`. |

## Five sample negative items

```json
{
  "id": "stream3_r1_auditor_rejected_001",
  "prose_in": "Both are right inside their own frame, and the distance between them feels unbridgeable. They have the words, but the words cannot carry the full weight of what they mean.",
  "context_before": "Both are right inside their own frame. The distance between them feels unbridgeable. They have the words. But the words cannot carry the full weight of what they mean.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "over_smoothing_nonpivot_connective",
      "evidence": "Adds “and” between sequential statements; inquisitor says connective is at a non-pivot and current period-then-But carries weight."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Rejected in docs/review/round_01/inquisitor_review.md: adds a connective at a non-pivot; rhythm is good prose, not AI tell.",
  "source": {
    "stream": "worktree_mined",
    "path": ".claude/worktrees/auditor-3631709-25083/docs/review/round_01/auditor_change_plan.md",
    "round": "round_01"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

```json
{
  "id": "stream3_r1_auditor_rejected_002",
  "prose_in": "It shapes what can be said, and bends what is meant. It fractures meaning for each community that uses it. Wittgenstein put it directly: meaning is not a label we stick on an object — meaning is use, and use varies across communities and disciplines.",
  "context_before": "It shapes what can be said and bends what is meant. It fractures meaning for each community that uses it. Wittgenstein saw this. Meaning is not a label we stick on an object. Meaning is use. Use varies across communities and disciplines.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "em_dash_smoothing",
      "evidence": "Reintroduces an em-dash while smoothing deliberate philosophical staccato."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Rejected in docs/review/round_01/inquisitor_review.md: touches deliberate Wittgenstein staccato and reintroduces an em-dash.",
  "source": {
    "stream": "worktree_mined",
    "path": ".claude/worktrees/auditor-3631709-25083/docs/review/round_01/auditor_change_plan.md",
    "round": "round_01"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

```json
{
  "id": "stream3_r2_self_revised_019",
  "prose_in": "The logic does not resolve the conflict, but makes it legible — the bare architecture of disagreement.",
  "context_before": "The logic does not resolve the conflict. It makes the conflict *legible*. It shows the bare architecture of disagreement.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "em_dash_bare_architecture",
      "evidence": "The plan self-corrected “Wait, em-dash again” and revised away from the dash version."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Round 2 auditor self-rejected the first AFTER because it introduced another em-dash and kept the abstract “bare architecture” reveal.",
  "source": {
    "stream": "worktree_mined",
    "path": "docs/review/round_02/auditor_change_plan.md",
    "round": "round_02"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

```json
{
  "id": "stream3_r2_regression_020",
  "prose_in": "Serious and casual writing side by side. The archive is closer to an amalgamation of collective human consciousness than to a dataset, the crude unprocessed form of human logic.",
  "context_before": "Serious and casual writing side by side. This is not just data. It is close to an amalgamation of collective human consciousness, and the crude unprocessed form of human logic.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "dangling_apposition_tone_shift",
      "evidence": "Round 3 auditor says the trailing apposition attaches to “dataset” by proximity, a parsing regression from the Round 2 fix."
    }
  ],
  "gold_rewrite": "Serious and casual writing side by side. The archive is the crude unprocessed form of human logic, closer to an amalgamation of collective human consciousness than to a dataset.",
  "regression_check": "Round 3 auditor explicitly labels this a regression from the Round 2 fix: the apposition attaches to the wrong noun.",
  "source": {
    "stream": "worktree_mined",
    "path": "docs/review/round_03/auditor_change_plan.md",
    "round": "round_03"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

```json
{
  "id": "stream3_slop_round0_flagged_021",
  "prose_in": "The distance between them feels unbridgeable, and not for lack of vocabulary — it's that their words can't transmit the lived weight behind each position.",
  "context_before": "And yet the distance between them feels unbridgeable — not because they lack the words to speak to each other, but because the words they have cannot carry the full weight of what they mean.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "em_dash_lived_weight_abstraction",
      "evidence": "Round 1 inquisitor says the line-25 rewrite still leans on em-dash + “lived weight”."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Flagged in slop_revision/round_01/inquisitor_review.md as a rewrite that swaps one AI pattern for another.",
  "source": {
    "stream": "worktree_mined",
    "path": "docs/review/ai_slop_audit.md",
    "round": "round_01"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

## Different-pattern regression taxonomy

- `anaphoric_sentence_split` (1)
- `balanced_semicolon_aphorism` (1)
- `dangling_apposition_tone_shift` (1)
- `double_em_dash_insert` (1)
- `em_dash_abstract_foundation` (1)
- `em_dash_bare_architecture` (1)
- `em_dash_exotic_geography_pair` (1)
- `em_dash_fragment_collapse` (1)
- `em_dash_lived_weight_abstraction` (1)
- `em_dash_metaphor_stack` (1)
- `em_dash_not_what_contrast` (1)
- `em_dash_not_x_but_y` (1)
- `em_dash_smoothing` (1)
- `em_dash_smoothing_staccato` (1)
- `em_dash_substitution` (2)
- `fabricated_specificity` (1)
- `generic_flattening_metaphor_erasure` (1)
- `generic_technical_metaphor_erasure` (1)
- `generic_universal_readability` (1)
- `meta_commentary_i_mean` (1)
- `metaphor_ghost_skeleton` (1)
- `mild_hedge_plus_parallel_cascade` (1)
- `nonpivot_and_smoothing` (1)
- `over_smoothing_nonpivot_connective` (1)
- `pressure_in_motion_pseudo_profundity` (1)
- `rule_of_three_tricolon` (1)
- `staccato_smoothing` (1)
- `staccato_smoothing_register_shift` (1)
- `vague_abstraction` (1)

## Files written

- `dev_docs/design/dataset_construction/stream3_items.json`
- `dev_docs/design/dataset_construction/stream3_worktree_mined.md`
- `dev_docs/design/dataset_construction/stream3_report.md`

STATUS: DONE
