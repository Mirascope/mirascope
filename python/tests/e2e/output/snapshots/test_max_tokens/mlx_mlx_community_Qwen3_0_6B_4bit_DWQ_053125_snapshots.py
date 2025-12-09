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
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking to list all U.S. states. Let me start by recalling the main states. I know the capital cities are Washington, D.C., and also some other states like Florida, Texas, California, New York\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
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
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking to list all U.S. states. Let me start by recalling the main states. I know the capital cities are Washington, D.C., and also some other states like Florida, Texas, California, New York\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
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
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking to list all U.S. states. Let me start by recalling the main states. I know the capital cities are Washington, D.C., and also some other states like Florida, Texas, California, New York\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 51,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<think>
Okay, the user is asking to list all U.S. states. Let me start by recalling the main states. I know the capital cities are Washington, D.C., and also some other states like Florida, Texas, California, New York\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 51,
        }
    }
)
