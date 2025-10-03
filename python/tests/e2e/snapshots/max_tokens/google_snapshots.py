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
        "model_id": "gemini-2.5-flash",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "thinking_signatures": [],
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[Text(text="Here is a list of all 50 U.S. states:")]
            ),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "thinking_signatures": [],
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are all 50 U.S. states:

1\
"""
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(content=[Text(text="Here are all 50 U.S. states in")]),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(content=[Text(text="Here is a list of all 50 U.S")]),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
