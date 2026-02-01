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
            "model_id": "openai/gpt-5-mini:responses",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 8,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=15, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=8, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=23)",
                "total_tokens": 23,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:responses",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0024f5b14c683a8c00695cb5b3c13481979337a73e4da67821",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0024f5b14c683a8c00695cb5b4356c8197a76a5b6db4380e03",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "4242",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
