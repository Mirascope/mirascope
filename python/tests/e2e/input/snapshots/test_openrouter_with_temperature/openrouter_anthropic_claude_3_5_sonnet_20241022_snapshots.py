from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openrouter",
            "model_id": "openrouter/anthropic/claude-3-5-sonnet-20241022",
            "provider_model_name": "anthropic/claude-3-5-sonnet-20241022",
            "params": {"temperature": 0.5},
            "finish_reason": None,
            "usage": {
                "input_tokens": 9,
                "output_tokens": 10,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=10, prompt_tokens=9, total_tokens=19, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=0, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0, cache_write_tokens=0), cost=0.000354, is_byok=False, cost_details={'upstream_inference_cost': 0.000354, 'upstream_inference_prompt_cost': 5.4e-05, 'upstream_inference_completions_cost': 0.0003})",
                "total_tokens": 19,
            },
            "messages": [
                UserMessage(content=[Text(text="Say hello")]),
                AssistantMessage(
                    content=[Text(text="Hello! How are you today?")],
                    provider_id="openrouter",
                    model_id="openrouter/anthropic/claude-3-5-sonnet-20241022",
                    provider_model_name="anthropic/claude-3-5-sonnet-20241022",
                    raw_message={
                        "content": "Hello! How are you today?",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
