from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "ollama",
            "model_id": "ollama/gemma3:4b",
            "provider_model_name": "gemma3:4b",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 21,
                "output_tokens": 16,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=16, prompt_tokens=21, total_tokens=37, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 37,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4200 + 42 = 4242\n")],
                    provider_id="ollama",
                    model_id="ollama/gemma3:4b",
                    provider_model_name="gemma3:4b",
                    raw_message={"content": "4200 + 42 = 4242\n", "role": "assistant"},
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
