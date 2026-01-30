from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "async_call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 258,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 270,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To solve the problem \\(4200 + 42\\), we can follow these steps:

1. Align the numbers by their place values:
   \\[
   \\begin{array}{c@{}c@{}c@{}c@{}c}
     & 4 & 2 & 0 & 0 \\\\
   + &    &   & 4 & 2 \\\\
   \\end{array}
   \\]

2. Add the digits starting from the rightmost column (the ones place):
   - In the ones place: \\(0 + 2 = 2\\)
   - In the tens place: \\(0 + 4 = 4\\)
   - In the hundreds place: \\(2 + 0 = 2\\)
   - In the thousands place: \\(4 + 0 = 4\\)

3. Combine these results to get the final answer:
   \\[
   \\begin{array}{c@{}c@{}c@{}c@{}c}
     & 4 & 2 & 4 & 2 \\\\
   \\end{array}
   \\]

So, the sum of \\(4200 + 42\\) is \\(\\boxed{4242}\\).\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        },
        "async_context_call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 61,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 73,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the sum of 4200 and 42, you simply add the two numbers together:

\\[ 4200 + 42 = 4242 \\]

So, 4200 plus 42 equals 4242.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        },
        "async_stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To solve the problem \\(4200 + 42\\), we can follow these steps:

1. Align the numbers by their place values:
   \\[
   \\begin{array}{c@{}c@{}c@{}c@{}c}
     & 4 & 2 & 0 & 0 \\\\
     + & & 4 & 2 & \\\\
   \\end{array}
   \\]

2. Add the numbers starting from the rightmost digit (the units place):
   - Units place: \\(0 + 2 = 2\\)
   - Tens place: \\(0 + 4 = 4\\)
   - Hundreds place: \\(2 + 0 = 2\\)
   - Thousands place: \\(4 + 0 = 4\\)

3. Combine these results to get the final sum:
   \\[
   \\begin{array}{c@{}c@{}c@{}c@{}c}
     & 4 & 2 & 4 & 2 \\\\
   \\end{array}
   \\]

So, the sum of \\(4200 + 42\\) is \\(\\boxed{4242}\\).\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 12,
                "output_tokens": 249,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 261,
            },
            "n_chunks": 53,
        },
        "async_context_stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the sum of 4200 and 42, you simply add the two numbers together:

\\[ 4200 + 42 = 4242 \\]

So, 4200 plus 42 equals 4242.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 12,
                "output_tokens": 61,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 73,
            },
            "n_chunks": 14,
        },
    }
)
