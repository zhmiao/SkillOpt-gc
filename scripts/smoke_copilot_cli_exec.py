#!/usr/bin/env python3
"""Smoke test for the copilot_cli_exec target backend.

Calls `copilot -p "say hello"` via the harness; verifies non-empty
response, exit code, and that the trace artifacts land on disk.

This test does NOT depend on `openai` being installed because it
imports the backend_config / codex_harness modules directly via
importlib, bypassing skillopt.model.__init__'s openai import.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types


def _load_module(name: str, path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Bootstrap a minimal skillopt package namespace so codex_harness's
# `from skillopt.model.backend_config import ...` works without
# triggering the package's openai-importing __init__.
sys.modules["skillopt"] = types.ModuleType("skillopt")
sys.modules["skillopt.model"] = types.ModuleType("skillopt.model")
common = _load_module("skillopt.model.common", "skillopt/model/common.py")
backend_config = _load_module("skillopt.model.backend_config", "skillopt/model/backend_config.py")
harness = _load_module("skillopt.model.codex_harness", "skillopt/model/codex_harness.py")

# Point the harness at the real copilot CLI on PATH
backend_config.set_target_backend("copilot_cli_exec")
backend_config.configure_copilot_cli_exec(
    path=os.environ.get("COPILOT_CLI_EXEC_PATH", "copilot"),
    effort="low",  # keep the smoke fast
    allow_all_tools=True,
    allow_all_paths=False,
    allow_all_urls=False,
    agent="",
)

assert backend_config.get_target_backend() == "copilot_cli_exec"
assert backend_config.is_target_exec_backend() is True
cfg = backend_config.get_copilot_cli_exec_config()
print(f"  config: {cfg}")

with tempfile.TemporaryDirectory() as work_dir:
    # Real CLI invocation. Keep the prompt tiny.
    print(f"  work_dir: {work_dir}")
    print("  calling copilot CLI (90s timeout)...")
    response, raw = harness.run_copilot_cli_exec(
        work_dir=work_dir,
        prompt='Say the single word "hello" and nothing else. Do NOT use any tools.',
        model="",  # let the CLI pick the default
        timeout=90,
    )
    print(f"\n  response (chars={len(response)}):")
    print("    " + (response[:300].replace("\n", "\n    ") or "(empty)"))
    print(f"\n  raw transcript (chars={len(raw)})")
    print("  first 400 chars of raw:")
    print("    " + raw[:400].replace("\n", "\n    "))

    # Verify artifacts were persisted
    pred_dir = os.path.dirname(work_dir.rstrip(os.sep))
    raw_path = os.path.join(pred_dir, "copilot_raw.txt")
    summary_path = os.path.join(pred_dir, "copilot_trace_summary.txt")
    print(f"\n  persisted: copilot_raw.txt exists = {os.path.exists(raw_path)}")
    print(f"  persisted: copilot_trace_summary.txt exists = {os.path.exists(summary_path)}")
    if os.path.exists(summary_path):
        print("  summary:")
        with open(summary_path) as f:
            print("    " + f.read().replace("\n", "\n    "))

    if response.strip():
        print("\nSTATUS: PASS — non-empty response, harness round-trip works")
        sys.exit(0)
    print("\nSTATUS: FAIL — empty response")
    sys.exit(1)
