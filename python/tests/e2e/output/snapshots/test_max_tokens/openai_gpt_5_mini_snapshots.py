from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=13, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=0, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=13)",
                "total_tokens": 13,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_018923f8d395125e0069492e1b2bcc819798c6be1727db8a10",
                            "summary": [],
                            "type": "reasoning",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=13, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=0, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=13)",
                "total_tokens": 13,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0ef367e9007678350069492e1d6eb88197ae870da8082d5d79",
                            "summary": [],
                            "type": "reasoning",
                        }
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": None,
            "n_chunks": 0,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": None,
            "n_chunks": 0,
        }
    }
)
