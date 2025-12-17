from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider_id": "openai",
                "model_id": "openai/gpt-4o:completions",
                "provider_model_name": "gpt-4o:completions",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "usage": {
                    "input_tokens": 16,
                    "output_tokens": 9,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "reasoning_tokens": 0,
                },
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider_id="openai",
                        model_id="openai/gpt-4o:completions",
                        provider_model_name="gpt-4o:completions",
                        raw_message={
                            "content": "4200 + 42 equals ",
                            "role": "assistant",
                            "annotations": [],
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: openai)",
            "Skipping unsupported parameter: thinking=False (provider: openai)",
        ],
    }
)
