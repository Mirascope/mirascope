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
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 74,
                "output_tokens": 80,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=80, prompt_tokens=74, total_tokens=154, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 154,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<reasoning>The user asks: "What is 4200 + 42?" That's a simple addition: 4200 + 42 = 4242. So answer 4242. That's it.</reasoning>4220 + 22 is 4220 + 22 = 4242.

Therefore, 4200 + 42 = **4242**.\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": """\
<reasoning>The user asks: "What is 4200 + 42?" That's a simple addition: 4200 + 42 = 4242. So answer 4242. That's it.</reasoning>4220 + 22 is 4220 + 22 = 4242.

Therefore, 4200 + 42 = **4242**.\
""",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        },
        "context_call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 74,
                "output_tokens": 56,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=56, prompt_tokens=74, total_tokens=130, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 130,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user is asking a simple arithmetic addition problem: 4200 + 42. The answer is 4242. I should respond succinctly: 4242.</reasoning>\\(4200 + 42 = 4242\\)"
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>The user is asking a simple arithmetic addition problem: 4200 + 42. The answer is 4242. I should respond succinctly: 4242.</reasoning>\\(4200 + 42 = 4242\\)",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        },
        "stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>User asks simple math: 4200 + 42? That's 4242. Provide answer. I might mention it's 4242.</reasoning>4200\u202f+\u202f42\u202f=\u202f**4242**."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 74,
                "output_tokens": 52,
                "cache_read_tokens": 48,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 126,
            },
            "n_chunks": 5,
        },
        "context_stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>The user asks: "What is 4200 + 42?" Simple addition: 4200 + 42 = 4242. So answer is 4242.</reasoning>The sum is\u202f**4242**.'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 74,
                "output_tokens": 54,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 128,
            },
            "n_chunks": 4,
        },
    }
)
