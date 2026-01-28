from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 78,
                "output_tokens": 41,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=41, prompt_tokens=78, total_tokens=119, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 119,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>We need to answer sum. 4200+42=4242. Probably just answer.</reasoning>4200\u202f+\u202f42\u202f=\u202f4242."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>We need to answer sum. 4200+42=4242. Probably just answer.</reasoning>4200\u202f+\u202f42\u202f=\u202f4242.",
                        "role": "assistant",
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
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 78,
                "output_tokens": 67,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=67, prompt_tokens=78, total_tokens=145, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 145,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user asks: \"What is 4200 + 42?\" It's a simple math: 4200 + 42 = 4242. Let's ensure no ambiguity. So answer is 4242. Let's respond.</reasoning>4200\u202f+\u202f42\xa0=\xa04242."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>The user asks: \"What is 4200 + 42?\" It's a simple math: 4200 + 42 = 4242. Let's ensure no ambiguity. So answer is 4242. Let's respond.</reasoning>4200\u202f+\u202f42\xa0=\xa04242.",
                        "role": "assistant",
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
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user asks \"What is 4200 + 42?\" We just need to give the sum: 4242. It's trivial. In addition, check if any mention of policies like privacy or no.</reasoning><reasoning> It's straightforward. Provide the answer and maybe a bit of explanation.</reasoning>4200\u202f+\u202f42\u202f=\u202f**4242**."
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
                "input_tokens": 78,
                "output_tokens": 79,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 157,
            },
            "n_chunks": 5,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>User asks a simple math: 4200 + 42 = 4242. Need to respond.</reasoning>4200\u202f+\u202f42\u202f=\u202f**4242**."
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
                "input_tokens": 78,
                "output_tokens": 45,
                "cache_read_tokens": 48,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 123,
            },
            "n_chunks": 4,
        }
    }
)
