from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {"thinking": False},
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=(Text(text="What is the 100th fibonacci number?"),)
                ),
                AssistantMessage(
                    content=(
                        Thought(thought="[anthropic thinking]"),
                        Text(text="[xai assistant text]"),
                        ToolCall(
                            id="[anthropic tool id]",
                            name="compute_fib",
                            args="[anthropic tool input]",
                        ),
                    ),
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "signature": "[anthropic signature]",
                                "thinking": "[anthropic thinking]",
                                "type": "thinking",
                            },
                            {
                                "citations": None,
                                "text": "[xai assistant text]",
                                "type": "text",
                            },
                            {
                                "id": "[anthropic tool id]",
                                "input": "[anthropic tool input]",
                                "name": "compute_fib",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="compute_fib",
                            value="218922995834555169026",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "compute_fib",
                    "description": "Compute the nth Fibonacci number (1-indexed).",
                    "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
