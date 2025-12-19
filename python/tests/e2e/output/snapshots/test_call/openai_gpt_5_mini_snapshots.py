from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 8,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=15, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=8, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=23)",
                "total_tokens": 23,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0d7cde5746e448a00069492cd604a081909ca5bc3f75e2e4aa",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0d7cde5746e448a00069492cd6831c819083b2d7b4be8fbbde",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "4242",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 8,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=15, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=8, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=23)",
                "total_tokens": 23,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0ba1cccede5b4d340069492df109b481969a479f35a791ffee",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0ba1cccede5b4d340069492df179408196b87b2bf66cb2b251",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "4242",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
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
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0bc2488d91902e550069492df330ec819090b954c3c1f65cae",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0bc2488d91902e550069492df430048190be11d75813c2e23a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "4242",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 72,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 64,
                "raw": "None",
                "total_tokens": 87,
            },
            "n_chunks": 4,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_06849d5de77b1b000069492df598b481969338f5911753d22e",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_06849d5de77b1b000069492df62fd08196bcf547e1748bee4c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "4242",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 8,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 23,
            },
            "n_chunks": 4,
        }
    }
)
