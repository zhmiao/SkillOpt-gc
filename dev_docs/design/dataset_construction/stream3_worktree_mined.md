# Stream 3 worktree-mined negative items
## Extraction notes
- Read `dev_docs/design/dataset_construction_plan.md` before extraction.
- Created initial draft files before mining.
- Ran quick hash comparisons before reading worktree content in depth. First sampled auditor plan matched main by md5; full pass found 32 identical scoped worktree files and 31 different/stale scoped files.
- Worktree branch tips showed no scoped diff versus the current HumanEmbedding branch for `essay_v3.md` or review-plan/report files; useful negatives came from explicit rejection/regression notes, not from branch-only merged diffs.
- Extracted 30 medium-quality negative items. All have `is_negative: true`; no positives included.

## Source counts
- `.claude/worktrees/auditor-3631709-25083/docs/review/round_01/auditor_change_plan.md`: 17
- `docs/research/slop_revision/round_01/researcher-audit_report.md`: 1
- `docs/research/slop_revision/round_02/inquisitor_review.md`: 1
- `docs/review/ai_slop_audit.md`: 8
- `docs/review/round_02/auditor_change_plan.md`: 2
- `docs/review/round_03/auditor_change_plan.md`: 1

## Pattern taxonomy introduced by rejected fixes
- `anaphoric_sentence_split`: 1
- `balanced_semicolon_aphorism`: 1
- `dangling_apposition_tone_shift`: 1
- `double_em_dash_insert`: 1
- `em_dash_abstract_foundation`: 1
- `em_dash_bare_architecture`: 1
- `em_dash_exotic_geography_pair`: 1
- `em_dash_fragment_collapse`: 1
- `em_dash_lived_weight_abstraction`: 1
- `em_dash_metaphor_stack`: 1
- `em_dash_not_what_contrast`: 1
- `em_dash_not_x_but_y`: 1
- `em_dash_smoothing`: 1
- `em_dash_smoothing_staccato`: 1
- `em_dash_substitution`: 2
- `fabricated_specificity`: 1
- `generic_flattening_metaphor_erasure`: 1
- `generic_technical_metaphor_erasure`: 1
- `generic_universal_readability`: 1
- `meta_commentary_i_mean`: 1
- `metaphor_ghost_skeleton`: 1
- `mild_hedge_plus_parallel_cascade`: 1
- `nonpivot_and_smoothing`: 1
- `over_smoothing_nonpivot_connective`: 1
- `pressure_in_motion_pseudo_profundity`: 1
- `rule_of_three_tricolon`: 1
- `staccato_smoothing`: 1
- `staccato_smoothing_register_shift`: 1
- `vague_abstraction`: 1
