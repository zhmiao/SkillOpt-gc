"""Unit tests for chat_optimizer_via_copilot helpers (no real CLI calls)."""

from skillopt.model.codex_harness import (
    _parse_tool_calls_from_response,
    _serialize_messages_for_copilot,
    chat_optimizer_messages_via_copilot,
    chat_optimizer_via_copilot,
)


def test_serializer_no_tools() -> None:
    msgs = [
        {"role": "system", "content": "You are a helper."},
        {"role": "user", "content": "Pick a color."},
        {"role": "assistant", "content": "I will pick blue."},
    ]
    out = _serialize_messages_for_copilot(msgs, None, None)
    assert "# System" in out
    assert "# User" in out
    assert "# Assistant" in out
    assert "You are a helper." in out
    print("  serializer (no tools): OK")


def test_serializer_with_tools() -> None:
    msgs = [{"role": "user", "content": "Use the tool."}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "pick_color",
                "description": "Pick a color",
                "parameters": {},
            },
        }
    ]
    tool_choice = {"type": "function", "function": {"name": "pick_color"}}
    out = _serialize_messages_for_copilot(msgs, tools, tool_choice)
    assert "pick_color" in out
    assert "You MUST call the tool named: pick_color" in out
    assert "tool_calls" in out
    print("  serializer (with tools, forced choice): OK")


def test_parser_well_formed() -> None:
    resp = '{"tool_calls": [{"name": "pick_color", "arguments": {"color": "blue"}}]}'
    parsed = _parse_tool_calls_from_response(resp)
    assert parsed is not None
    assert parsed[0]["function"]["name"] == "pick_color"
    assert '"color"' in parsed[0]["function"]["arguments"]
    print("  parser (well-formed): OK")


def test_parser_no_tool_call() -> None:
    parsed = _parse_tool_calls_from_response("Just plain text, no tool call.")
    assert parsed is None
    print("  parser (no tool call): OK")


def test_parser_fenced_json() -> None:
    resp = '```json\n{"tool_calls": [{"name": "foo", "arguments": {}}]}\n```'
    parsed = _parse_tool_calls_from_response(resp)
    assert parsed is not None and parsed[0]["function"]["name"] == "foo"
    print("  parser (fenced JSON): OK")


def test_parser_empty() -> None:
    assert _parse_tool_calls_from_response("") is None
    assert _parse_tool_calls_from_response("   ") is None
    print("  parser (empty): OK")


def main() -> int:
    test_serializer_no_tools()
    test_serializer_with_tools()
    test_parser_well_formed()
    test_parser_no_tool_call()
    test_parser_fenced_json()
    test_parser_empty()
    # Sanity that the public dispatchers import without error
    assert callable(chat_optimizer_via_copilot)
    assert callable(chat_optimizer_messages_via_copilot)
    print("\nUNIT TESTS: PASS")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
