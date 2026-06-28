"""Stop-Slop environment for SkillOpt.

Trains a skill document that rewrites AI-tell-laden prose into cleaner
prose. Each rollout: target reads the candidate skill + an input
passage, returns a rewrite, the grader scores the rewrite against the
canonical banned-pattern catalog at
``data/stop_slop_split/banned_patterns.json``.

The grader semantics are documented in
``dev_docs/design/copilot_integration_plan.md`` and were chosen by the
user in the 2026-06-01 form:

- Positive items: ``hard=1`` iff every pattern tagged on ``prose_in``
  is absent from the rewrite AND no new banned patterns appear.
- Negative items (``prose_in`` is itself the rejected rewrite):
  ``hard=1`` iff the target's rewrite is not identical to ``prose_in``.
- Soft score: severity-weighted (high=3, medium=2, low=1) average of
  per-pattern wins, blended with the regression-penalty for new
  patterns.
- LLM-judge patterns (~14 of 57) are evaluated on every rollout via
  one batched call per text, with a sha256-keyed in-process cache.
"""
