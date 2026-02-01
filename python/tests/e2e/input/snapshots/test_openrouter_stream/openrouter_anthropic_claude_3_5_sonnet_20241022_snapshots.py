from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openrouter",
            "model_id": "openrouter/anthropic/claude-3-5-sonnet-20241022",
            "provider_model_name": "anthropic/claude-3-5-sonnet-20241022",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Say hello in one word")]),
                AssistantMessage(
                    content=[Text(text="Hello!")],
                    provider_id="openrouter",
                    model_id="openrouter/anthropic/claude-3-5-sonnet-20241022",
                    provider_model_name="anthropic/claude-3-5-sonnet-20241022",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 12,
                "output_tokens": 5,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 17,
            },
            "n_chunks": 3,
        }
    }
)
