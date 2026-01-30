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
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 50,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=50, prompt_tokens=13, total_tokens=63, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=50, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 63,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={"content": "", "role": "assistant", "annotations": []},
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
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 50,
                "provider_tool_usage": None,
                "raw": "CompletionUsage(completion_tokens=50, prompt_tokens=13, total_tokens=63, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=50, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 63,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={"content": "", "role": "assistant", "annotations": []},
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
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 13,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 50,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 63,
            },
            "n_chunks": 0,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 13,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 50,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 63,
            },
            "n_chunks": 0,
        }
    }
)
