from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 74,
                "output_tokens": 59,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=59, prompt_tokens=74, total_tokens=133, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 133,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="<reasoning>The user asks: \"What is 4200 + 42?\" They likely expect the sum 4242. That's straightforward. No special context. Provide answer. It's 4242.</reasoning>4200 + 42 equals **4242**."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": "<reasoning>The user asks: \"What is 4200 + 42?\" They likely expect the sum 4242. That's straightforward. No special context. Provide answer. It's 4242.</reasoning>4200 + 42 equals **4242**.",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
