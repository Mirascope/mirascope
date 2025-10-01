from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(content=[Text(text="I was indeed created by Anthropic!")]),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(content=[Text(text="Yes, I was created by Anthropic.")]),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[Text(text="Yes, I was indeed created by Anthropic.")]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 12,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[Text(text="Yep, I was indeed created by Anthropic.")]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 12,
    }
)
