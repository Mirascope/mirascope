from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
## Step 1: Understand the problem
The problem asks us to add 4200 and 42 together.

## Step 2: Perform the addition
To find the sum, we add 4200 and 42. This can be done by simple arithmetic addition.

## Step 3: Calculate the sum
4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
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
The problem asks us to add 4200 and 42 together.

## Step 2: Perform the addition
To find the sum, we add 4200 and 42. This can be done by simple arithmetic addition.

## Step 3: Calculate the sum
4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
""",
                        "tool_calls": [],
                    },
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
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
## Step 1: Understand the problem
The problem asks for the sum of 4200 and 42.

## Step 2: Add the numbers
To find the sum, we simply add 4200 and 42 together. 4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
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
The problem asks for the sum of 4200 and 42.

## Step 2: Add the numbers
To find the sum, we simply add 4200 and 42 together. 4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
""",
                        "tool_calls": [],
                    },
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
            "provider": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
## Step 1: Understand the problem
The problem requires adding two numbers, 4200 and 42.

## Step 2: Perform the addition
To find the sum, we simply add 4200 and 42 together.

## Step 3: Calculate the sum
4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 80,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
## Step 1: Understand the problem
The problem requires adding two numbers, 4200 and 42.

## Step 2: Perform the addition
To find the sum, we simply add 4200 and 42 together.

## Step 3: Calculate the sum
4200 + 42 = 4242.

The final answer is: $\\boxed{4242}$\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 80,
        }
    }
)
