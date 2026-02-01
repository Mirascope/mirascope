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
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[Text(text="4242")],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:responses",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_02cbfd68e4ae57b500695cb5baa70881958fc5f6be59e1512b",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_02cbfd68e4ae57b500695cb5baff7c8195976581ed7c4d5108",
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
            "usage": {
                "input_tokens": 15,
                "output_tokens": 8,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 23,
            },
            "n_chunks": 4,
        }
    }
)
