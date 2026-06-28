# Stream 2 report — auto-diff paragraph mining

## Summary

- Total raw paragraph-level candidate pairs from diffs: **659**.
- Pairs surviving judge filter: **147**.
- Dropped by judge/filter: **512**.
- Label quality for all kept items: `medium`.
- Negative items emitted: `0`.

## Version range

- Existing files: `essay_v2.md`, `essay_v3.md`, `essay_v4.md`, `essay_v5.md`, `essay_v6.md`, `essay_v7.md`, `essay_v8.md`, `essay_v9.md`, `essay_v10.md`, `essay_v11.md`, `essay_v12.md`, `essay_v13.md`, `essay_v14.md`, `essay_v15.md`, `essay_v16.md`, `essay_v17.md`, `essay_v18.md`, `essay_v19.md`, `essay_v20.md`, `essay_v22.md`.
- Skipped version pairs:
  - `v20->v21` because missing essay_v21.md.
  - `v21->v22` because missing essay_v21.md.

## Per-version-pair breakdown

| Version pair | Git no-index hunks | Raw paragraph candidates | Judge-kept items |
|---|---:|---:|---:|
| `v2->v3` | 53 | 49 | 42 |
| `v3->v4` | 44 | 49 | 3 |
| `v4->v5` | 22 | 20 | 4 |
| `v5->v6` | 4 | 2 | 1 |
| `v6->v7` | 7 | 6 | 1 |
| `v7->v8` | 7 | 6 | 0 |
| `v8->v9` | 16 | 14 | 1 |
| `v9->v10` | 55 | 41 | 3 |
| `v10->v11` | 48 | 51 | 5 |
| `v11->v12` | 56 | 56 | 9 |
| `v12->v13` | 54 | 57 | 9 |
| `v13->v14` | 53 | 53 | 19 |
| `v14->v15` | 45 | 45 | 17 |
| `v15->v16` | 59 | 58 | 17 |
| `v16->v17` | 58 | 59 | 7 |
| `v17->v18` | 17 | 18 | 1 |
| `v18->v19` | 25 | 28 | 3 |
| `v19->v20` | 47 | 47 | 5 |

Most productive diffs by kept count: `v2->v3` (42), `v13->v14` (19), `v14->v15` (17), `v15->v16` (17), `v11->v12` (9).

## Pattern-frequency table

| Pattern ID | Count |
|---|---:|
| `em_dash_overuse` | 92 |
| `adverbs` | 41 |
| `pseudo_profound_fragments` | 11 |
| `not_x_but_y` | 11 |
| `hedge_stack` | 10 |
| `meta_commentary_on_word_choice` | 8 |
| `perfect_rhythm_unvaried_sentence_length` | 7 |
| `rule_of_three` | 6 |
| `not_a_not_b_not_c_but_d` | 6 |
| `importance_inflation` | 4 |
| `something_older_something_closer` | 3 |
| `overused_transitions` | 2 |
| `throat_clearing_openers` | 2 |
| `unearned_spiritual_register` | 1 |
| `geographic_diversity_stuffing` | 1 |
| `meta_commentary` | 1 |

## Sample kept items

### stream2_v2_to_v3_1

- Source: `essay_v2.md → essay_v3.md`
- Patterns: `em_dash_overuse`
- Judge reason: Kept: judge found named slop-pattern reduction and regression guard passed.
- Before: I have spent years in rooms where people who love each other's work cannot speak to each other. Biologists and engineers, ecologists and data scientists, theorists and practitioners — as patient and enthusiastic as they can be — and yet the words they carry a…
- After: I have spent years in rooms where people who love each other's work cannot speak to one another. Biologists and engineers sit across the table, read each other's papers in good faith, and walk away meaning different things by the same words.

### stream2_v3_to_v4_2

- Source: `essay_v3.md → essay_v4.md`
- Patterns: `importance_inflation`
- Judge reason: Kept: judge found named slop-pattern reduction and regression guard passed.
- Before: I have come to suspect there is a structure underneath, older than any vocabulary. It is the shape of how we reason before the words we reason in. This is the foundational layer of our shared thought, and for most of human history we could not see it. We have…
- After: The argument I want to make is narrow. Large language models, trained on a wide cross-section of human text, have absorbed enough of how people in different communities reason that they can render an argument from one community as a structured artifact — a fl…

### stream2_v4_to_v5_3

- Source: `essay_v4.md → essay_v5.md`
- Patterns: `adverbs`
- Judge reason: Kept: judge found named slop-pattern reduction and regression guard passed.
- Before: Explaining this to engineers was its own job. They would suggest fixes — focal loss, oversampling, augmentation — that addressed parts of the problem but missed the part where the ecologist's frame of reference is itself the reasoning. Explaining the same thi…
- After: Explaining this to engineers was its own job. They would suggest fixes — focal loss, oversampling, augmentation — that addressed parts of the problem but missed the part where the ecologist's frame of reference *is* the reasoning. Explaining it back to ecolog…

### stream2_v5_to_v6_2

- Source: `essay_v5.md → essay_v6.md`
- Patterns: `em_dash_overuse`
- Judge reason: Kept: judge found named slop-pattern reduction and regression guard passed.
- Before: The shared premise is the top node. The divergent paths are visible without interpretation. A reader from either community can point at a node and say *I disagree with that one*, or *we don't actually disagree about that — only about what comes after.*
- After: The shared premise is the top node; the two paths run in parallel below it, each with the same three steps: premise, action, terminal goal. A reader from either community can now point at a specific node and say *I disagree with that step*, or *we actually ag…

### stream2_v6_to_v7_5

- Source: `essay_v6.md → essay_v7.md`
- Patterns: `adverbs`
- Judge reason: Kept: judge found named slop-pattern reduction and regression guard passed.
- Before: Some of it goes badly. I once asked a model to diagram an active-learning pipeline I was building. What I had in mind branched: model predictions go through human verification before feeding back into fine-tuning, *and* a fraction of high-confidence predictio…
- After: I once asked a model to diagram an active-learning pipeline I was building. What I had in mind branched: model predictions go through human verification before feeding back into fine-tuning, *and* a fraction of high-confidence predictions skip verification an…

## Sample dropped items

### v2_to_v3 hunk 10

- Source: `essay_v2.md → essay_v3.md`
- Judge reason for dropping: Dropped: no specific named pattern reduced under the conservative judge.
- Before: And the bridge breaks. The English comment is opaque to a reader who does not speak English. The logic transferred perfectly across every human language on Earth. The natural-language wrapper did not.
- After: The bridge fails. A reader without English can still read the logic. They cannot read the English wrapped around it.

### v2_to_v3 hunk 13

- Source: `essay_v2.md → essay_v3.md`
- Judge reason for dropping: Dropped: rewrite introduces or retains a high-salience catalogued tell.
- Before: This insight is not new in its aspiration. Leibniz dreamed of a *characteristica universalis* — a universal symbolic language in which all human disagreements could be resolved by calculation. "Let us calculate!" he wrote, imagining a future where disputes wo…
- After: This idea is not new. Leibniz dreamed of a *characteristica universalis*, a universal symbolic language that would settle disagreements by calculation. "Let us calculate!" he wrote. The Vienna Circle, two centuries later, tried to build a unified language for…

### v9_to_v10 hunk 3

- Source: `essay_v9.md → essay_v10.md`
- Judge reason for dropping: Dropped: low semantic relation and only weak surface-pattern reduction.
- Before: The argument I want to make is: large language models, trained on a wide cross-section of human text, have absorbed enough of how people in different communities reason that they can render an argument from one community as a structured artifact — a flow char…
- After: Large language models matter, in this argument, because they may be the first tools that compress enough ordinary human expression to expose some of that underlying structure without asking everyone to learn a new formal language. If that is true, they could …

## Notes

- No files under `/home/miao/repos/HumanEmbedding` were modified.
- No files under `SkillOpt-gc/data/stop_slop_split/` were touched.
- The final yield is slightly below the planned 150–300 range because the judge dropped structural rewrites and candidates without a named pattern reduction.

STATUS: DONE
