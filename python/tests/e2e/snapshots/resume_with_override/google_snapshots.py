from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
My apologies! You are absolutely right to ask me to double-check.

I made a mistake in my previous answer. I am a large language model, trained by **Google**.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
You're right to ask me to double-check! My apologies for the confusion.

I am a large language model, trained by **Google**.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="I was created by Anthropic, an AI safety company. I'm Claude, an AI assistant developed by their team to be helpful, harmless, and honest."
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Yes, I can double-check that for you.

My previous answer is correct: I was created by **Anthropic**.

I am Claude, an AI assistant developed by Anthropic.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
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
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
You are absolutely right to ask me to double-check! My apologies for that error.

I am a large language model, trained by **Google**.\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
