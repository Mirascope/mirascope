from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "xai",
                "model_id": "grok-3",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=(Text(text="What is 4200 + 42?"),)),
                    AssistantMessage(
                        content=(Text(text="[xai assistant text]"),),
                        provider="xai",
                        model_id="grok-3",
                        raw_message={
                            "content": [
                                {"type": "text", "text": "[xai assistant text]"}
                            ]
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        )
    }
)
