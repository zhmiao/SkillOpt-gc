# Stream 4 banned-pattern catalog report

Generated at: 2026-05-31T18:37:48+00:00

## Counts

- Total pattern count: 47
- Counts by source: ai_writing_tells_only=16, stop_slop_only=23, both=8
- Counts by matcher type: regex=43, llm_judge=4
- Counts by severity: high=13, medium=30, low=4

## Patterns not represented

None. Every source pattern family was represented either by a regex matcher or by an LLM-judge prompt; broad phrase categories were deduplicated into canonical families where the source grouped them together.

## Regex validation against assigned examples

All 43 regex matchers compiled under Python `re` and matched at least one assigned example string.

## Sample regex matches against `/home/miao/repos/HumanEmbedding/essay_v2.md`

- `em_dash_overuse` matched: — as patient and enthusiastic as they can be —
- `not_x_but_y_reveal` matched: not because it understands either field perfectly, but because it has compressed the reasoning patterns of both fields into the same geometric structure
- `word_choice_meta_commentary` matched: I use "logic" here deliberately

STATUS: DONE n_patterns=47
