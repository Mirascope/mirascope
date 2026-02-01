from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-haiku-4-5",
            "provider_model_name": "claude-haiku-4-5",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 = 4242")],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [{"type": "text", "text": "4200 + 42 = 4242"}],
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 17,
                "output_tokens": 15,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 32,
            },
            "n_chunks": 4,
        }
    }
)
