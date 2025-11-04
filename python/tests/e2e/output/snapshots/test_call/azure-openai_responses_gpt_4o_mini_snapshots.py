from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0f97d91745cbcb7800690c21743d888190b9b5f064c23e03af",
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
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_03ad827fa9fb69c900690c2176ed2c8193919b3e1776f73aa8",
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
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0ef4c09315bcd6d800690c217879d88190b4b5f56574f5f8d1",
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
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0326378503895f4100690c217c423081908f2ac3b3183d5eef",
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
        }
    }
)
