# Stream 1 hand-labeled extraction report

## Total item count

- Total items: **83**
- Stream: `hand_labeled`
- All items use `label_quality: "high"` and `is_negative: false`.

## Per-source-file breakdown

| Source file | Items |
|---|---:|
| `docs/research/slop_revision/round_01/researcher-audit_report.md` | 5 |
| `docs/research/slop_revision/round_01/researcher-humans_report.md` | 3 |
| `docs/research/slop_revision/round_02/researcher-plan_report.md` | 30 |
| `docs/research/slop_revision/round_02/researcher-structural_report.md` | 1 |
| `docs/review/round_01/auditor_change_plan.md` | 21 |
| `docs/review/round_01/auditor_report.md` | 7 |
| `docs/review/round_01/reviewer_report.md` | 6 |
| `docs/review/round_02/auditor_change_plan.md` | 10 |

## Pattern-frequency table

| pattern_id | Count |
|---|---:|
| `em_dash_overuse` | 13 |
| `ai_adverb_strip` | 5 |
| `asyndeton_adjective_triplet` | 5 |
| `balanced_cadence` | 5 |
| `even_sentence_rhythm` | 3 |
| `meta_commentary` | 3 |
| `skeleton_metaphor` | 3 |
| `ai_adverb` | 2 |
| `anaphoric_pair` | 2 |
| `awkward_preposition_stranding` | 2 |
| `cosmic_koan` | 2 |
| `dramatized_wording` | 2 |
| `duplicate_antithesis` | 2 |
| `genitive_abstraction` | 2 |
| `grand_ai_abstract` | 2 |
| `italicized_abstract_emphasis` | 2 |
| `not_x_it_is_y_inversion` | 2 |
| `q_and_a_pair` | 2 |
| `something_x_opener` | 2 |
| `stripped_causal_connective` | 2 |
| `abrupt_section_join` | 1 |
| `aim_framing` | 1 |
| `anaphoric_sweep` | 1 |
| `anaphoric_triplet` | 1 |
| `anaphoric_x_beneath_y_triplet` | 1 |
| `and_yet_pivot` | 1 |
| `aphoristic_kicker` | 1 |
| `balanced_antinomy` | 1 |
| `broken_parallel_verb_structure` | 1 |
| `cleft_construction` | 1 |
| `cross_paragraph_antecedent` | 1 |
| `do_too_tag` | 1 |
| `doubled_abstraction` | 1 |
| `every_x_anaphora` | 1 |
| `exotic_breadth_triplet` | 1 |
| `four_fold_parallel_anaphora` | 1 |
| `geographic_triplet` | 1 |
| `geometric_grand_abstraction` | 1 |
| `geometry_metaphor_cluster` | 1 |
| `grand_concept` | 1 |
| `hedge_word` | 1 |
| `hedged_declarative` | 1 |
| `indirect_speech_tense_mismatch` | 1 |
| `its_not_this_its_that` | 1 |
| `label_collision` | 1 |
| `lazy_extreme` | 1 |
| `loose_technical_plural` | 1 |
| `mechanical_contrast` | 1 |
| `mechanical_parallel_openers` | 1 |
| `metaphor_cluster` | 1 |
| `metaphor_pileup` | 1 |
| `mid_sentence_inversion` | 1 |
| `not_because_x_but_because_y` | 1 |
| `not_just_additive_hedge` | 1 |
| `not_only_x_but_y` | 1 |
| `not_x_but_y_inversion` | 1 |
| `not_x_but_y_reflex` | 1 |
| `not_x_not_y_but_z` | 1 |
| `paired_anaphora` | 1 |
| `paired_item_triplet` | 1 |
| `parallel_quintet` | 1 |
| `parallel_triplet` | 1 |
| `purified_crystallized_doublet` | 1 |
| `q_and_a_sequence` | 1 |
| `q_and_a_staircase` | 1 |
| `redundant_aphoristic_kicker` | 1 |
| `redundant_grand_claim` | 1 |
| `sentence_completion` | 1 |
| `shape_of_abstraction` | 1 |
| `staccato_fragmentation` | 1 |
| `staircase` | 1 |
| `staircase_anaphora` | 1 |
| `stripped_causal_connectives` | 1 |
| `telling_not_showing` | 1 |
| `textbook_spectrum` | 1 |
| `there_is_opener` | 1 |
| `there_may_be_opener` | 1 |
| `throat_clearing` | 1 |
| `tricolon` | 1 |
| `triplet` | 1 |
| `twin_balance_kicker` | 1 |
| `two_word_kicker` | 1 |
| `unclear_antecedent` | 1 |
| `x_not_y_antithesis` | 1 |

## Sample items

### Sample 1: `stream1_slop_revision_r02_tier2_line7`

```json
{
  "id": "stream1_slop_revision_r02_tier2_line7",
  "prose_in": "Biologists and engineers, ecologists and data scientists, theorists and practitioners — as patient and enthusiastic as they can be — and yet the words they carry across the table keep arriving wrong, keep meaning something else on the other side.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "paired_item_triplet",
      "evidence": "Checks: dropped the three paired-item triplet to a single pair + modifier clause."
    },
    {
      "pattern_id": "em_dash_overuse",
      "evidence": "Before contains two em-dash interruptions."
    },
    {
      "pattern_id": "and_yet_pivot",
      "evidence": "Before uses \"and yet\" rhetorical pivot."
    }
  ],
  "gold_rewrite": "Biologists and engineers, patient with each other and fluent in each other's papers, and the words still keep arriving wrong on the far side of the table.",
  "regression_check": "No different AI shape; preserves structural mistranslation claim; more specific pair grounded in author work.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/research/slop_revision/round_02/researcher-plan_report.md:53-57",
    "round": "slop_revision_round_02"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### Sample 2: `stream1_slop_revision_r02_tier1_l88_delete`

```json
{
  "id": "stream1_slop_revision_r02_tier1_l88_delete",
  "prose_in": "I use 'logic' here deliberately, and I mean it broadly.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "meta_commentary",
      "evidence": "Reason: Pure meta-commentary; redundant with line 70 definition paragraph."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Delete; content loss ≈ 0 per Tier 1. No replacement.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/research/slop_revision/round_02/researcher-plan_report.md:36-39",
    "round": "slop_revision_round_02"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### Sample 3: `stream1_slop_revision_r01_audit_line90_fix`

```json
{
  "id": "stream1_slop_revision_r01_audit_line90_fix",
  "prose_in": "What the training process does is not memorization — it is compression.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "not_x_it_is_y_inversion",
      "evidence": "Audit tag: NV."
    },
    {
      "pattern_id": "balanced_cadence",
      "evidence": "Audit tag: BAL."
    },
    {
      "pattern_id": "em_dash_overuse",
      "evidence": "Audit tag: EM."
    }
  ],
  "gold_rewrite": "Training isn't memorization; it's compression.",
  "regression_check": "Fix removes em-dash inversion using flatter declarative contrast.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/research/slop_revision/round_01/researcher-audit_report.md:47-50",
    "round": "slop_revision_round_01"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### Sample 4: `stream1_review_r01_reviewer_l21_doubled_it`

```json
{
  "id": "stream1_review_r01_reviewer_l21_doubled_it",
  "prose_in": "a human mind can hold only so much, and it can hold it only through natural language.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "unclear_antecedent",
      "evidence": "Bug type: first \"it\" = mind, second \"it\" = so much."
    }
  ],
  "gold_rewrite": "a human mind can hold only so much, and only through natural language.",
  "regression_check": "Applied verb-elision removes doubled pronoun while preserving capacity + medium constraints.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/review/round_01/reviewer_report.md:67-73",
    "round": "round_01"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### Sample 5: `stream1_review_r02_change_plan_i_l104_staccato`

```json
{
  "id": "stream1_review_r02_change_plan_i_l104_staccato",
  "prose_in": "LLMs do not produce truth. They are not intelligent. They extract the structure of how we collectively think. The result is imperfect, but the closest shared logical foundation we have.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "even_sentence_rhythm",
      "evidence": "Pattern: criterion #19 even rhythm."
    },
    {
      "pattern_id": "staccato_fragmentation",
      "evidence": "Pattern: structures.md staccato fragmentation."
    }
  ],
  "gold_rewrite": "LLMs do not produce truth, and they are not intelligent. What they extract is the structure of how we collectively think: imperfect, but the closest shared logical foundation we have.",
  "regression_check": "Uses revised after: no em-dash; combines parallel sentences and trailing fragment.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/review/round_02/auditor_change_plan.md:123-139",
    "round": "round_02"
  },
  "label_quality": "high",
  "is_negative": false
}
```

## Sources skipped or mined for zero items

| Source file | Why |
|---|---|
| `docs/research/slop_revision/round_01/researcher-tells_report.md` | Read. Taxonomy/report prose did not contain concrete source-backed before/after rewrite pairs suitable for gold items. |
| `docs/review/round_01/inquisitor_review.md` | Read. Used as adjudication context only; no additional final gold before/after pairs beyond round_01 change-plan and applied-report items. |
| `docs/review/round_02/auditor_report.md` | Read. Contains stale-audit status and critique, not new explicit before/after rewrite pairs with gold after text. |
| `docs/review/round_02/inquisitor_review.md` | Read. Adjudicates the stale round_02 plan; no additional gold pairs beyond the explicit round_02 change-plan entries mined. |
| `docs/review/round_02/reviewer_report.md` | Read. Reports convergence / no reviewer-side changes; no before/after pair to mine. |
| `docs/review/round_03/auditor_change_plan.md` | Read. File explicitly says NO PROPOSALS, zero edits. |
| `docs/review/round_03/auditor_report.md` | Read. Zero findings; no before/after pair. |
| `docs/review/round_03/inquisitor_review.md` | Read. Convergence adjudication only; no before/after pair. |
| `docs/review/round_03/reviewer_report.md` | Read. Zero findings; no before/after pair. |
| `docs/review/round_04/auditor_change_plan.md` | Missing in source tree at extraction time. |
| `docs/review/round_04/auditor_report.md` | Read. Discusses line 88 follow-up but does not provide a complete original BEFORE block; skipped rather than reconstruct. |
| `docs/review/round_04/inquisitor_review.md` | Read. Gives a truncated original quote and current text for line 88; skipped because BEFORE was incomplete. |
| `docs/review/round_04/reviewer_report.md` | Read. Reviewer remained converged; no gold before/after pair. |

## Pattern IDs assigned

- `abrupt_section_join`
- `ai_adverb`
- `ai_adverb_strip`
- `aim_framing`
- `anaphoric_pair`
- `anaphoric_sweep`
- `anaphoric_triplet`
- `anaphoric_x_beneath_y_triplet`
- `and_yet_pivot`
- `aphoristic_kicker`
- `asyndeton_adjective_triplet`
- `awkward_preposition_stranding`
- `balanced_antinomy`
- `balanced_cadence`
- `broken_parallel_verb_structure`
- `cleft_construction`
- `cosmic_koan`
- `cross_paragraph_antecedent`
- `do_too_tag`
- `doubled_abstraction`
- `dramatized_wording`
- `duplicate_antithesis`
- `em_dash_overuse`
- `even_sentence_rhythm`
- `every_x_anaphora`
- `exotic_breadth_triplet`
- `four_fold_parallel_anaphora`
- `genitive_abstraction`
- `geographic_triplet`
- `geometric_grand_abstraction`
- `geometry_metaphor_cluster`
- `grand_ai_abstract`
- `grand_concept`
- `hedge_word`
- `hedged_declarative`
- `indirect_speech_tense_mismatch`
- `italicized_abstract_emphasis`
- `its_not_this_its_that`
- `label_collision`
- `lazy_extreme`
- `loose_technical_plural`
- `mechanical_contrast`
- `mechanical_parallel_openers`
- `meta_commentary`
- `metaphor_cluster`
- `metaphor_pileup`
- `mid_sentence_inversion`
- `not_because_x_but_because_y`
- `not_just_additive_hedge`
- `not_only_x_but_y`
- `not_x_but_y_inversion`
- `not_x_but_y_reflex`
- `not_x_it_is_y_inversion`
- `not_x_not_y_but_z`
- `paired_anaphora`
- `paired_item_triplet`
- `parallel_quintet`
- `parallel_triplet`
- `purified_crystallized_doublet`
- `q_and_a_pair`
- `q_and_a_sequence`
- `q_and_a_staircase`
- `redundant_aphoristic_kicker`
- `redundant_grand_claim`
- `sentence_completion`
- `shape_of_abstraction`
- `skeleton_metaphor`
- `something_x_opener`
- `staccato_fragmentation`
- `staircase`
- `staircase_anaphora`
- `stripped_causal_connective`
- `stripped_causal_connectives`
- `telling_not_showing`
- `textbook_spectrum`
- `there_is_opener`
- `there_may_be_opener`
- `throat_clearing`
- `tricolon`
- `triplet`
- `twin_balance_kicker`
- `two_word_kicker`
- `unclear_antecedent`
- `x_not_y_antithesis`

## Extraction notes

- Pure deletion entries use `gold_rewrite: ""`.
- Optional/explicit KEEP entries in change plans were skipped when the source did not present them as a rewrite target.
- Entries with incomplete or unclear BEFORE text were skipped rather than reconstructed.
