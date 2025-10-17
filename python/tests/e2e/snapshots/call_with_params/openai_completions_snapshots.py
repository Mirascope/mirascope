from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:completions",
                "model_id": "gpt-4o",
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
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider="openai:completions",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "content": "4200 + 42 equals ",
                                "role": "assistant",
                                "annotations": [],
                            }
                        ],
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:completions)",
            "Skipping unsupported parameter: thinking=False (provider: openai:completions)",
        ],
    }
)
async_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:completions",
                "model_id": "gpt-4o",
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
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider="openai:completions",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "content": "4200 + 42 equals ",
                                "role": "assistant",
                                "annotations": [],
                            }
                        ],
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:completions)",
            "Skipping unsupported parameter: thinking=False (provider: openai:completions)",
        ],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:completions",
                "model_id": "gpt-4o",
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider="openai:completions",
                        model_id="gpt-4o",
                        raw_content=[],
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 9,
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:completions)",
            "Skipping unsupported parameter: thinking=False (provider: openai:completions)",
        ],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:completions",
                "model_id": "gpt-4o",
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals ")],
                        provider="openai:completions",
                        model_id="gpt-4o",
                        raw_content=[],
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 9,
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:completions)",
            "Skipping unsupported parameter: thinking=False (provider: openai:completions)",
        ],
    }
)
