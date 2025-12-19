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
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 7,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=7, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=26, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=33)",
                "total_tokens": 33,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="It looks like you're trying to share an image or details about a scene or object. How can I assist you with it?"
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_02aecbd82c76cb54006931df309ef08197a1a028224b73014e",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": "It looks like you're trying to share an image or details about a scene or object. How can I assist you with it?",
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
