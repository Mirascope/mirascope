from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "openai",
            "model_id": "openai/gpt-4o",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[Text(text="Hello! How can I assist you today?")],
                    provider="openai",
                    model_id="openai/gpt-4o",
                    raw_message={
                        "content": "Hello! How can I assist you today?",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
