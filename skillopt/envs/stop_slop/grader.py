"""Stop-Slop grader: hard/soft scoring against the canonical pattern catalog.

Pipeline per rollout:
  1. ``regex_matches(rewrite, catalog)`` — fires every regex matcher.
  2. ``judge_matches(rewrite, catalog, judge_fn)`` — one batched LLM call
     against the 14 ``llm_judge`` patterns. Cached by sha256(rewrite).
  3. ``grade(rewrite, item, catalog, judge_fn)`` — combines into
     ``(hard, soft, diagnostics)`` per the design choices documented in
     ``__init__.py``.

The grader is a pure function over (rewrite, item, catalog, judge_fn);
all side effects (caching, model calls) are contained in ``judge_fn``.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# ── Catalog loading ─────────────────────────────────────────────────────────


@dataclass
class PatternEntry:
    id: str
    display_name: str
    description: str
    matcher_type: str  # "regex" | "llm_judge"
    regex: re.Pattern | None
    llm_prompt: str
    severity: str  # "high" | "medium" | "low"


_SEVERITY_WEIGHT = {"high": 3.0, "medium": 2.0, "low": 1.0}


def load_catalog(path: str | Path) -> dict[str, PatternEntry]:
    """Load ``banned_patterns.json`` into a dict[id, PatternEntry]."""
    with open(path) as f:
        raw = json.load(f)
    catalog: dict[str, PatternEntry] = {}
    for p in raw.get("patterns", []):
        matcher = p.get("matcher", {}) or {}
        m_type = matcher.get("type", "regex")
        regex = None
        if m_type == "regex" and matcher.get("regex"):
            try:
                regex = re.compile(matcher["regex"])
            except re.error as exc:  # noqa: BLE001
                raise ValueError(f"pattern {p['id']!r} has invalid regex: {exc}") from exc
        catalog[p["id"]] = PatternEntry(
            id=p["id"],
            display_name=p.get("display_name", p["id"]),
            description=p.get("description", ""),
            matcher_type=m_type,
            regex=regex,
            llm_prompt=matcher.get("llm_prompt", "") or "",
            severity=p.get("severity", "medium"),
        )
    return catalog


# ── Regex pass ──────────────────────────────────────────────────────────────


def regex_matches(text: str, catalog: dict[str, PatternEntry]) -> set[str]:
    """Return the set of canonical pattern_ids whose regex fires on ``text``."""
    if not text:
        return set()
    hits: set[str] = set()
    for pid, entry in catalog.items():
        if entry.matcher_type != "regex" or entry.regex is None:
            continue
        if entry.regex.search(text):
            hits.add(pid)
    return hits


# ── LLM-judge pass (batched + cached) ───────────────────────────────────────


JudgeFn = Callable[[str, list[PatternEntry]], dict[str, bool]]
"""A judge function: takes (text, list_of_patterns), returns {pattern_id: bool}.

The skillopt.envs.stop_slop.rollout module provides the production
implementation via ``chat_optimizer``. Tests can pass a deterministic
stub.
"""


class JudgeCache:
    """In-process cache for judge results, keyed by sha256(text)."""

    def __init__(self, maxsize: int = 4096) -> None:
        self._lock = threading.Lock()
        self._data: OrderedDict[str, dict[str, bool]] = OrderedDict()
        self._maxsize = maxsize
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def get(self, text: str) -> dict[str, bool] | None:
        key = self._key(text)
        with self._lock:
            if key in self._data:
                self.hits += 1
                self._data.move_to_end(key)
                return dict(self._data[key])
            self.misses += 1
            return None

    def put(self, text: str, result: dict[str, bool]) -> None:
        key = self._key(text)
        with self._lock:
            self._data[key] = dict(result)
            self._data.move_to_end(key)
            while len(self._data) > self._maxsize:
                self._data.popitem(last=False)


def judge_matches(
    text: str,
    catalog: dict[str, PatternEntry],
    judge_fn: JudgeFn,
    cache: JudgeCache | None = None,
) -> set[str]:
    """Return the set of llm_judge pattern_ids that fire on ``text``.

    Issues at most one ``judge_fn`` call per text via batching of every
    ``llm_judge`` pattern in the catalog. Caches by sha256(text) when a
    cache is provided.
    """
    if not text:
        return set()
    judge_patterns = [e for e in catalog.values() if e.matcher_type == "llm_judge"]
    if not judge_patterns:
        return set()

    if cache is not None:
        cached = cache.get(text)
        if cached is not None:
            return {pid for pid, hit in cached.items() if hit}

    result = judge_fn(text, judge_patterns)
    if cache is not None:
        cache.put(text, result)
    return {pid for pid, hit in result.items() if hit}


# ── Combined per-text matcher ───────────────────────────────────────────────


def all_matches(
    text: str,
    catalog: dict[str, PatternEntry],
    judge_fn: JudgeFn,
    cache: JudgeCache | None = None,
) -> set[str]:
    """Union of regex hits and LLM-judge hits."""
    return regex_matches(text, catalog) | judge_matches(text, catalog, judge_fn, cache)


# ── Grade per rollout ───────────────────────────────────────────────────────


@dataclass
class GradeResult:
    hard: int  # 0 or 1
    soft: float  # in [0, 1]
    diagnostics: dict  # for the analyst / reflect stage

    def to_skillopt(self) -> tuple[int, float, dict]:
        """Return (hard, soft, diagnostics) tuple the rollout expects."""
        return self.hard, self.soft, self.diagnostics


def _severity_weighted_sum(pattern_ids: set[str], catalog: dict[str, PatternEntry]) -> float:
    return sum(_SEVERITY_WEIGHT.get(catalog[pid].severity, 1.0) for pid in pattern_ids if pid in catalog)


def _positive_soft_score(
    input_tags: set[str],
    rewrite_hits: set[str],
    catalog: dict[str, PatternEntry],
) -> float:
    """Severity-weighted positive score.

    Composition (each term in [0,1]):
      * removal: fraction of input's tagged-severity weight that the
        rewrite no longer triggers.
      * cleanliness: fraction of catalog severity weight NOT introduced as
        new patterns in the rewrite (excluding input's original tags).

    Final = 0.5 * removal + 0.5 * cleanliness — equal-weight blend so a
    rewrite that drops one input pattern but adds three new ones is not
    rewarded as much as it would be under removal-only.
    """
    catalog_total = sum(_SEVERITY_WEIGHT.get(e.severity, 1.0) for e in catalog.values())
    if catalog_total <= 0:
        return 0.0

    if input_tags:
        input_weight = _severity_weighted_sum(input_tags, catalog)
        if input_weight <= 0:
            removal = 1.0
        else:
            still_present = input_tags & rewrite_hits
            removed_weight = input_weight - _severity_weighted_sum(still_present, catalog)
            removal = max(0.0, min(1.0, removed_weight / input_weight))
    else:
        removal = 1.0

    new_patterns = rewrite_hits - input_tags
    new_weight = _severity_weighted_sum(new_patterns, catalog)
    cleanliness = max(0.0, min(1.0, 1.0 - (new_weight / catalog_total)))

    return 0.5 * removal + 0.5 * cleanliness


def grade(
    rewrite: str,
    item: dict,
    catalog: dict[str, PatternEntry],
    judge_fn: JudgeFn,
    cache: JudgeCache | None = None,
) -> GradeResult:
    """Score a rewrite against an item per the chosen semantics."""
    is_negative = bool(item.get("is_negative", False))
    prose_in = (item.get("prose_in") or "").strip()
    rewrite_text = (rewrite or "").strip()

    input_tags = {tag["pattern_id"] for tag in item.get("banned_patterns") or [] if isinstance(tag, dict)}
    input_tags = {pid for pid in input_tags if pid in catalog}

    rewrite_hits = all_matches(rewrite_text, catalog, judge_fn, cache)
    new_patterns = rewrite_hits - input_tags
    still_present = input_tags & rewrite_hits

    diagnostics = {
        "input_tags": sorted(input_tags),
        "rewrite_hits": sorted(rewrite_hits),
        "still_present": sorted(still_present),
        "new_patterns": sorted(new_patterns),
        "is_negative": is_negative,
        "rewrite_chars": len(rewrite_text),
    }

    if is_negative:
        hard = 0 if rewrite_text == prose_in else 1
        # Soft for negatives: 1.0 if no banned patterns at all; otherwise the
        # general cleanliness measure. Removes need for a separate sub-grader.
        catalog_total = sum(_SEVERITY_WEIGHT.get(e.severity, 1.0) for e in catalog.values())
        new_weight = _severity_weighted_sum(rewrite_hits, catalog)
        soft = max(0.0, min(1.0, 1.0 - (new_weight / catalog_total))) if catalog_total > 0 else 0.0
        diagnostics["mode"] = "negative"
        return GradeResult(hard=hard, soft=float(soft), diagnostics=diagnostics)

    hard = 1 if (not still_present and not new_patterns) else 0
    soft = _positive_soft_score(input_tags, rewrite_hits, catalog)
    diagnostics["mode"] = "positive"
    return GradeResult(hard=hard, soft=float(soft), diagnostics=diagnostics)


# ── Default JudgeFn factory using the optimizer backend ─────────────────────


def make_optimizer_judge_fn() -> JudgeFn:
    """Build a JudgeFn that calls ``chat_optimizer`` with one batched prompt.

    Returns a callable suitable for passing into ``judge_matches`` /
    ``grade``. Imported lazily inside the function so unit tests can
    avoid pulling in the model backends.
    """

    def _judge(text: str, patterns: list[PatternEntry]) -> dict[str, bool]:
        from skillopt.model import chat_optimizer
        from skillopt.utils import extract_json

        rubric_lines = []
        for p in patterns:
            rubric_lines.append(f"- `{p.id}` — {p.display_name}: {p.llm_prompt or p.description}")
        system = (
            "You are a strict editor judging whether a passage of prose contains "
            "specific AI-writing tells. For each pattern, answer yes only if the "
            "tell is unambiguously present and prominent (not incidental). "
            "Return STRICT JSON with one boolean per pattern id. No prose, no "
            "markdown fences, no commentary."
        )
        user = (
            "PATTERNS TO JUDGE:\n"
            + "\n".join(rubric_lines)
            + "\n\nPASSAGE:\n"
            + text
            + "\n\nReturn JSON of the shape: "
            + '{"'
            + (patterns[0].id if patterns else "example")
            + '": true|false, ...}'
        )
        try:
            response, _ = chat_optimizer(system=system, user=user, max_completion_tokens=2048)
        except Exception:  # noqa: BLE001
            return {p.id: False for p in patterns}

        parsed = extract_json(response) or {}
        if not isinstance(parsed, dict):
            return {p.id: False for p in patterns}
        return {p.id: bool(parsed.get(p.id, False)) for p in patterns}

    return _judge
