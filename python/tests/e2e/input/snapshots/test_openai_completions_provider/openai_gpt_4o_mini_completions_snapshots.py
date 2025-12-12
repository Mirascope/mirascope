from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai:completions",
            "model_id": "openai/gpt-4o-mini:completions",
            "provider_model_name": "gpt-4o-mini:completions",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Say hello")]),
                AssistantMessage(
                    content=[Text(text="Hello! How can I assist you today?")],
                    provider_id="openai:completions",
                    model_id="openai/gpt-4o-mini:completions",
                    provider_model_name="gpt-4o-mini:completions",
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
