from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Answer this question: What is 2 + 3, using the custom addition tool?"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="toolu_01GWMYVRPdJWuP8ywu1XZDW8",
                            name="customAdditionImplementation",
                            args='{"a": 2, "b": 3}',
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_01GWMYVRPdJWuP8ywu1XZDW8",
                                "name": "customAdditionImplementation",
                                "input": {"a": 2, "b": 3},
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01GWMYVRPdJWuP8ywu1XZDW8",
                            name="customAdditionImplementation",
                            result=13,
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(text='{"integer_a": 2, "integer_b": 3, "answer": 13}')
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": '{"integer_a": 2, "integer_b": 3, "answer": 13}',
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "IntegerAdditionResponse",
                "description": "A simple response for testing.",
                "schema": {
                    "description": "A simple response for testing.",
                    "properties": {
                        "integer_a": {"title": "Integer A", "type": "integer"},
                        "integer_b": {"title": "Integer B", "type": "integer"},
                        "answer": {"title": "Answer", "type": "integer"},
                    },
                    "required": ["integer_a", "integer_b", "answer"],
                    "title": "IntegerAdditionResponse",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "customAdditionImplementation",
                    "description": "Perform computation on integers.",
                    "parameters": """\
{
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    },
    "b": {
      "title": "B",
      "type": "integer"
    }
  },
  "required": [
    "a",
    "b"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 939,
                "output_tokens": 25,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 964,
            },
            "n_chunks": 6,
        }
    }
)
