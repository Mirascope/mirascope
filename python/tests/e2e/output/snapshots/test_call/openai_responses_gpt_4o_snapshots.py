from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[Text(text="4200 + 42 is 4242.")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0dd4d7c7953cdc350068f2974a56b081908ae3b07c4d73c2d7",
                        "content": [
                            {
                                "annotations": [],
                                "text": "4200 + 42 is 4242.",
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
)
async_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[Text(text="4200 + 42 equals 4242.")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0c9b1376dac632050068f2974ff7b88196befe9451216b2bf0",
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
)
stream_snapshot = snapshot(
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
                        "id": "msg_0a457f78f810604b0068f29756e5d4819781bffda073f1c224",
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
)
async_stream_snapshot = snapshot(
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
                        "id": "msg_01c3c1bd01a071710068f2975bb39c81978b53bd51c43b4c69",
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
)
