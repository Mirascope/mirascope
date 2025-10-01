from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, a company focused on developing AI models and systems."
                    )
                ]
            ),
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
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, an AI safety and research company."
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
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(text="Yes, I can confirm that I was created by Anthropic.")
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 16,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(content=[Text(text="I was created by Anthropic.")]),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was developed by Anthropic, a company focused on creating safe and aligned AI models."
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 27,
    }
)
