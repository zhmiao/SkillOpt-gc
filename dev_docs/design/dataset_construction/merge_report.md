# `stop_slop` Dataset Merge Report

_Generated 2026-05-31T18:44:54.225920+00:00_

## Per-stream input counts

- Stream 1 (hand_labeled, high quality): 83
- Stream 2 (auto_diff, medium quality):  147
- Stream 3 (worktree_mined, negatives):  30
- **Total raw**: 260

## Canonical pattern catalog

- Stream 4 original: 47
- New canonical (added by merge for unmapped variants): 10
- **Final canonical count**: 57

### New canonical patterns added
- `anaphora_repetition` — Anaphoric repetition (llm_judge, severity=high)
- `metaphor_overuse` — Metaphor cluster / pileup (llm_judge, severity=high)
- `q_and_a_pair` — Q&A pair (chat-trained tell) (regex, severity=high)
- `staccato_fragmentation` — Staccato fragmentation (llm_judge, severity=medium)
- `throat_clearing_openers` — Throat-clearing opener (regex, severity=medium)
- `balanced_cadence_aphorism` — Balanced cadence / aphoristic kicker (llm_judge, severity=medium)
- `unclear_antecedent` — Unclear pronoun antecedent (llm_judge, severity=medium)
- `fabricated_specificity` — Fabricated specificity (llm_judge, severity=high)
- `stripped_causal_connective` — Stripped causal connective (llm_judge, severity=low)
- `vague_grand_abstraction` — Vague grand abstraction (regex, severity=medium)

## Remap pipeline

- Items after remap: 258
- Items dropped (no remappable pattern): 2
- Duplicates dropped: 6
- **Final unique items**: 252

## Quality distribution (final)

| Quality | Positive | Negative |
|---|---:|---:|
| high | 77 | 0 |
| medium | 145 | 30 |

## Split sizes

- train: 151
- val:   50
- test:  51

## Pattern frequency in final dataset

| pattern_id | count |
|---|---:|
| `em_dash_overuse` | 114 |
| `adverb_softener_intensifier` | 48 |
| `not_x_but_y_reveal` | 21 |
| `rule_of_three` | 19 |
| `word_choice_meta_commentary` | 13 |
| `pseudo_profound_fragments` | 13 |
| `hedge_stack` | 13 |
| `unvaried_sentence_rhythm` | 13 |
| `throat_clearing_openers` | 12 |
| `vague_grand_abstraction` | 11 |
| `anaphora_repetition` | 10 |
| `balanced_cadence_aphorism` | 9 |
| `metaphor_overuse` | 8 |
| `negative_listing_reveal` | 8 |
| `importance_inflation` | 7 |
| `overused_transitions` | 5 |
| `unclear_antecedent` | 5 |
| `q_and_a_pair` | 4 |
| `unearned_spiritual_register` | 4 |
| `stripped_causal_connective` | 4 |
| `staccato_fragmentation` | 3 |
| `geographic_diversity_stuffing` | 1 |
| `fabricated_specificity` | 1 |

## Sample items (verbatim)

### high positive
```json
{
  "id": "stream1_review_r01_change_plan_04_l88_grand_abstract",
  "prose_in": "The archive is the crude unprocessed form of human logic, closer to an amalgamation of collective human consciousness than to a dataset.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "vague_grand_abstraction",
      "evidence": "Rationale: \"amalgamation of collective human consciousness\" is residual grand-AI abstract."
    }
  ],
  "gold_rewrite": "The archive is the crude unprocessed form of human logic, closer to a record of how we collectively think than to a dataset.",
  "regression_check": "Replacement is plainer and parallel to nearby reasoning language.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/review/round_01/auditor_change_plan.md:29-32",
    "round": "round_01"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### medium positive
```json
{
  "id": "stream2_v2_to_v3_43",
  "prose_in": "I am not claiming that current reinforcement learning methods will produce Logos. Current methods optimize for human approval, not for truth; they improve sampling efficiency within the boundaries of what the base model already knows. These are real limitations of present technology. But I am not talking about present technology. I am talking about the principle — the observation that simple objectives, applied at sufficient scale through unconstrained iteration, produce emergent structure that transcends the simplicity of the objective. This is what evolution demonstrates. This is what the future development of reinforcement learning — or whatever approach succeeds it — might achieve.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "em_dash_overuse",
      "evidence": "Reduced em-dash cadence (3 → 0)."
    }
  ],
  "gold_rewrite": "I am not claiming current reinforcement learning methods will produce Logos. Current methods optimize for human approval, not truth. They improve sampling efficiency inside the boundaries of what the base model knows. These are real limits of present technology. I am pointing at the principle. Apply a simple objective at sufficient scale, with no constraint on the path, and the system develops structure that the objective alone could not predict. Evolution shows this. Future RL methods, or whatever replaces them, may show it too.",
  "regression_check": "Gold rewrite checked against catalogued high-salience tells; no different named tell introduced.",
  "source": {
    "stream": "auto_diff",
    "path": "essay_v2.md → essay_v3.md",
    "round": null
  },
  "label_quality": "medium",
  "is_negative": false
}
```

### negative
```json
{
  "id": "stream3_r1_auditor_rejected_014",
  "prose_in": "The principle behind reinforcement learning points past this limitation. I mean the principle, not the specific RL methods we have today.",
  "context_before": "The principle behind reinforcement learning, not the specific RL methods we have today, points past this limitation.",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "word_choice_meta_commentary",
      "evidence": "Adds explicit “I mean X, not Y” self-glossing."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Rejected in docs/review/round_01/inquisitor_review.md: adds meta-commentary, the exact AI tell the project had been editing out.",
  "source": {
    "stream": "worktree_mined",
    "path": ".claude/worktrees/auditor-3631709-25083/docs/review/round_01/auditor_change_plan.md",
    "round": "round_01"
  },
  "label_quality": "medium",
  "is_negative": true
}
```

### pure deletion
```json
{
  "id": "stream1_slop_revision_r01_humans_rewrite_pattern_1",
  "prose_in": "This essay explores the ways in which X shapes Y.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "throat_clearing_openers",
      "evidence": "Rewrite patterns table: delete meta-framing."
    }
  ],
  "gold_rewrite": "",
  "regression_check": "Cut the sentence. Start with the thing.",
  "source": {
    "stream": "hand_labeled",
    "path": "docs/research/slop_revision/round_01/researcher-humans_report.md:51-59",
    "round": "slop_revision_round_01"
  },
  "label_quality": "high",
  "is_negative": false
}
```

### test-split sample
```json
{
  "id": "stream2_v12_to_v13_22",
  "prose_in": "A model trained on that archive isn't given a theory of logic. It is given a token-prediction task. That sounds shallow until you ask what doing it well actually requires. To predict text across many domains, the model has to absorb recurring relations: questions and answers, premises and conclusions, definitions and objections. It absorbs these statistically rather than philosophically, and what gets learned is a pattern in how reasoning is expressed.",
  "context_before": "",
  "context_after": "",
  "banned_patterns": [
    {
      "pattern_id": "adverb_softener_intensifier",
      "evidence": "Reduced softeners/intensifiers/adverb filler (2 → 1); removed actually."
    }
  ],
  "gold_rewrite": "A model trained on that archive isn't given a theory of logic. Its task is to predict the next token, and the question worth asking is what it has to learn in order to do that across many domains. To predict text reliably, the model has to absorb recurring relations between bits of language: the way questions tend to be followed by answers and premises by conclusions, the way definitions get tested against objections, the way explanations get rebuilt when something fails to hold up. Those relations are picked up statistically rather than philosophically, and what ends up encoded is a pattern in how reasoning, when it shows up in text at all, tends to be expressed.",
  "regression_check": "Gold rewrite checked against catalogued high-salience tells; no different named tell introduced.",
  "source": {
    "stream": "auto_diff",
    "path": "essay_v12.md → essay_v13.md",
    "round": null
  },
  "label_quality": "medium",
  "is_negative": false
}
```
