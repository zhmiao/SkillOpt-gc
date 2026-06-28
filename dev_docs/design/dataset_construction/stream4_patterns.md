# Stream 4 banned-pattern catalog notes

Generated at: 2026-05-31T18:37:48+00:00

## Sources read

- `/home/miao/repos/SkillOpt-gc/dev_docs/design/dataset_construction_plan.md` lines 1-229 (full plan).
- `/home/miao/repos/HumanEmbedding/docs/research/ai_writing_tells.md` lines 1-137 (primary source).
- `/home/miao/.copilot/skills/stop-slop/references/phrases.md` lines 1-129 (primary source).
- `/home/miao/.copilot/skills/stop-slop/references/structures.md` lines 1-135 (read-only support for descriptions/examples only).
- `/home/miao/.copilot/skills/stop-slop/references/examples.md` lines 1-59 (read-only support for descriptions/examples only).

## Canonical pattern traceability

| ID | Source | Matcher | Severity | Trace embedded in description |
|---|---|---|---|---|
| `em_dash_overuse` | ai_writing_tells | regex | medium | ai_writing_tells.md:11-15 flags frequency and multiple em dashes as the giveaway; structures.md:124-125 supports using commas or periods instead. |
| `not_x_but_y_reveal` | ai_writing_tells | regex | high | ai_writing_tells.md:17-21 calls it a top tell; structures.md:3-21 lists related binary contrasts. |
| `rule_of_three` | ai_writing_tells | regex | low | ai_writing_tells.md:23-27 flags corporate tricolons; structures.md:118-125 also warns against three-item lists. |
| `negative_listing_reveal` | ai_writing_tells | regex | high | ai_writing_tells.md:29-32 names the 'Not A. Not B. Not C. But D.' cadence; structures.md:23-32 calls this negative listing. |
| `ai_vocabulary_cluster` | ai_writing_tells | regex | high | ai_writing_tells.md:34-38 says three or more cluster members in one paragraph are the giveaway. |
| `importance_inflation` | both | regex | high | ai_writing_tells.md:40-43 lists testament, pivotal moment, indelible mark, and setting the stage; phrases.md:118-128 lists vague claims about implications, stakes, and consequences. |
| `geographic_diversity_stuffing` | ai_writing_tells | regex | medium | ai_writing_tells.md:45-49 cites Tokyo, Nairobi, and São Paulo syndrome. |
| `pseudo_profound_fragments` | ai_writing_tells | regex | medium | ai_writing_tells.md:51-54 gives 'And yet.' and 'What remains.'; structures.md:34-44 lists dramatic fragmentation. |
| `something_older_closer_formula` | ai_writing_tells | regex | high | ai_writing_tells.md:56-60 names the exact 'Something older than X, something closer to Y' construction. |
| `word_choice_meta_commentary` | ai_writing_tells | regex | medium | ai_writing_tells.md:62-66 gives 'I use X deliberately' and related self-glossing. |
| `heres_family_opener` | both | regex | high | ai_writing_tells.md:68-72 flags announcer phrases; phrases.md:7-23 lists here's-the-thing / here's-what / here's-why variants. |
| `truth_reality_opener` | both | regex | high | ai_writing_tells.md:68-72 lists truth-style announcers; phrases.md:12-16 and 83 list 'The uncomfortable truth is', 'The truth is', and 'The reality is'. |
| `clarity_honesty_opener` | stop_slop_phrases | regex | medium | phrases.md:15-18 lists 'Let me be clear', 'I'll say it again', and 'I'm going to be honest' under throat-clearing openers. |
| `it_turns_out_opener` | stop_slop_phrases | regex | medium | phrases.md:12-13 lists 'It turns out' as a throat-clearing opener. |
| `can_we_talk_about_opener` | stop_slop_phrases | regex | medium | phrases.md:19 lists 'Can we talk about' among throat-clearing openers. |
| `overused_transitions` | ai_writing_tells | regex | medium | ai_writing_tells.md:74-77 flags these as AI connective defaults. |
| `outline_like_conclusion` | ai_writing_tells | regex | high | ai_writing_tells.md:79-82 lists 'In summary', 'Overall', and 'In conclusion'. |
| `abstract_example_moral_sandwich` | ai_writing_tells | llm_judge | medium | ai_writing_tells.md:84-87 says the symmetry is too neat and examples are framed and closed. |
| `elegant_variation_epithets` | ai_writing_tells | llm_judge | medium | ai_writing_tells.md:89-93 gives Dickens → the novelist → the Victorian author → the celebrated writer. |
| `hedge_stack` | both | regex | medium | ai_writing_tells.md:95-99 names might/could/potentially/often/generally; phrases.md:53-56 also bans softeners and hedges. |
| `forced_sass_cadence` | both | regex | medium | ai_writing_tells.md:100-103 names this cadence; phrases.md:89-92 lists Hint, Plot twist, and Spoiler under meta-commentary. |
| `unearned_spiritual_register` | ai_writing_tells | regex | medium | ai_writing_tells.md:105-109 lists sacred, witness, reverence, soul, testimony. |
| `unvaried_sentence_rhythm` | ai_writing_tells | llm_judge | medium | ai_writing_tells.md:111-114 flags every sentence landing around 12-18 words. |
| `signposting_without_payoff` | both | regex | high | ai_writing_tells.md:116-119 names this; phrases.md:31-34 and 93-99 list related signposts. |
| `compound_density_cluster` | ai_writing_tells | llm_judge | high | ai_writing_tells.md:5 and 123-126 says four to six tells in one paragraph are the strongest signal. |
| `full_stop_period_emphasis` | stop_slop_phrases | regex | medium | phrases.md:25-33 lists 'Full stop.' and 'Period.' as removable emphasis crutches. |
| `let_that_sink_in` | stop_slop_phrases | regex | high | phrases.md:29-33 lists 'Let that sink in.' as an emphasis crutch. |
| `make_no_mistake` | stop_slop_phrases | regex | medium | phrases.md:29-34 lists 'Make no mistake' as an emphasis crutch. |
| `this_matters_because` | stop_slop_phrases | regex | medium | phrases.md:29-34 lists 'This matters because' and 'Here's why that matters' as emphasis crutches. |
| `business_jargon_navigate_landscape` | both | regex | medium | ai_writing_tells.md:34-38 includes navigate and landscape in the AI vocabulary cluster; phrases.md:35-52 lists Navigate and Landscape as business jargon. |
| `business_jargon_action_cliches` | stop_slop_phrases | regex | medium | phrases.md:35-52 lists unpack, lean into, game-changer, double down, deep dive, take a step back, moving forward, circle back, and on the same page. |
| `adverb_softener_intensifier` | stop_slop_phrases | regex | low | phrases.md:53-75 says kill adverbs and lists really, just, literally, genuinely, honestly, simply, actually, deeply, truly, fundamentally, inherently, inevitably, interestingly, importantly, and crucially. |
| `at_its_core_filler` | stop_slop_phrases | regex | medium | phrases.md:75-84 lists 'At its core' among filler phrases. |
| `worth_noting_filler` | stop_slop_phrases | regex | medium | phrases.md:75-84 lists 'It's worth noting' as filler. |
| `end_of_day_filler` | stop_slop_phrases | regex | medium | phrases.md:75-84 lists 'At the end of the day' as filler. |
| `when_it_comes_to_filler` | stop_slop_phrases | regex | medium | phrases.md:75-84 lists 'When it comes to' as filler. |
| `in_world_today_opener` | both | regex | high | ai_writing_tells.md:68-72 names 'In today's fast-paced digital landscape'; phrases.md:78 and 82 list 'In today's [X]' and 'In a world where'. |
| `self_referential_structure_meta` | stop_slop_phrases | regex | medium | phrases.md:85-100 lists 'The rest of this essay explains', 'Let me walk you through', 'In this section', 'As we'll see', and 'I want to explore'. |
| `feature_not_bug_cliche` | stop_slop_phrases | regex | medium | phrases.md:89-95 lists 'X is a feature, not a bug' under meta-commentary. |
| `dressed_up_as_cliche` | stop_slop_phrases | regex | medium | phrases.md:89-95 lists 'Dressed up as' under meta-commentary. |
| `performative_promise` | stop_slop_phrases | regex | medium | phrases.md:101-108 lists 'I promise' and 'They exist, I promise'. |
| `creeps_in_personification` | stop_slop_phrases | regex | low | phrases.md:101-106 lists 'creeps in' under performative emphasis. |
| `telling_difficulty_instead_of_showing` | stop_slop_phrases | regex | medium | phrases.md:109-117 lists 'This is genuinely hard', 'This is what leadership actually looks like', and 'This is what X actually looks like'. |
| `actually_matters_formula` | stop_slop_phrases | regex | medium | phrases.md:113-117 lists 'actually matters' under telling instead of showing. |
| `vague_declarative_importance` | stop_slop_phrases | regex | high | phrases.md:118-128 lists reasons are structural, implications are significant, deepest problem, stakes are high, and consequences are real. |
| `you_already_know_this_but` | stop_slop_phrases | regex | medium | phrases.md:89-93 lists 'You already know this, but' under meta-commentary. |
| `another_post_aside` | stop_slop_phrases | regex | low | phrases.md:89-94 lists 'But that's another post' under meta-commentary. |

## Regex validation

Validated 43 regex patterns with Python `re.search` against at least one assigned example string before writing the JSON.

- `em_dash_overuse` matched example: Theorists and practitioners — as patient as they can be — still talk past each other.
- `not_x_but_y_reveal` matched example: It's not about writing faster, it's about writing smarter.
- `rule_of_three` matched example: Clear, concise, compelling.
- `negative_listing_reveal` matched example: Not speed. Not scale. Not automation. But transformation.
- `ai_vocabulary_cluster` matched example: This pivotal shift underscores the intricate tapestry of the evolving landscape.
- `importance_inflation` matched example: Stands as a testament to the evolving landscape of innovation.
- `geographic_diversity_stuffing` matched example: From the boardrooms of Tokyo to the startups of Nairobi to the factories of São Paulo.
- `pseudo_profound_fragments` matched example: And yet. What remains is not the data, but something older.
- `something_older_closer_formula` matched example: Something older than language, something closer to breath.
- `word_choice_meta_commentary` matched example: I use the word 'witness' deliberately.
- `heres_family_opener` matched example: Here's the thing: building products is hard.
- `truth_reality_opener` matched example: The uncomfortable truth is that nobody wants to admit they're confused.
- `clarity_honesty_opener` matched example: Let me be clear: this has to change.
- `it_turns_out_opener` matched example: It turns out that most teams struggle with alignment.
- `can_we_talk_about_opener` matched example: Can we talk about why this keeps happening?
- `overused_transitions` matched example: Moreover, the findings suggest a broader trend.
- `outline_like_conclusion` matched example: In conclusion, we have seen that the system matters.
- `hedge_stack` matched example: This could potentially suggest that X might generally tend to happen.
- `forced_sass_cadence` matched example: Hot take: the result was predictable.
- `unearned_spiritual_register` matched example: This is not data. It is testimony. It is witness.
- `signposting_without_payoff` matched example: Here is the key takeaway: the system needs to improve.
- `full_stop_period_emphasis` matched example: This is the only path. Full stop.
- `let_that_sink_in` matched example: The team shipped nothing for a year. Let that sink in.
- `make_no_mistake` matched example: Make no mistake, this changes the market.
- `this_matters_because` matched example: This matters because your competition isn't waiting.
- `business_jargon_navigate_landscape` matched example: Navigate uncertainty across the evolving landscape.
- `business_jargon_action_cliches` matched example: We need to lean into discomfort and circle back moving forward.
- `adverb_softener_intensifier` matched example: This is genuinely hard and actually matters.
- `at_its_core_filler` matched example: At its core, this is a coordination problem.
- `worth_noting_filler` matched example: It's worth noting that the model still failed.
- `end_of_day_filler` matched example: At the end of the day, the numbers decide.
- `when_it_comes_to_filler` matched example: When it comes to evaluation, consistency matters.
- `in_world_today_opener` matched example: In today's fast-paced digital landscape, clarity matters.
- `self_referential_structure_meta` matched example: The rest of this essay explains why the system breaks.
- `feature_not_bug_cliche` matched example: This is a feature, not a bug.
- `dressed_up_as_cliche` matched example: The plan is delay dressed up as strategy.
- `performative_promise` matched example: They exist, I promise.
- `creeps_in_personification` matched example: Doubt creeps in before the launch.
- `telling_difficulty_instead_of_showing` matched example: This is what leadership actually looks like.
- `actually_matters_formula` matched example: This is the part that actually matters.
- `vague_declarative_importance` matched example: The reasons are structural.
- `you_already_know_this_but` matched example: You already know this, but the process is broken.
- `another_post_aside` matched example: The incentive problem is worse, but that's another post.
