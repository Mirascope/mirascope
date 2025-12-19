from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 17,
                "output_tokens": 15,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=15, prompt_tokens=17, total_tokens=32, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 32,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 = 4242")],
                    provider_id="openai",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5:completions",
                    raw_message={"content": "4200 + 42 = 4242", "role": "assistant"},
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
