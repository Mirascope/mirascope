from inline_snapshot import snapshot

from mirascope.llm import AssistantMessage, Text, UserMessage

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "together",
            "model_id": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "provider_model_name": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 44,
                "output_tokens": 23,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=23, prompt_tokens=44, total_tokens=67, completion_tokens_details=None, prompt_tokens_details=None, cached_tokens=0)",
                "total_tokens": 67,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the answer, add 4200 and 42.

4200 + 42 = 4242\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    provider_model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    raw_message={
                        "content": """\
To find the answer, add 4200 and 42.

4200 + 42 = 4242\
""",
                        "role": "assistant",
                        "tool_calls": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
