from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai:responses",
            "model_id": "openai/gpt-4o-mini:responses",
            "provider_model_name": "gpt-4o-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 9,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=9, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=10, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=19)",
                "total_tokens": 19,
            },
            "messages": [
                UserMessage(content=[Text(text="Say hello")]),
                AssistantMessage(
                    content=[Text(text="Hello! How can I assist you today?")],
                    provider_id="openai:responses",
                    model_id="openai/gpt-4o-mini:responses",
                    provider_model_name="gpt-4o-mini:responses",
                    raw_message=[
                        {
                            "id": "msg_0f4b2492a29645c100693c9fde16ac8193873fc70a3a865f3b",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "Hello! How can I assist you today?",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
