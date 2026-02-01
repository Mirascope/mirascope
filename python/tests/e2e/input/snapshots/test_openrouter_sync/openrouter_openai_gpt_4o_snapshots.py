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
            "model_id": "openrouter/openai/gpt-4o",
            "provider_model_name": "openai/gpt-4o",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 12,
                "output_tokens": 2,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=2, prompt_tokens=12, total_tokens=14, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0), cost=5e-05, is_byok=False, cost_details={'upstream_inference_cost': 5e-05, 'upstream_inference_prompt_cost': 3e-05, 'upstream_inference_completions_cost': 2e-05})",
                "total_tokens": 14,
            },
            "messages": [
                UserMessage(content=[Text(text="Say hello in one word")]),
                AssistantMessage(
                    content=[Text(text="Hello!")],
                    provider_id="openrouter",
                    model_id="openrouter/openai/gpt-4o",
                    provider_model_name="openai/gpt-4o",
                    raw_message={"content": "Hello!", "role": "assistant"},
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
