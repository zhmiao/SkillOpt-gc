#!/usr/bin/env python3
"""Merge the 4 stop_slop dataset construction streams into a SkillOpt split.

Inputs:
  dev_docs/design/dataset_construction/stream{1,2,3}_items.json
  dev_docs/design/dataset_construction/stream4_patterns.json

Outputs:
  data/stop_slop_split/train/items.json
  data/stop_slop_split/val/items.json
  data/stop_slop_split/test/items.json
  data/stop_slop_split/banned_patterns.json
  data/stop_slop_split/split_manifest.json
  dev_docs/design/dataset_construction/merge_report.md

Pipeline:
  1. Load all 4 stream files + the canonical pattern catalog.
  2. Expand the canonical catalog with NEW patterns surfaced by streams 1/2/3
     (anaphora, q_and_a, staccato, metaphor_overuse, etc.). Without this the
     remap step drops too many items.
  3. Apply a deterministic pattern_id remap (variant → canonical).
  4. Drop items whose every banned_pattern remaps to None (signal-free).
  5. Dedupe by sha256(prose_in). Tie-break: high > medium > low quality;
     within same quality, hand_labeled > worktree_mined > auto_diff.
  6. Stratified 60/20/20 split by (is_negative, label_quality).
     Deterministic seed = 42.
  7. Write outputs + a merge report.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

REPO = Path(__file__).resolve().parents[1]
DC = REPO / "dev_docs" / "design" / "dataset_construction"
DATA = REPO / "data" / "stop_slop_split"


# ── New canonical patterns to ADD to the catalog ────────────────────────────

# Stream 4 missed these — they showed up multiple times across streams 1/2/3 and
# deserve their own canonical entries. Pattern shape mirrors stream4_patterns.json.
NEW_CANONICAL_PATTERNS = [
    {
        "id": "anaphora_repetition",
        "display_name": "Anaphoric repetition",
        "description": (
            "Sentence opener repeated across 2+ adjacent sentences to manufacture "
            "rhetorical sweep (e.g., 'All of it. All of it. All of it.'). Covers "
            "anaphoric pair / triplet / sweep / staircase variants."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage start 2+ consecutive sentences with the same word(s) "
                "to manufacture sweep? Answer yes only if the repetition is the "
                "dominant rhetorical move, not incidental."
            ),
        },
        "examples": [
            {"text": "All of it. All of it. All of it.", "source": "ai_writing_tells"},
        ],
        "source": "stream_observed",
        "severity": "high",
    },
    {
        "id": "metaphor_overuse",
        "display_name": "Metaphor cluster / pileup",
        "description": (
            "Multiple competing metaphors stacked in close proximity (crystal, mine, "
            "mirror, skeleton, bridge, waypoint…) — none developed enough to do "
            "real work. Includes 'skeleton of thought'-style abstract metaphors."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage stack 2+ unrelated metaphors in close proximity "
                "without developing any one? Skip if a single metaphor is sustained."
            ),
        },
        "examples": [
            {
                "text": "the bones of thought, the shape of how we reason, the crystal beneath the noise",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "high",
    },
    {
        "id": "q_and_a_pair",
        "display_name": "Q&A pair (chat-trained tell)",
        "description": (
            "A rhetorical question immediately answered by the writer — 'Can we go "
            "further? Yes.' / 'Better at what? At achieving a reward signal.' Strong "
            "chat-trained-model tell."
        ),
        "matcher": {
            "type": "regex",
            "regex": r"\?\s+[A-Z][^.?!]{2,80}[.?!]",
            "llm_prompt": None,
        },
        "examples": [
            {"text": "Can we go further? There may be a way past this limitation.", "source": "ai_writing_tells"},
        ],
        "source": "stream_observed",
        "severity": "high",
    },
    {
        "id": "staccato_fragmentation",
        "display_name": "Staccato fragmentation",
        "description": (
            "Sequence of 3+ very short sentences (≤8 words each) used for false "
            "weight: 'They are not intelligent. They extract structure. The result "
            "is imperfect.' Often a smoothing target that re-emerges after edits."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage contain 3+ consecutive sentences of ≤8 words each "
                "where the brevity feels manufactured rather than load-bearing?"
            ),
        },
        "examples": [
            {
                "text": "LLMs do not produce truth. They are not intelligent. They extract structure.",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "medium",
    },
    {
        "id": "throat_clearing_openers",
        "display_name": "Throat-clearing opener",
        "description": (
            "Sentence or paragraph begins with content-free meta-framing: 'Something "
            "older than vocabulary…', 'There is a kind of…', 'What I want to suggest "
            "is…'. Different from the specific openers ('it turns out', 'truth is') "
            "already catalogued; this is the generic class."
        ),
        "matcher": {
            "type": "regex",
            "regex": r"(?im)^\s*(There (?:is|are|was|were|may be)|Something (?:older|closer|prior|deeper)|What I (?:want to|am trying to|mean is))\b",
            "llm_prompt": None,
        },
        "examples": [
            {
                "text": "Something older than vocabulary, something closer to the bones of thought itself.",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "medium",
    },
    {
        "id": "balanced_cadence_aphorism",
        "display_name": "Balanced cadence / aphoristic kicker",
        "description": (
            "Sentence engineered for symmetric beats around a pivot — 'Not X. Not Y. "
            "But Z.' / 'Impure, because we are.' Often paired with em-dash or "
            "semicolon. Distinct from pseudo_profound_fragments by structural "
            "balance rather than mystery."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage end with a deliberately balanced 2-3 beat aphorism "
                "(matched syllables / mirrored grammar) that feels performative?"
            ),
        },
        "examples": [
            {"text": "Training isn't memorization — it is compression.", "source": "ai_writing_tells"},
        ],
        "source": "stream_observed",
        "severity": "medium",
    },
    {
        "id": "unclear_antecedent",
        "display_name": "Unclear pronoun antecedent",
        "description": (
            "Pronoun (it, this, that, they) whose referent is ambiguous between two "
            "or more recently-mentioned nouns. Common in AI prose because the model "
            "tracks coherence loosely."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage contain a pronoun (it/this/that/they) whose antecedent is ambiguous on first read?"
            ),
        },
        "examples": [
            {
                "text": "a human mind can hold only so much, and it can hold it only through natural language.",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "medium",
    },
    {
        "id": "fabricated_specificity",
        "display_name": "Fabricated specificity",
        "description": (
            "Invented concrete details (citations, numbers, named events) inserted "
            "to manufacture credibility. The HumanEmbedding corpus caught a "
            "fabricated Dillard quote and a malformed arXiv ID this way."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage contain a specific citation, number, or named "
                "event that looks plausible but cannot be verified?"
            ),
        },
        "examples": [
            {
                "text": "as Dillard wrote in The Writing Life, 'the precision of the line itself…'",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "high",
    },
    {
        "id": "stripped_causal_connective",
        "display_name": "Stripped causal connective",
        "description": (
            "Removal of 'because', 'since', 'so that' between clauses to manufacture "
            "telegraph cadence. Two clauses placed side-by-side without the "
            "explanatory link that the prose actually relies on."
        ),
        "matcher": {
            "type": "llm_judge",
            "regex": None,
            "llm_prompt": (
                "Does the passage place 2+ clauses side-by-side where a 'because' / "
                "'since' / 'so that' connective is implied but suppressed?"
            ),
        },
        "examples": [
            {
                "text": "The pixels are one input among several. An off-the-shelf classifier has only those.",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "low",
    },
    {
        "id": "vague_grand_abstraction",
        "display_name": "Vague grand abstraction",
        "description": (
            "Noun phrases of the form 'the X of Y' or 'the geometry of Z' that "
            "wave at a profound concept without specifying what it actually is — "
            "'the shape of how we reason', 'the geometry of meaning', 'the "
            "architecture of disagreement'."
        ),
        "matcher": {
            "type": "regex",
            "regex": r"\bthe (?:shape|geometry|architecture|texture|topology|grammar|fabric) of \w+",
            "llm_prompt": None,
        },
        "examples": [
            {
                "text": "the shape of how we reason, prior to the words we happen to reason in.",
                "source": "ai_writing_tells",
            },
        ],
        "source": "stream_observed",
        "severity": "medium",
    },
]


# ── Pattern remap table (stream_level_id → canonical_id) ────────────────────

# Built by inspecting all unique stream-level IDs against the (extended)
# canonical catalog. Maps to None to DROP the tag (item kept if at least one
# of its tags maps to a real canonical).
PATTERN_REMAP: dict[str, str | None] = {
    # ─ Em-dash family (all variants → canonical em_dash_overuse) ─
    "em_dash_overuse": "em_dash_overuse",
    "em_dash_abstract_foundation": "em_dash_overuse",
    "em_dash_bare_architecture": "em_dash_overuse",
    "em_dash_exotic_geography_pair": "em_dash_overuse",
    "em_dash_fragment_collapse": "em_dash_overuse",
    "em_dash_lived_weight_abstraction": "em_dash_overuse",
    "em_dash_metaphor_stack": "em_dash_overuse",
    "em_dash_not_what_contrast": "em_dash_overuse",
    "em_dash_not_x_but_y": "em_dash_overuse",
    "em_dash_smoothing": "em_dash_overuse",
    "em_dash_smoothing_staccato": "em_dash_overuse",
    "em_dash_substitution": "em_dash_overuse",
    "double_em_dash_insert": "em_dash_overuse",
    # ─ Adverbs ─
    "adverbs": "adverb_softener_intensifier",
    "ai_adverb": "adverb_softener_intensifier",
    "ai_adverb_strip": "adverb_softener_intensifier",
    # ─ Not X but Y family ─
    "not_x_but_y": "not_x_but_y_reveal",
    "not_x_but_y_reveal": "not_x_but_y_reveal",
    "not_x_but_y_inversion": "not_x_but_y_reveal",
    "not_x_but_y_reflex": "not_x_but_y_reveal",
    "not_x_it_is_y_inversion": "not_x_but_y_reveal",
    "not_only_x_but_y": "not_x_but_y_reveal",
    "not_because_x_but_because_y": "not_x_but_y_reveal",
    "its_not_this_its_that": "not_x_but_y_reveal",
    "mechanical_contrast": "not_x_but_y_reveal",
    "duplicate_antithesis": "not_x_but_y_reveal",
    "x_not_y_antithesis": "not_x_but_y_reveal",
    "balanced_antinomy": "not_x_but_y_reveal",
    # ─ Negative listing reveal ─
    "not_x_not_y_but_z": "negative_listing_reveal",
    "not_a_not_b_not_c_but_d": "negative_listing_reveal",
    "not_just_additive_hedge": "negative_listing_reveal",
    # ─ Rule of three / triplet family ─
    "rule_of_three": "rule_of_three",
    "rule_of_three_tricolon": "rule_of_three",
    "tricolon": "rule_of_three",
    "triplet": "rule_of_three",
    "parallel_triplet": "rule_of_three",
    "paired_item_triplet": "rule_of_three",
    "geographic_triplet": "rule_of_three",
    "asyndeton_adjective_triplet": "rule_of_three",
    "anaphoric_triplet": "rule_of_three",
    "exotic_breadth_triplet": "rule_of_three",
    "parallel_quintet": "rule_of_three",
    # ─ Meta commentary ─
    "meta_commentary": "word_choice_meta_commentary",
    "meta_commentary_i_mean": "word_choice_meta_commentary",
    "meta_commentary_on_word_choice": "word_choice_meta_commentary",
    "word_choice_meta_commentary": "word_choice_meta_commentary",
    # ─ Hedge ─
    "hedge_stack": "hedge_stack",
    "hedge_word": "hedge_stack",
    "hedged_declarative": "hedge_stack",
    "mild_hedge_plus_parallel_cascade": "hedge_stack",
    # ─ Importance inflation ─
    "importance_inflation": "importance_inflation",
    "redundant_grand_claim": "importance_inflation",
    "generic_universal_readability": "importance_inflation",
    "dramatized_wording": "importance_inflation",
    "lazy_extreme": "importance_inflation",
    # ─ Pseudo-profound fragments / aphorism ─
    "pseudo_profound_fragments": "pseudo_profound_fragments",
    "pressure_in_motion_pseudo_profundity": "pseudo_profound_fragments",
    "cosmic_koan": "pseudo_profound_fragments",
    "aphoristic_kicker": "balanced_cadence_aphorism",
    "redundant_aphoristic_kicker": "balanced_cadence_aphorism",
    "twin_balance_kicker": "balanced_cadence_aphorism",
    "two_word_kicker": "balanced_cadence_aphorism",
    "balanced_cadence": "balanced_cadence_aphorism",
    "balanced_semicolon_aphorism": "balanced_cadence_aphorism",
    # ─ Unvaried sentence rhythm ─
    "even_sentence_rhythm": "unvaried_sentence_rhythm",
    "perfect_rhythm_unvaried_sentence_length": "unvaried_sentence_rhythm",
    "mechanical_parallel_openers": "unvaried_sentence_rhythm",
    "broken_parallel_verb_structure": "unvaried_sentence_rhythm",
    "sentence_completion": "unvaried_sentence_rhythm",
    # ─ Throat-clearing / pseudo-openers ─
    "throat_clearing": "throat_clearing_openers",
    "throat_clearing_openers": "throat_clearing_openers",
    "something_x_opener": "throat_clearing_openers",
    "something_older_something_closer": "throat_clearing_openers",
    "something_older_closer_formula": "throat_clearing_openers",
    "there_is_opener": "throat_clearing_openers",
    "there_may_be_opener": "throat_clearing_openers",
    "aim_framing": "throat_clearing_openers",
    "abrupt_section_join": "throat_clearing_openers",
    # ─ Vague grand abstraction ─
    "grand_concept": "vague_grand_abstraction",
    "grand_ai_abstract": "vague_grand_abstraction",
    "geometric_grand_abstraction": "vague_grand_abstraction",
    "geometry_metaphor_cluster": "vague_grand_abstraction",
    "shape_of_abstraction": "vague_grand_abstraction",
    "doubled_abstraction": "vague_grand_abstraction",
    "genitive_abstraction": "vague_grand_abstraction",
    "vague_abstraction": "vague_grand_abstraction",
    "vague_declarative_importance": "vague_grand_abstraction",
    "textbook_spectrum": "vague_grand_abstraction",
    # ─ Geographic stuffing ─
    "geographic_diversity_stuffing": "geographic_diversity_stuffing",
    # ─ Overused transitions / pivot smoothing ─
    "overused_transitions": "overused_transitions",
    "and_yet_pivot": "overused_transitions",
    "nonpivot_and_smoothing": "overused_transitions",
    "over_smoothing_nonpivot_connective": "overused_transitions",
    # ─ Anaphora (NEW canonical) ─
    "anaphoric_pair": "anaphora_repetition",
    "anaphoric_sentence_split": "anaphora_repetition",
    "anaphoric_sweep": "anaphora_repetition",
    "anaphoric_x_beneath_y_triplet": "anaphora_repetition",
    "every_x_anaphora": "anaphora_repetition",
    "four_fold_parallel_anaphora": "anaphora_repetition",
    "paired_anaphora": "anaphora_repetition",
    "staircase": "anaphora_repetition",
    "staircase_anaphora": "anaphora_repetition",
    # ─ Q&A (NEW canonical) ─
    "q_and_a_pair": "q_and_a_pair",
    "q_and_a_sequence": "q_and_a_pair",
    "q_and_a_staircase": "q_and_a_pair",
    # ─ Staccato (NEW canonical) ─
    "staccato_fragmentation": "staccato_fragmentation",
    "staccato_smoothing": "staccato_fragmentation",
    "staccato_smoothing_register_shift": "staccato_fragmentation",
    # ─ Metaphor overuse (NEW canonical) ─
    "metaphor_cluster": "metaphor_overuse",
    "metaphor_pileup": "metaphor_overuse",
    "metaphor_ghost_skeleton": "metaphor_overuse",
    "skeleton_metaphor": "metaphor_overuse",
    "generic_flattening_metaphor_erasure": "metaphor_overuse",
    "generic_technical_metaphor_erasure": "metaphor_overuse",
    # ─ Unclear antecedent (NEW canonical) ─
    "unclear_antecedent": "unclear_antecedent",
    "cross_paragraph_antecedent": "unclear_antecedent",
    "dangling_apposition_tone_shift": "unclear_antecedent",
    "indirect_speech_tense_mismatch": "unclear_antecedent",
    "label_collision": "unclear_antecedent",
    # ─ Fabricated specificity (NEW canonical) ─
    "fabricated_specificity": "fabricated_specificity",
    # ─ Stripped causal connectives (NEW canonical) ─
    "stripped_causal_connective": "stripped_causal_connective",
    "stripped_causal_connectives": "stripped_causal_connective",
    "telling_not_showing": "stripped_causal_connective",
    # ─ Unearned spiritual register ─
    "unearned_spiritual_register": "unearned_spiritual_register",
    "italicized_abstract_emphasis": "unearned_spiritual_register",
    "purified_crystallized_doublet": "unearned_spiritual_register",
    # ─ Misc / drop ─
    "awkward_preposition_stranding": None,  # grammar issue, not slop
    "cleft_construction": None,  # legitimate structure
    "do_too_tag": None,  # not slop signal
    "loose_technical_plural": None,  # field-specific terminology
    "mid_sentence_inversion": None,  # style, not slop
}


# ── IO ───────────────────────────────────────────────────────────────────────


def load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, obj, indent: int = 2):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)


# ── Pipeline ────────────────────────────────────────────────────────────────


def main():
    s1 = load_json(DC / "stream1_items.json")
    s2 = load_json(DC / "stream2_items.json")
    s3 = load_json(DC / "stream3_items.json")
    catalog = load_json(DC / "stream4_patterns.json")

    print(
        f"Loaded streams: s1={len(s1)} s2={len(s2)} s3={len(s3)} catalog={len(catalog['patterns'])} canonical patterns"
    )

    # ── 2. Extend canonical catalog ─────────────────────────────────────────
    existing_ids = {p["id"] for p in catalog["patterns"]}
    for new_p in NEW_CANONICAL_PATTERNS:
        if new_p["id"] not in existing_ids:
            catalog["patterns"].append(new_p)
    catalog["version"] = "2"
    catalog["generated_at"] = datetime.now(timezone.utc).isoformat()
    canonical_ids = {p["id"] for p in catalog["patterns"]}
    print(f"Extended catalog: {len(canonical_ids)} canonical patterns (+{len(NEW_CANONICAL_PATTERNS)} new)")

    # ── 3. Remap + drop signal-free items ──────────────────────────────────
    all_items = s1 + s2 + s3
    remap_misses: Counter = Counter()
    items_remapped: list[dict] = []
    items_dropped_no_signal: list[dict] = []

    for item in all_items:
        new_patterns = []
        for tag in item["banned_patterns"]:
            pid = tag["pattern_id"]
            mapped = PATTERN_REMAP.get(pid, "__UNMAPPED__")
            if mapped == "__UNMAPPED__":
                remap_misses[pid] += 1
                continue
            if mapped is None:
                continue
            if mapped not in canonical_ids:
                remap_misses[f"<bad_target:{mapped}>"] += 1
                continue
            new_patterns.append(
                {
                    "pattern_id": mapped,
                    "evidence": tag.get("evidence", ""),
                }
            )

        # dedup canonical ids within an item (multiple variants → one canonical)
        seen = set()
        deduped = []
        for tag in new_patterns:
            if tag["pattern_id"] in seen:
                continue
            seen.add(tag["pattern_id"])
            deduped.append(tag)

        if not deduped:
            items_dropped_no_signal.append(item)
            continue

        merged = dict(item)
        merged["banned_patterns"] = deduped
        items_remapped.append(merged)

    print(f"Remapped: {len(items_remapped)} kept; {len(items_dropped_no_signal)} dropped (all patterns mapped to None)")
    if remap_misses:
        print(f"⚠ Unmapped pattern IDs: {dict(remap_misses)}")

    # ── 4. Dedupe by prose_in hash ──────────────────────────────────────────
    QUALITY_RANK = {"high": 3, "medium": 2, "low": 1}
    STREAM_RANK = {"hand_labeled": 3, "worktree_mined": 2, "auto_diff": 1}

    def rank(item) -> tuple:
        return (
            QUALITY_RANK.get(item.get("label_quality", "medium"), 0),
            STREAM_RANK.get(item.get("source", {}).get("stream", ""), 0),
        )

    by_hash: dict[str, dict] = {}
    dup_count = 0
    for item in items_remapped:
        h = hashlib.sha256(item["prose_in"].strip().encode()).hexdigest()
        existing = by_hash.get(h)
        if existing is None or rank(item) > rank(existing):
            if existing is not None:
                dup_count += 1
            by_hash[h] = item
        else:
            dup_count += 1

    deduped = list(by_hash.values())
    print(f"Deduped: {len(deduped)} unique items; {dup_count} duplicates dropped")

    # ── 5. Stratified split 60/20/20 ────────────────────────────────────────
    rng = random.Random(42)

    strata: dict[tuple, list] = defaultdict(list)
    for item in deduped:
        key = (item.get("is_negative", False), item.get("label_quality", "medium"))
        strata[key].append(item)

    train: list = []
    val: list = []
    test: list = []
    for key, group in strata.items():
        rng.shuffle(group)
        n = len(group)
        n_train = int(n * 0.60)
        n_val = int(n * 0.20)
        train.extend(group[:n_train])
        val.extend(group[n_train : n_train + n_val])
        test.extend(group[n_train + n_val :])

    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)

    print(f"Split: train={len(train)} val={len(val)} test={len(test)}")

    # ── 6. Add stable item id field if missing ──────────────────────────────
    # Items already have an `id`; assert uniqueness.
    all_ids = [item["id"] for item in train + val + test]
    if len(set(all_ids)) != len(all_ids):
        raise SystemExit("ERROR: non-unique item IDs after merge")

    # ── 7. Write outputs ────────────────────────────────────────────────────
    write_json(DATA / "train" / "items.json", train)
    write_json(DATA / "val" / "items.json", val)
    write_json(DATA / "test" / "items.json", test)
    write_json(DATA / "banned_patterns.json", catalog)

    manifest = {
        "source_corpus": "/home/miao/repos/HumanEmbedding",
        "split_mode": "ratio",
        "split_ratio": "60:20:20",
        "split_seed": 42,
        "stratified_by": ["is_negative", "label_quality"],
        "counts": {
            "train": len(train),
            "val": len(val),
            "test": len(test),
            "total": len(deduped),
        },
        "streams": {
            "stream1_hand_labeled": len(s1),
            "stream2_auto_diff": len(s2),
            "stream3_worktree_mined": len(s3),
            "stream4_patterns": len(catalog["patterns"]),
        },
        "post_merge": {
            "items_kept": len(items_remapped),
            "items_dropped_no_signal": len(items_dropped_no_signal),
            "duplicates_dropped": dup_count,
            "unmapped_pattern_ids": dict(remap_misses),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(DATA / "split_manifest.json", manifest)

    # ── 8. Merge report ─────────────────────────────────────────────────────
    quality_dist = Counter((it["label_quality"], it.get("is_negative", False)) for it in deduped)
    pattern_freq = Counter(t["pattern_id"] for it in deduped for t in it["banned_patterns"])

    report_lines = []
    report_lines.append("# `stop_slop` Dataset Merge Report\n")
    report_lines.append(f"_Generated {datetime.now(timezone.utc).isoformat()}_\n")
    report_lines.append("## Per-stream input counts\n")
    report_lines.append(f"- Stream 1 (hand_labeled, high quality): {len(s1)}")
    report_lines.append(f"- Stream 2 (auto_diff, medium quality):  {len(s2)}")
    report_lines.append(f"- Stream 3 (worktree_mined, negatives):  {len(s3)}")
    report_lines.append(f"- **Total raw**: {len(all_items)}\n")
    report_lines.append("## Canonical pattern catalog\n")
    report_lines.append(f"- Stream 4 original: {len(catalog['patterns']) - len(NEW_CANONICAL_PATTERNS)}")
    report_lines.append(f"- New canonical (added by merge for unmapped variants): {len(NEW_CANONICAL_PATTERNS)}")
    report_lines.append(f"- **Final canonical count**: {len(catalog['patterns'])}\n")
    report_lines.append("### New canonical patterns added")
    for p in NEW_CANONICAL_PATTERNS:
        report_lines.append(f"- `{p['id']}` — {p['display_name']} ({p['matcher']['type']}, severity={p['severity']})")
    report_lines.append("")
    report_lines.append("## Remap pipeline\n")
    report_lines.append(f"- Items after remap: {len(items_remapped)}")
    report_lines.append(f"- Items dropped (no remappable pattern): {len(items_dropped_no_signal)}")
    report_lines.append(f"- Duplicates dropped: {dup_count}")
    report_lines.append(f"- **Final unique items**: {len(deduped)}\n")
    if remap_misses:
        report_lines.append("### Unmapped pattern IDs (these tags were dropped)")
        for pid, count in remap_misses.most_common():
            report_lines.append(f"- `{pid}` ({count})")
        report_lines.append("")
    report_lines.append("## Quality distribution (final)\n")
    report_lines.append("| Quality | Positive | Negative |")
    report_lines.append("|---|---:|---:|")
    for q in ("high", "medium", "low"):
        pos = quality_dist.get((q, False), 0)
        neg = quality_dist.get((q, True), 0)
        if pos or neg:
            report_lines.append(f"| {q} | {pos} | {neg} |")
    report_lines.append("")
    report_lines.append("## Split sizes\n")
    report_lines.append(f"- train: {len(train)}")
    report_lines.append(f"- val:   {len(val)}")
    report_lines.append(f"- test:  {len(test)}")
    report_lines.append("")
    report_lines.append("## Pattern frequency in final dataset\n")
    report_lines.append("| pattern_id | count |")
    report_lines.append("|---|---:|")
    for pid, count in pattern_freq.most_common():
        report_lines.append(f"| `{pid}` | {count} |")
    report_lines.append("")
    report_lines.append("## Sample items (verbatim)\n")
    samples = []
    for it in train:
        if not it.get("is_negative") and it.get("label_quality") == "high":
            samples.append(("high positive", it))
            break
    for it in train:
        if not it.get("is_negative") and it.get("label_quality") == "medium":
            samples.append(("medium positive", it))
            break
    for it in train + val + test:
        if it.get("is_negative"):
            samples.append(("negative", it))
            break
    for it in train:
        if it.get("gold_rewrite") == "":
            samples.append(("pure deletion", it))
            break
    for it in test:
        if not it.get("is_negative"):
            samples.append(("test-split sample", it))
            break
    for label, it in samples:
        report_lines.append(f"### {label}\n```json")
        report_lines.append(json.dumps(it, indent=2, ensure_ascii=False))
        report_lines.append("```\n")

    (DC / "merge_report.md").write_text("\n".join(report_lines))

    print(f"\nWrote:\n  {DATA}/train/items.json")
    print(f"  {DATA}/val/items.json")
    print(f"  {DATA}/test/items.json")
    print(f"  {DATA}/banned_patterns.json")
    print(f"  {DATA}/split_manifest.json")
    print(f"  {DC}/merge_report.md")


if __name__ == "__main__":
    main()
