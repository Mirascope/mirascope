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
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                },
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["parameter top_k is not supported by OpenAI - ignoring"],
    }
)
async_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai",
                "model_id": "gpt-4o",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                },
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": ["parameter top_k is not supported by OpenAI - ignoring"],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 10,
            },
        ),
        "logging": ["parameter top_k is not supported by OpenAI - ignoring"],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai",
                "model_id": "gpt-4o",
                "finish_reason": FinishReason.END_TURN,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(content=[Text(text="4200 + 42 equals ")]),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 10,
            },
        ),
        "logging": ["parameter top_k is not supported by OpenAI - ignoring"],
    }
)
