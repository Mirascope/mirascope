from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider_id": "anthropic",
                "model_id": "anthropic-beta/claude-sonnet-4-0",
                "provider_model_name": "claude-sonnet-4-0",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "usage": {
                    "input_tokens": 17,
                    "output_tokens": 12,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "reasoning_tokens": 0,
                    "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=17, output_tokens=12, server_tool_use=None, service_tier='standard')",
                    "total_tokens": 29,
                },
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 = ")],
                        provider_id="anthropic",
                        model_id="anthropic-beta/claude-sonnet-4-0",
                        provider_model_name="claude-sonnet-4-0",
                        raw_message={
                            "role": "assistant",
                            "content": [{"text": "4200 + 42 = ", "type": "text"}],
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logs": ["Skipping unsupported parameter: seed=42 (provider: anthropic)"],
    }
)
