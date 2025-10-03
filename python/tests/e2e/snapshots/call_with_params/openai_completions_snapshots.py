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
                },
                "finish_reason": None,
                "thinking_signatures": [],
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["Skipping unsupported parameter: top_k=50 for provider OpenAI"],
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
                },
                "finish_reason": None,
                "thinking_signatures": [],
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["Skipping unsupported parameter: top_k=50 for provider OpenAI"],
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
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 9,
            },
        ),
        "logging": ["Skipping unsupported parameter: top_k=50 for provider OpenAI"],
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
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 9,
            },
        ),
        "logging": ["Skipping unsupported parameter: top_k=50 for provider OpenAI"],
    }
)
