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
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 74,
                "output_tokens": 61,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=61, prompt_tokens=74, total_tokens=135, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 135,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>The user asks: "What is 4200 + 42?" We simply compute: 4200 + 42 = 4242. Provide answer. Probably trivial. We\'ll respond.</reasoning>4200\u202f+\u202f42\u202f=\u202f**4242**'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": '<reasoning>The user asks: "What is 4200 + 42?" We simply compute: 4200 + 42 = 4242. Provide answer. Probably trivial. We\'ll respond.</reasoning>4200\u202f+\u202f42\u202f=\u202f**4242**',
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        },
        "async_context_call": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 74,
                "output_tokens": 53,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=53, prompt_tokens=74, total_tokens=127, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 127,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>The user asks: "What is 4200 + 42?" Simple arithmetic: 4200 + 42 = 4242. So answer that.</reasoning>4200 + 42 = **4242**.'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": '<reasoning>The user asks: "What is 4200 + 42?" Simple arithmetic: 4200 + 42 = 4242. So answer that.</reasoning>4200 + 42 = **4242**.',
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        },
        "async_stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>User: "What is 4200 + 42?" They want sum. 4200+42=4242. Provide answer.</reasoning>4200 + 42 = **4242**.'
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
                "output_tokens": 49,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 123,
            },
            "n_chunks": 4,
        },
        "async_context_stream": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user asks a simple arithmetic: 4200 + 42 = 4242. They might want an answer. Just answer: 4242</reasoning><reasoning>.</reasoning>\\(4200 + 42 = 4242\\)."
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
                "output_tokens": 53,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 127,
            },
            "n_chunks": 5,
        },
    }
)
