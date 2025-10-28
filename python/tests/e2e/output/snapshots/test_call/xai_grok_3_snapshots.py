from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=(Text(text="What is 4200 + 42?"),)),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=(Text(text="What is 4200 + 42?"),)),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                UserMessage(content=(Text(text="What is 4200 + 42?"),)),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": "variable",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                UserMessage(content=(Text(text="What is 4200 + 42?"),)),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": "variable",
        }
    }
)
