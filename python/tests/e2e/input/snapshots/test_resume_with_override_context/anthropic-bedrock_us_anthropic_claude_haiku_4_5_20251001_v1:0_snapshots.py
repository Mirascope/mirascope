from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                        text="Yes, I've double-checked and can confirm: I was created by Anthropic, an AI safety company. Anthropic built me to be helpful, harmless, and honest. Is there something specific you'd like to know about Anthropic or how I was created?"
                    )
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": "Yes, I've double-checked and can confirm: I was created by Anthropic, an AI safety company. Anthropic built me to be helpful, harmless, and honest. Is there something specific you'd like to know about Anthropic or how I was created?",
                            "type": "text",
                        }
                    ],
                },
            ),
        ],
        "format": None,
        "tools": [],
    }
)
