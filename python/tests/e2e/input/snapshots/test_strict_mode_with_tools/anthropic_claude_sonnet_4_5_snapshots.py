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
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 939,
                "output_tokens": 25,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=939, output_tokens=25, server_tool_use=None, service_tier='standard')",
                "total_tokens": 964,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Answer this question: What is 2 + 3, using the custom addition tool??"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="toolu_01AZ4GPmus1WZnerDUvvTLHG",
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
                                "id": "toolu_01AZ4GPmus1WZnerDUvvTLHG",
                                "input": {"a": 2, "b": 3},
                                "name": "customAdditionImplementation",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01AZ4GPmus1WZnerDUvvTLHG",
                            name="customAdditionImplementation",
                            value=13,
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
                                "text": '{"integer_a": 2, "integer_b": 3, "answer": 13}',
                                "type": "text",
                                "parsed_output": {
                                    "integer_a": 2,
                                    "integer_b": 3,
                                    "answer": 13,
                                },
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
                    "strict": False,
                }
            ],
        }
    }
)
