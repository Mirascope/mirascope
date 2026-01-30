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
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 32,
                "output_tokens": 1159,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 1152,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=32, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=1159, output_tokens_details=OutputTokensDetails(reasoning_tokens=1152), total_tokens=1191)",
                "total_tokens": 1191,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_085d300305cb9e0f00696aefb6042481968e79bd97da8920f0",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_085d300305cb9e0f00696aefc6a27081969e5e73c231e5be1d",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
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
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "params": {"thinking": {"level": "medium", "include_thoughts": False}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 32,
                "output_tokens": 1287,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 1280,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=32, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=1287, output_tokens_details=OutputTokensDetails(reasoning_tokens=1280), total_tokens=1319)",
                "total_tokens": 1319,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_05dbc5316d1fcc3100696af01c615c81969031391e23c74b37",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_05dbc5316d1fcc3100696af02c68fc8196b01531821357a5ba",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
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
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_00be767a684ac49d00696aefefbda881949385c2abc3a0a1c0",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_00be767a684ac49d00696aeff84d348194900f2557198e218d",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
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
                "input_tokens": 32,
                "output_tokens": 647,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 679,
            },
            "n_chunks": 3,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5:responses",
            "provider_model_name": "gpt-5:responses",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="How many primes below 400 contain 79 as a substring? Answer ONLY with the number, not sharing which primes they are."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="3")],
                    provider_id="openai",
                    model_id="openai/gpt-5:responses",
                    provider_model_name="gpt-5:responses",
                    raw_message=[
                        {
                            "id": "rs_0b3fa1fc0060d42b00696af059c1748197b3a1e949827e434c",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0b3fa1fc0060d42b00696af06545c48197afeccc2f4dae865a",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "3",
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
                "input_tokens": 32,
                "output_tokens": 839,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 832,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 871,
            },
            "n_chunks": 3,
        }
    }
)
