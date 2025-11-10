from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=(Text(text="Who created you?"),)),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="anthropic",
                    model_id="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "[xai assistant text]",
                                "type": "text",
                            }
                        ],
                    },
                ),
                UserMessage(content=(Text(text="Can you double-check that?"),)),
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
