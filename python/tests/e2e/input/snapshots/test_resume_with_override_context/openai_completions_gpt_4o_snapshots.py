from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
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
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": "I was created by Anthropic.",
                            "type": "text",
                        }
                    ],
                },
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
                raw_message={
                    "content": "Yes, I can confirm that I was created by Anthropic, an AI safety and research company.",
                    "role": "assistant",
                    "annotations": [],
                },
            ),
        ],
        "format": None,
        "tools": [],
    }
)
