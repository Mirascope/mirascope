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
                "provider": "anthropic-vertex",
                "model_id": "claude-haiku-4-5@20251001",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 = ")],
                        provider="anthropic",
                        model_id="claude-haiku-4-5@20251001",
                        raw_message={
                            "role": "assistant",
                            "content": [
                                {
                                    "citations": None,
                                    "text": "4200 + 42 = ",
                                    "type": "text",
                                }
                            ],
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": ["Skipping unsupported parameter: seed=42 (provider: anthropic)"],
    }
)
