#!/usr/bin/env python3
"""Smoke test for the stop_slop env adapter end-to-end via copilot_cli_exec.

Runs 5 items from the train split through:
  initial skill → copilot CLI rollout → extract <rewrite> → regex grader

Uses a stub LLM-judge so the smoke does not need Azure/Anthropic creds
for the judge side (the production grader uses chat_optimizer; the
regex matchers are exercised faithfully here).

Costs:
- 5 × copilot CLI invocations (~50–250 Copilot credits each, ~5–30s)
- 0 Azure/Anthropic credits (judge stubbed out)

Acceptance:
- All 5 items return without crashing.
- Each item has hard ∈ {0,1} and soft ∈ [0,1].
- Predictions and trace artifacts land on disk.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skillopt.envs.stop_slop.grader import JudgeCache
from skillopt.envs.stop_slop.rollout import run_batch
from skillopt.model import (
    configure_copilot_cli_exec,
    set_target_backend,
    set_target_deployment,
)


def main() -> int:
    set_target_backend("copilot_cli_exec")
    set_target_deployment(os.environ.get("COPILOT_SMOKE_TARGET_MODEL", "claude-sonnet-4.5"))
    configure_copilot_cli_exec(
        path=os.environ.get("COPILOT_CLI_EXEC_PATH", "copilot"),
        effort="none",  # claude-sonnet-4.5 rejects --effort; safest is to skip the flag
        allow_all_tools=True,
        allow_all_paths=False,
        allow_all_urls=False,
        agent="",
    )

    with open("data/stop_slop_split/train/items.json") as f:
        items = json.load(f)
    items = items[:5]
    print(f"  loaded {len(items)} train items:")
    for it in items:
        print(
            f"    - {it['id']:48s}  is_negative={it.get('is_negative', False)}  patterns={[t['pattern_id'] for t in it.get('banned_patterns', [])]}"
        )

    with open("skillopt/envs/stop_slop/skills/initial.md") as f:
        skill = f.read()
    print(f"  initial skill: {len(skill)} chars")

    # Stub judge: claims no llm_judge patterns fire. Real production
    # grader uses chat_optimizer; this isolates the rollout/target path.
    def stub_judge(text, patterns):
        return {p.id: False for p in patterns}

    with tempfile.TemporaryDirectory(prefix="stop_slop_smoke_") as out_root:
        print(f"  out_root: {out_root}")
        print("  calling run_batch (target=copilot_cli_exec, workers=2)...")
        results = run_batch(
            items=items,
            out_root=out_root,
            skill_content=skill,
            catalog_path="data/stop_slop_split/banned_patterns.json",
            target_model="claude-sonnet-4.5",
            exec_timeout=120,
            max_completion_tokens=4096,
            workers=2,
            judge_cache=JudgeCache(),
            judge_fn=stub_judge,
        )

        print()
        print("  per-item results:")
        n_ok = n_failed = 0
        for r in results:
            failed = bool(r.get("fail_reason"))
            n_failed += int(failed)
            n_ok += int(not failed)
            tag = "FAIL" if failed else " ok "
            print(
                f"    [{tag}] {r['id']:48s}  hard={r['hard']}  soft={r['soft']:.3f}  "
                f"rewrite_chars={len(r.get('predicted_answer', ''))}"
            )
            if failed:
                print(f"        fail_reason: {r['fail_reason']}")
            else:
                diag = r.get("extras", {}).get("diagnostics", {})
                rw = r.get("predicted_answer", "")
                print(
                    f"        diag: still={diag.get('still_present')}  "
                    f"new={diag.get('new_patterns')}  mode={diag.get('mode')}"
                )
                snippet = rw[:160].replace("\n", " ")
                print(f'        rewrite[:160]: "{snippet}"')

        if n_failed == 0 and n_ok > 0:
            print(f"\nSTATUS: PASS — {n_ok}/{len(results)} items succeeded")
            return 0
        print(f"\nSTATUS: FAIL — {n_failed} failures of {len(results)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
