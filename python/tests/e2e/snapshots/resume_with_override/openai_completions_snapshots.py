from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, a company focused on developing advanced AI models."
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "content": "Yes, I can confirm that I was created by Anthropic, a company focused on developing advanced AI models.",
                        "role": "assistant",
                        "annotations": [],
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "citations": None,
                        "text": "I was created by Anthropic.",
                        "type": "text",
                    }
                ],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, an AI safety and research company."
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "content": "Yes, I can confirm that I was created by Anthropic, an AI safety and research company.",
                        "role": "assistant",
                        "annotations": [],
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, a company focused on developing advanced AI models and ensuring their alignment with human values and safety."
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 33,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[{"type": "text", "text": "I was created by Anthropic."}],
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="Yes, I can confirm that I was created by Anthropic, an AI safety and research company."
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 22,
    }
)
