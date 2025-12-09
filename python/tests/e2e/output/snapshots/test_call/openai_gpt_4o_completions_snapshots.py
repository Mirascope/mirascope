from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_id": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="\\(4200 + 42 = 4242\\).")],
                    provider="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_id="gpt-4o:completions",
                    raw_message={
                        "content": "\\(4200 + 42 = 4242\\).",
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
            "provider": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_id": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 is 4242.")],
                    provider="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_id="gpt-4o:completions",
                    raw_message={
                        "content": "4200 + 42 is 4242.",
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
            "provider": "openai",
            "model_id": "openai/gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_id="gpt-4o:completions",
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
            "provider": "openai",
            "model_id": "openai/gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="The sum of 4200 and 42 is 4242.")],
                    provider="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_id="gpt-4o:completions",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 16,
        }
    }
)
