from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 56,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 68,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the sum of 4200 and 42, you simply add the two numbers together:

\\[ 4200 + 42 = 4242 \\]

So, the result is \\( 4242 \\).\
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
        "context_call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 63,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 75,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the sum of 4200 and 42, you simply add the two numbers together:

\\[ 4200 + 42 = 4242 \\]

So, \\( 4200 + 42 = 4242 \\).\
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
        "stream": {
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

So, \\( 4200 + 42 = 4242 \\).\
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
                "output_tokens": 63,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 75,
            },
            "n_chunks": 17,
        },
        "context_stream": {
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

2. Add the digits in the ones place:
   \\[
   0 + 2 = 2
   \\]

3. Add the digits in the tens place:
   \\[
   0 + 4 = 4
   \\]

4. Add the digits in the hundreds place:
   \\[
   2 + 0 = 2
   \\]

5. Add the digits in the thousands place:
   \\[
   4 + 0 = 4
   \\]

Putting it all together, we get:
\\[
\\begin{array}{c@{}c@{}c@{}c@{}c}
  & 4 & 2 & 0 & 0 \\\\
  + & & 4 & 2 & \\\\
  \\hline
  & 4 & 2 & 4 & 2 \\\\
\\end{array}
\\]

So, the final answer is \\(\\boxed{4242}\\).\
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
                "output_tokens": 285,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 297,
            },
            "n_chunks": 65,
        },
    }
)
