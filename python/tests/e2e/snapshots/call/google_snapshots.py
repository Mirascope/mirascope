from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242\n")]),
        ],
        "format_type": None,
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242\n")]),
        ],
        "format_type": None,
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242\n")]),
        ],
        "format_type": None,
        "n_chunks": 5,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(content=[Text(text="4200 + 42 = 4242\n")]),
        ],
        "format_type": None,
        "n_chunks": 5,
    }
)
