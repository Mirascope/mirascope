from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai:completions",
            "model_id": "openai/gpt-4o-mini",
            "provider_model_name": "gpt-4o-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 9,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "messages": [
                UserMessage(content=[Text(text="Say hello")]),
                AssistantMessage(
                    content=[Text(text="Hello! How can I assist you today?")],
                    provider_id="openai:completions",
                    model_id="openai/gpt-4o-mini",
                    provider_model_name="gpt-4o-mini:completions",
                    raw_message={
                        "content": "Hello! How can I assist you today?",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
