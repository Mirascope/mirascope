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
            "model_id": "openai/gpt-5-mini",
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
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0682958ac604b79f00695cb5af7f0c8197be05619c7bfb342a",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0682958ac604b79f00695cb5afeab88197876619489f88d7ce",
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
