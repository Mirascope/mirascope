from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider_id": "together",
                "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
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
                        content=[
                            Text(
                                text="""\
## Step 1: Understand the problem
The problem asks us to add 4200 and 42.

## Step 2: Perform the addition
To find the sum, we simply add 4200 and 42 together. 4200 + 42 = \
"""
                            )
                        ],
                        provider_id="together",
                        model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                        provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                        raw_message={
                            "role": "assistant",
                            "content": """\
## Step 1: Understand the problem
The problem asks us to add 4200 and 42.

## Step 2: Perform the addition
To find the sum, we simply add 4200 and 42 together. 4200 + 42 = \
""",
                            "tool_calls": [],
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": ["Skipping unsupported parameter: thinking=False (provider: together)"],
    }
)
