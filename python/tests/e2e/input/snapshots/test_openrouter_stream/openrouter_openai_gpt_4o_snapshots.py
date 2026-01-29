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
            "model_id": "openrouter/openai/gpt-4o",
            "provider_model_name": "openai/gpt-4o",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Say hello in one word")]),
                AssistantMessage(
                    content=[Text(text="Hello!")],
                    provider_id="openrouter",
                    model_id="openrouter/openai/gpt-4o",
                    provider_model_name="openai/gpt-4o",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 12,
                "output_tokens": 2,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 14,
            },
            "n_chunks": 4,
        }
    }
)
