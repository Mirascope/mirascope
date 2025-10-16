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
                content=[Text(text="The sum of 4200 and 42 is 4242.")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0614dcd6b70956660068e70508f3ec8195802d1160f635dc2d",
                        "content": [
                            {
                                "annotations": [],
                                "text": "The sum of 4200 and 42 is 4242.",
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
                        "id": "msg_0bd5699b93d837ab0068e7050a737081909673651d9fd6e8c6",
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
                content=[Text(text="4200 + 42 = 4242")],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_68daff03617c819393014d1750b636a70db3d44e8379eace",
                        "content": [
                            {
                                "annotations": [],
                                "text": "4200 + 42 = 4242",
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
        "n_chunks": 11,
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
                        "id": "msg_68daff05faf08196821592950863f6470f51c699b4637947",
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
