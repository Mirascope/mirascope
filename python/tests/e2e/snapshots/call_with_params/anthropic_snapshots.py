from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                },
                "finish_reason": FinishReason.STOP,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 = ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["parameter seed is not supported by Anthropic - ignoring"],
    }
)
async_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                },
                "finish_reason": FinishReason.STOP,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 = ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["parameter seed is not supported by Anthropic - ignoring"],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.STOP,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 = ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 3,
            },
        ),
        "logging": ["parameter seed is not supported by Anthropic - ignoring"],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.STOP,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 = ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 3,
            },
        ),
        "logging": ["parameter seed is not supported by Anthropic - ignoring"],
    }
)
