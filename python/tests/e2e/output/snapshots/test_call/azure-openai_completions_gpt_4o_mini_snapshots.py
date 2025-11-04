from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": "4200 + 42 equals 4242.",
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
async_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message={
                        "content": "4200 + 42 equals 4242.",
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
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 12,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:completions",
            "model_id": "gpt-4o-mini",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:completions",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 12,
        }
    }
)
