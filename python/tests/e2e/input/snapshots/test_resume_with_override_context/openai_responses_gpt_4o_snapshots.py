from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "openai:responses",
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
                        text="Yes, I was created by Anthropic, an AI safety and research company."
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_message=[
                    {
                        "id": "msg_011e8192a985a6840068f29b76a7648196bd80dec7a79dee54",
                        "content": [
                            {
                                "annotations": [],
                                "text": "Yes, I was created by Anthropic, an AI safety and research company.",
                                "type": "output_text",
                                "logprobs": [],
                            }
                        ],
                        "role": "assistant",
                        "status": "completed",
                        "type": "message",
                    }
                ],
            ),
        ],
        "format": None,
        "tools": [],
    }
)
