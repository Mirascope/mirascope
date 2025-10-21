from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
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
                    raw_message=[
                        {
                            "id": "msg_0bee99a5de5b12910068f966a1fb3c819587e157227fc327ff",
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
                    raw_message=[
                        {
                            "id": "msg_03b14221ccca5c620068f966a3948881958dafb416da3a7122",
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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0360bd45725b0a010068f966a601b081958e95c4085b086532",
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
            "provider": "openai:responses",
            "model_id": "gpt-4o",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 equals 4242.")],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_05aee6862dd20adc0068f966a7b06481939ce80dfccd63051e",
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
