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
                "provider_id": "openai",
                "model_id": "openai/gpt-4o:responses",
                "provider_model_name": "gpt-4o:responses",
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
                    "input_tokens": 16,
                    "output_tokens": 11,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "reasoning_tokens": 0,
                    "raw": "ResponseUsage(input_tokens=16, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=11, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=27)",
                    "total_tokens": 27,
                },
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[Text(text="4200 + 42 equals 4242.")],
                        provider_id="openai",
                        model_id="openai/gpt-4o:responses",
                        provider_model_name="gpt-4o:responses",
                        raw_message=[
                            {
                                "id": "msg_0d902d0e83de5d560068f96689f0b8819698f9c3a097db17f1",
                                "content": [
                                    {
                                        "annotations": [],
                                        "text": "4200 + 42 equals 4242.",
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
            },
        ),
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: openai)",
            "Skipping unsupported parameter: seed=42 (provider: openai)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai)",
            "Skipping unsupported parameter: thinking=False (provider: openai with model_id: openai/gpt-4o:responses)",
        ],
    }
)
