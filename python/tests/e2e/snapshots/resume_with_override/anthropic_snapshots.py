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
        "thinking_signatures": [],
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I am a large language model, trained by Google.")]
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="You're absolutely right to ask me to double-check that. I made an error - I was created by Anthropic, not Google. Thank you for the correction!"
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
        "thinking_signatures": [],
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I am a large language model, trained by Google.")]
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="You're absolutely right to ask me to double-check that. I made an error - I am Claude, and I was created by Anthropic, not Google. Thank you for the correction!"
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
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I am a large language model, trained by Google.")]
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="You're absolutely right to ask me to double-check that. I made an error - I am Claude, and I was created by Anthropic, not Google. Thank you for the correction!"
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 7,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I am a large language model, trained by Google.")]
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="You're absolutely right - I apologize for the error. I am Claude, an AI assistant created by Anthropic. Thank you for prompting me to correct that mistake."
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 6,
    }
)
