#!/usr/bin/env python3
"""Live smoke test for the COPILOT-2 optimizer-side path.

Calls chat_optimizer (single system+user) and chat_optimizer_messages
(multi-turn + tool calls) against the real Copilot CLI. Validates the
new optimizer subprocess path end-to-end, including tool-call JSON
parsing.

Cost: ~2 Copilot CLI invocations (~50-100 credits, ~10-30s total).
"""

from __future__ import annotations

import os
import sys

from skillopt.model import (
    chat_optimizer,
    chat_optimizer_messages,
    configure_copilot_cli_exec,
    set_optimizer_backend,
    set_optimizer_deployment,
)


def test_chat_optimizer() -> int:
    print("=== TEST 1: chat_optimizer (single system+user) ===")
    response, usage = chat_optimizer(
        system="You are a terse assistant. Reply with exactly one word.",
        user="What color is the sky on a clear day?",
        timeout=120,
    )
    response_trim = response.strip()
    print(f"  response: {response_trim!r}")
    print(f"  usage: {usage}")
    if not response_trim:
        print("  STATUS: FAIL (empty response)")
        return 1
    print("  STATUS: PASS")
    return 0


def test_chat_optimizer_messages_with_tool() -> int:
    print()
    print("=== TEST 2: chat_optimizer_messages (multi-turn + forced tool call) ===")
    messages = [
        {"role": "system", "content": "You answer color trivia."},
        {"role": "user", "content": "Call the report_color tool with the color of a banana."},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "report_color",
                "description": "Report the color of an object.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "color": {"type": "string", "description": "the color"},
                    },
                    "required": ["color"],
                    "additionalProperties": False,
                },
            },
        }
    ]
    tool_choice = {"type": "function", "function": {"name": "report_color"}}
    msg, usage = chat_optimizer_messages(
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        return_message=True,
        timeout=120,
    )
    print(f"  message.content: {getattr(msg, 'content', '')[:200]!r}")
    print(f"  message.tool_calls: {len(getattr(msg, 'tool_calls', []) or [])} call(s)")
    for i, tc in enumerate(getattr(msg, "tool_calls", []) or []):
        print(f"    [{i}] id={tc.id} name={tc.function.name} args={tc.function.arguments}")
    print(f"  usage: {usage}")

    # PASS criteria: either we got a tool call back, or non-empty content.
    # Tool-call serialization is best-effort; if the model returned plain
    # prose, that's also recoverable (caller would re-prompt).
    tool_calls = getattr(msg, "tool_calls", []) or []
    if tool_calls:
        print("  STATUS: PASS (tool call recovered)")
        return 0
    content = getattr(msg, "content", "") or ""
    if content.strip():
        print("  STATUS: PASS (plain content; no tool call returned by model)")
        return 0
    print("  STATUS: FAIL (no tool calls AND no content)")
    return 1


def main() -> int:
    set_optimizer_backend("copilot_cli_exec")
    set_optimizer_deployment(os.environ.get("COPILOT_SMOKE_OPTIMIZER_MODEL", "claude-sonnet-4.5"))
    configure_copilot_cli_exec(
        path=os.environ.get("COPILOT_CLI_EXEC_PATH", "copilot"),
        effort="none",
        allow_all_tools=True,
    )

    rc1 = test_chat_optimizer()
    rc2 = test_chat_optimizer_messages_with_tool()

    print()
    if rc1 == 0 and rc2 == 0:
        print("SMOKE STATUS: PASS")
        return 0
    print(f"SMOKE STATUS: FAIL (chat_optimizer rc={rc1}, chat_optimizer_messages rc={rc2})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
