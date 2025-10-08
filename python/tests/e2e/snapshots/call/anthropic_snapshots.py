from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242")]),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242")]),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242")]),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242")]),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
