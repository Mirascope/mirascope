from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Image,
    Text,
    URLImageSource,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 34,
                "output_tokens": 161,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 128,
                "raw": "CompletionUsage(completion_tokens=161, prompt_tokens=34, total_tokens=195, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=128, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 195,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(text="Describe the following image in one sentence"),
                        Image(
                            source=URLImageSource(
                                type="url_image_source",
                                url="https://en.wikipedia.org/static/images/icons/wikipedia.png",
                            )
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The image shows Wikipedia’s iconic globe-shaped jigsaw puzzle logo made of gray tiles inscribed with various letters and symbols."
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": "The image shows Wikipedia’s iconic globe-shaped jigsaw puzzle logo made of gray tiles inscribed with various letters and symbols.",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
