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
            "provider_model_id": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="Hello! It looks like your message might be incomplete. How can I assist you today?"
                        )
                    ],
                    provider="openai",
                    model_id="openai/gpt-4o",
                    provider_model_id="gpt-4o:completions",
                    raw_message={
                        "content": "Hello! It looks like your message might be incomplete. How can I assist you today?",
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
