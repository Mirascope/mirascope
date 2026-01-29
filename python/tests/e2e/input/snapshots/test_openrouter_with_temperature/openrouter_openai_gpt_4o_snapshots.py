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
            "params": {"temperature": 0.5},
            "finish_reason": None,
            "usage": {
                "input_tokens": 9,
                "output_tokens": 9,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=9, prompt_tokens=9, total_tokens=18, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=None), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0), cost=0.0001125, is_byok=False, cost_details={'upstream_inference_cost': 0.0001125, 'upstream_inference_prompt_cost': 2.25e-05, 'upstream_inference_completions_cost': 9e-05})",
                "total_tokens": 18,
            },
            "messages": [
                UserMessage(content=[Text(text="Say hello")]),
                AssistantMessage(
                    content=[Text(text="Hello! How can I assist you today?")],
                    provider_id="openrouter",
                    model_id="openrouter/openai/gpt-4o",
                    provider_model_name="openai/gpt-4o",
                    raw_message={
                        "content": "Hello! How can I assist you today?",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
