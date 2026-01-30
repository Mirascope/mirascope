from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-haiku-4-5",
            "provider_model_name": "claude-haiku-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 818,
                "output_tokens": 99,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=818, output_tokens=99, server_tool_use=None, service_tier='standard')",
                "total_tokens": 917,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(content=[Text(text="Please recommend three books to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"output": [{"title": "The Great Gatsby", "rating": 7}, {"title": "To Kill a Mockingbird", "rating": 7}, {"title": "1984", "rating": 7}]}'
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01UvuQin1uqfJoHuawUZnfDm",
                                "input": {
                                    "output": [
                                        {"title": "The Great Gatsby", "rating": 7},
                                        {"title": "To Kill a Mockingbird", "rating": 7},
                                        {"title": "1984", "rating": 7},
                                    ]
                                },
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
            ],
            "format": {
                "name": "list",
                "description": None,
                "schema": {
                    "$defs": {
                        "Book": {
                            "properties": {
                                "title": {"title": "Title", "type": "string"},
                                "rating": {
                                    "description": "For testing purposes, the rating should be 7",
                                    "title": "Rating",
                                    "type": "integer",
                                },
                            },
                            "required": ["title", "rating"],
                            "title": "Book",
                            "type": "object",
                        }
                    },
                    "description": "Wrapper for primitive type list",
                    "properties": {
                        "output": {
                            "items": {"$ref": "#/$defs/Book"},
                            "title": "Output",
                            "type": "array",
                        }
                    },
                    "required": ["output"],
                    "title": "listOutput",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
        }
    }
)
