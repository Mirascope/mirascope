from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text=' start', token=1191, prompt_tokens=15, generation_tokens=50, finish_reason='length')",
                "total_tokens": 65,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking me to list all U.S. states. Let me start by recalling the main states. I know that the United States has 50 states, so I should list them all. First, I'll start\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name=None,
                    raw_message=None,
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
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text=' start', token=1191, prompt_tokens=15, generation_tokens=50, finish_reason='length')",
                "total_tokens": 65,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking me to list all U.S. states. Let me start by recalling the main states. I know that the United States has 50 states, so I should list them all. First, I'll start\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name=None,
                    raw_message=None,
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
            "provider_id": "mlx",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking me to list all U.S. states. Let me start by recalling the main states. I know that the United States has 50 states, so I should list them all. First, I'll start\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 65,
            },
            "n_chunks": 51,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking me to list all U.S. states. Let me start by recalling the main states. I know that the United States has 50 states, so I should list them all. First, I'll start\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 65,
            },
            "n_chunks": 51,
        }
    }
)
