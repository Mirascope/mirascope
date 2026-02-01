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
            "model_id": "openrouter/openai/o1",
            "provider_model_name": "openai/o1",
            "params": {"temperature": 0.5},
            "finish_reason": None,
            "usage": {
                "input_tokens": 13,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=9, prompt_tokens=13, total_tokens=22, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=None, reasoning_tokens=0, rejected_prediction_tokens=None, image_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0), cost=0.000735, is_byok=False, cost_details={'upstream_inference_cost': 0.000735, 'upstream_inference_prompt_cost': 0.000195, 'upstream_inference_completions_cost': 0.00054})",
                "total_tokens": 22,
            },
            "messages": [
                UserMessage(content=[Text(text="What is 2+2?")]),
                AssistantMessage(
                    content=[Text(text="2 + 2 = 4.")],
                    provider_id="openrouter",
                    model_id="openrouter/openai/o1",
                    provider_model_name="openai/o1",
                    raw_message={"content": "2 + 2 = 4.", "role": "assistant"},
                ),
            ],
            "format": None,
            "tools": [],
        },
        "logs": ["Skipping unsupported parameter: temperature=0.5 (provider: openai)"],
    }
)
