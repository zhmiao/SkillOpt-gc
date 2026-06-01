"""Stop-Slop rollout: per-item target invocation + grading.

For each item, build a prompt that loads the candidate skill into the
target's system role and presents the input passage with an instruction
to return the rewrite inside ``<rewrite>...</rewrite>`` tags.

Routes through ``chat_target`` for chat backends and through
``run_target_exec`` (via the codex harness) for exec backends —
``copilot_cli_exec``, ``codex_exec``, ``claude_code_exec``.
"""

from __future__ import annotations

import json
import os
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from skillopt.envs.stop_slop.grader import (
    JudgeCache,
    grade,
    load_catalog,
    make_optimizer_judge_fn,
)
from skillopt.model import chat_target, is_target_exec_backend
from skillopt.model.codex_harness import prepare_workspace, render_skill_md, run_target_exec

# ── Prompt construction ─────────────────────────────────────────────────────


def build_system(skill_content: str) -> str:
    skill = (skill_content or "").strip() or "(No additional rules provided.)"
    return (
        "You are a careful editor. Rewrite the user's passage to remove AI-writing "
        "tells while keeping the original meaning, voice, and important details intact.\n\n"
        "## Skill\n"
        f"{skill}\n\n"
        "## Output format\n"
        "Return only the rewrite inside <rewrite>...</rewrite> tags. Do not add commentary, "
        "headings, or explanations. If the original passage is best removed entirely (e.g., "
        "pure throat-clearing), return empty <rewrite></rewrite>."
    )


def build_user(item: dict) -> str:
    ctx_before = (item.get("context_before") or "").strip()
    ctx_after = (item.get("context_after") or "").strip()
    parts = []
    if ctx_before:
        parts.append(f"## Context (before)\n{ctx_before}")
    parts.append(f"## Passage to rewrite\n{(item.get('prose_in') or '').strip()}")
    if ctx_after:
        parts.append(f"## Context (after)\n{ctx_after}")
    return "\n\n".join(parts)


_REWRITE_RE = re.compile(r"<rewrite>(.*?)</rewrite>", re.DOTALL | re.IGNORECASE)


def _write_conversation(
    pred_dir: str,
    *,
    item: dict,
    rewrite: str,
    graded,
    raw_response: str,
) -> None:
    """Persist the per-item conversation in the format the reflect stage expects.

    ``skillopt.gradient.reflect.fmt_minibatch_trajectories`` looks for
    ``<prediction_dir>/<id>/conversation.json``; if the file is missing,
    the formatter silently skips the item, which propagates as "0 edits"
    out of the analyst with no diagnostic. Writing this file (even when
    the rollout failed) keeps the analyst's view of the batch complete.

    The conversation is rendered as a tool-call-style list (one
    ``"tool_call"`` per rollout: ``cmd`` = the prose to rewrite,
    ``obs`` = the rewrite the target produced). The reflect formatter
    handles this shape natively.
    """
    prose_in = (item.get("prose_in") or "").strip()
    gold = (item.get("gold_rewrite") or "").strip()
    diag_text = ""
    if graded is not None:
        diag = graded.diagnostics or {}
        diag_text = (
            f"hard={graded.hard}  soft={graded.soft:.3f}  mode={diag.get('mode')}\n"
            f"input_tags={diag.get('input_tags')}\n"
            f"rewrite_hits={diag.get('rewrite_hits')}\n"
            f"still_present={diag.get('still_present')}\n"
            f"new_patterns={diag.get('new_patterns')}\n"
        )
    obs_parts = [f"<rewrite>\n{rewrite}\n</rewrite>"] if rewrite else ["<rewrite></rewrite> (no tag returned)"]
    if diag_text:
        obs_parts.append(f"[grader diagnostics]\n{diag_text}")
    if gold:
        obs_parts.append(f"[gold rewrite]\n{gold}")
    conversation = [
        {
            "type": "tool_call",
            "cmd": f"rewrite_prose:\n{prose_in}",
            "obs": "\n\n".join(obs_parts),
        }
    ]
    try:
        with open(os.path.join(pred_dir, "conversation.json"), "w", encoding="utf-8") as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
    except Exception:  # noqa: BLE001
        pass


def extract_rewrite(response: str) -> tuple[str, bool]:
    """Pull the rewrite text out of ``<rewrite>...</rewrite>`` tags.

    Returns ``(rewrite_text, tag_found)``. If no tag is found, returns
    ``("", False)``: the caller decides whether to mark the rollout as
    failed or fall back. Refusing to fall back here prevents the grader
    from scoring stderr / error transcripts as valid rewrites (which
    would otherwise look like perfect ``hard=1`` outputs).

    Empty-but-tagged content (``<rewrite></rewrite>``) is a valid rewrite
    and returns ``("", True)`` — meaningful for "delete the whole
    passage" target outputs.
    """
    if not response:
        return "", False
    match = _REWRITE_RE.search(response)
    if match:
        return match.group(1).strip(), True
    return "", False


# ── Exec-backend dispatch ───────────────────────────────────────────────────


def _run_exec_once(*, pred_dir: str, skill_content: str, item: dict, model: str, timeout: int) -> tuple[str, str]:
    """Legacy workspace-based exec path (kept for codex_exec / claude_code_exec).

    Writes task + skill to disk and tells the agent to read them. Suitable
    for agentic harnesses where the model is expected to use file-IO tools.
    Stop-slop now prefers :func:`_run_inline_copilot_once` for copilot_cli_exec
    because workspace exploration cost ~13% of rollouts in the dry run.
    """
    task_text = build_user(item)
    skill_md = render_skill_md(
        skill_content,
        description="Dynamic Stop-Slop rewrite skill.",
        preamble=(
            "Apply the rewrite rules in the Dynamic Guidance section to the passage in task.md. "
            "Return the rewrite inside <rewrite>...</rewrite> tags."
        ),
    )
    work_dir = os.path.join(pred_dir, "target_exec")
    prepare_workspace(work_dir=work_dir, skill_md=skill_md, task_text=task_text)
    prompt = (
        "Use the `skillopt-target` skill in this workspace.\n"
        "Read task.md and produce a rewrite of the passage.\n"
        "Return ONLY the rewrite inside <rewrite>...</rewrite> tags."
    )
    response, raw = run_target_exec(
        work_dir=work_dir,
        prompt=prompt,
        model=model,
        timeout=timeout,
    )
    return response or raw, raw


def _run_inline_copilot_once(
    *,
    pred_dir: str,
    skill_content: str,
    item: dict,
    model: str,
    timeout: int,
) -> tuple[str, str]:
    """Pure-text rewrite via Copilot CLI with tools disabled.

    Embeds the skill and the input prose directly into the prompt and
    calls ``run_copilot_cli_exec`` with ``available_tools=""`` and
    ``raw_prompt=True``. This bypasses the workspace-file approach used
    by :func:`_run_exec_once` and the target-side wrapper added by
    ``_exec_prompt``, eliminating the tool-exploration failure mode
    that produced ``no_rewrite_tag_in_response`` results in the
    2026-06-01 dry run.
    """
    import tempfile

    from skillopt.model.codex_harness import run_copilot_cli_exec

    system = build_system(skill_content)
    user = build_user(item)
    prompt = (
        "# System\n"
        + system
        + "\n\n# User\n"
        + user
        + "\n\n# Output\n"
        + "Return only the rewrite inside <rewrite>...</rewrite> tags. "
        + "No commentary, no markdown fences, no headings. Do not call any tools."
    )
    with tempfile.TemporaryDirectory(prefix="skillopt_stop_slop_") as work_dir:
        # work_dir is empty, available_tools='' disables tools, raw_prompt=True
        # bypasses the target-side workspace wrapper. Persistence of the raw
        # transcript happens inside run_copilot_cli_exec.
        response, raw = run_copilot_cli_exec(
            work_dir=work_dir,
            prompt=prompt,
            model=model,
            timeout=timeout,
            available_tools="",
            raw_prompt=True,
        )
        # The original pred_dir is where downstream code looks for artifacts;
        # copy the trace there for parity with _run_exec_once's persistence.
        try:
            os.makedirs(pred_dir, exist_ok=True)
            with open(os.path.join(pred_dir, "copilot_inline_raw.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
            with open(os.path.join(pred_dir, "copilot_inline_response.txt"), "w", encoding="utf-8") as f:
                f.write(response)
        except Exception:  # noqa: BLE001
            pass
    return response, raw


# ── Per-item rollout ────────────────────────────────────────────────────────


def process_one(
    item: dict,
    *,
    out_root: str,
    skill_content: str,
    catalog: dict,
    judge_fn,
    judge_cache: JudgeCache,
    target_model: str = "",
    exec_timeout: int = 120,
    max_completion_tokens: int = 4096,
) -> dict:
    item_id = str(item["id"])
    pred_dir = os.path.join(out_root, "predictions", item_id)
    os.makedirs(pred_dir, exist_ok=True)

    result: dict = {
        "id": item_id,
        "hard": 0,
        "soft": 0.0,
        "n_turns": 1,
        "fail_reason": "",
        "task_type": "stop_slop",
        "task_description": "Rewrite prose to remove AI tells.",
        "predicted_answer": "",
        "question": item.get("prose_in", "")[:400],
        "reference_text": item.get("gold_rewrite", "") or "",
        "extras": {},
    }

    try:
        if is_target_exec_backend():
            # Prefer the inline-prompt path for Copilot CLI: pure-text
            # rewrites don't need workspace exploration, and bypassing the
            # workspace + the target-side prompt wrapper eliminates the
            # ~13% "no_rewrite_tag_in_response" failures observed in the
            # 2026-06-01 dry run (model spending its budget on shell tools).
            from skillopt.model.backend_config import get_target_backend

            if get_target_backend() == "copilot_cli_exec":
                response, raw = _run_inline_copilot_once(
                    pred_dir=pred_dir,
                    skill_content=skill_content,
                    item=item,
                    model=target_model,
                    timeout=exec_timeout,
                )
            else:
                response, raw = _run_exec_once(
                    pred_dir=pred_dir,
                    skill_content=skill_content,
                    item=item,
                    model=target_model,
                    timeout=exec_timeout,
                )
        else:
            system = build_system(skill_content)
            user = build_user(item)
            response, _usage = chat_target(
                system=system,
                user=user,
                max_completion_tokens=max_completion_tokens,
                timeout=exec_timeout,
            )
            raw = response

        rewrite, tag_found = extract_rewrite(response)
        if not tag_found:
            result["hard"] = 0
            result["soft"] = 0.0
            result["predicted_answer"] = ""
            result["fail_reason"] = "no_rewrite_tag_in_response"
            result["extras"] = {
                "raw_response": raw[:4000],
                "response_preview": (response or "")[:400],
            }
            with open(os.path.join(pred_dir, "prediction.json"), "w") as f:
                json.dump(
                    {
                        "item": item,
                        "rewrite": "",
                        "fail_reason": result["fail_reason"],
                        "response_preview": result["extras"]["response_preview"],
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            _write_conversation(pred_dir, item=item, rewrite="", graded=None, raw_response=raw)
            return result

        graded = grade(rewrite, item, catalog, judge_fn, judge_cache)
        result["hard"] = int(graded.hard)
        result["soft"] = float(graded.soft)
        result["predicted_answer"] = rewrite
        result["extras"] = {
            "diagnostics": graded.diagnostics,
            "raw_response": raw[:4000],
            "is_negative": bool(item.get("is_negative", False)),
        }

        with open(os.path.join(pred_dir, "prediction.json"), "w") as f:
            json.dump(
                {
                    "item": item,
                    "rewrite": rewrite,
                    "graded": {
                        "hard": graded.hard,
                        "soft": graded.soft,
                        "diagnostics": graded.diagnostics,
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        _write_conversation(pred_dir, item=item, rewrite=rewrite, graded=graded, raw_response=raw)
    except Exception as exc:  # noqa: BLE001
        result["fail_reason"] = f"{type(exc).__name__}: {exc}"
        result["extras"] = {"traceback": traceback.format_exc()[:4000]}

    return result


# ── Batch execution ─────────────────────────────────────────────────────────


def run_batch(
    *,
    items: list[dict],
    out_root: str,
    skill_content: str,
    catalog_path: str,
    target_model: str = "",
    exec_timeout: int = 120,
    max_completion_tokens: int = 4096,
    workers: int = 8,
    judge_cache: JudgeCache | None = None,
    judge_fn=None,
) -> list[dict]:
    """Run rollout on a batch of items in parallel; return list of result dicts.

    ``judge_fn``: optional override for the LLM-judge callable used by the
    grader. Defaults to ``make_optimizer_judge_fn()`` (production path).
    Tests and credential-free smoke runs can pass a stub.
    """
    catalog = load_catalog(catalog_path)
    if judge_fn is None:
        judge_fn = make_optimizer_judge_fn()
    if judge_cache is None:
        judge_cache = JudgeCache()

    results: list[dict] = [{} for _ in items]
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as ex:
        futures = {
            ex.submit(
                process_one,
                item,
                out_root=out_root,
                skill_content=skill_content,
                catalog=catalog,
                judge_fn=judge_fn,
                judge_cache=judge_cache,
                target_model=target_model,
                exec_timeout=exec_timeout,
                max_completion_tokens=max_completion_tokens,
            ): idx
            for idx, item in enumerate(items)
        }
        for fut in as_completed(futures):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as exc:  # noqa: BLE001
                results[idx] = {
                    "id": str(items[idx].get("id", f"idx_{idx}")),
                    "hard": 0,
                    "soft": 0.0,
                    "fail_reason": f"future_failed: {type(exc).__name__}: {exc}",
                }

    elapsed = time.time() - t0
    n_ok = sum(1 for r in results if not r.get("fail_reason"))
    print(
        f"  [stop_slop rollout] {len(items)} items in {elapsed:.1f}s "
        f"({n_ok} ok, {len(items) - n_ok} failed); "
        f"judge cache: hits={judge_cache.hits} misses={judge_cache.misses}"
    )
    return results
