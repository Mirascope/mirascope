from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:responses",
                "model_id": "gpt-4o",
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
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider="openai:responses",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "id": "msg_01494efc7f3e9c250068e6fd9f8784819097461e6defecaccd",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: openai:responses with model_id: gpt-4o)",
        ],
    }
)
async_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:responses",
                "model_id": "gpt-4o",
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
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider="openai:responses",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "id": "msg_002a8e2b9b9734d10068e6fda2dc9c819081a4743049f00820",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: openai:responses with model_id: gpt-4o)",
        ],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:responses",
                "model_id": "gpt-4o",
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider="openai:responses",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "id": "msg_0a272ac95e6c35680068e6fda1887c81958cb45ff13f06ace2",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
                "n_chunks": 12,
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: openai:responses with model_id: gpt-4o)",
        ],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "openai:responses",
                "model_id": "gpt-4o",
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider="openai:responses",
                        model_id="gpt-4o",
                        raw_content=[
                            {
                                "id": "msg_098276e4691db86a0068e6fda5d0b0819089f6a1c6942a7539",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
                "n_chunks": 12,
            },
        ),
        "logging": [
            "Skipping unsupported parameter: top_k=50 (provider: openai:responses)",
            "Skipping unsupported parameter: seed=42 (provider: openai:responses)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai:responses)",
            "Skipping unsupported parameter: thinking=False (provider: openai:responses with model_id: gpt-4o)",
        ],
    }
)
