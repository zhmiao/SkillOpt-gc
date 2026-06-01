"""Stop-Slop reflect: minibatch analyst integration.

This module is a thin wrapper around the generic ``run_minibatch_reflect``
from ``skillopt.gradient.reflect``. The adapter's ``reflect`` method
delegates here.

The grader's ``diagnostics`` (input_tags, still_present, new_patterns)
are passed into each item's payload so the analyst sees not just the
target's output but also which specific banned patterns survived or
were introduced. That's the per-item training signal.
"""

from __future__ import annotations

from skillopt.gradient.reflect import run_minibatch_reflect


def run_reflect(
    *,
    results: list[dict],
    skill_content: str,
    prediction_dir: str,
    patches_dir: str,
    workers: int = 16,
    failure_only: bool = False,
    minibatch_size: int = 8,
    edit_budget: int = 4,
    random_seed: int | None = None,
    error_system: str | None = None,
    success_system: str | None = None,
    step_buffer_context: str = "",
    meta_skill_context: str = "",
    update_mode: str = "patch",
) -> list[dict | None]:
    return run_minibatch_reflect(
        results=results,
        skill_content=skill_content,
        prediction_dir=prediction_dir,
        patches_dir=patches_dir,
        workers=workers,
        failure_only=failure_only,
        minibatch_size=minibatch_size,
        edit_budget=edit_budget,
        random_seed=random_seed,
        error_system=error_system,
        success_system=success_system,
        step_buffer_context=step_buffer_context,
        meta_skill_context=meta_skill_context,
        update_mode=update_mode,
    )
