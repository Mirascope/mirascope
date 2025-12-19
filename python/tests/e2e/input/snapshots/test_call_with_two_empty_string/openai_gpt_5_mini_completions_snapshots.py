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
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 6,
                "output_tokens": 386,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 192,
                "raw": "CompletionUsage(completion_tokens=386, prompt_tokens=6, total_tokens=392, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=192, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 392,
            },
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I didn't get any content — how can I help you today?

Here are some examples of things I can do (copy any one to start):
- "Summarize this text: [paste text]."
- "Write a professional email to my manager about [topic]."
- "Help debug this code: [paste code and error]."
- "Explain [concept] as if I'm [grade level / beginner / expert]."
- "Plan a 3-day itinerary in [city] with [interests]."
- "Translate this into [language]: [text]."
- "Create a study schedule to learn [skill] in [timeframe]."
- "Generate a recipe using [ingredients]."
- "Compare [A] vs [B] and recommend one."

If you prefer, just tell me what you need and any relevant details (length, tone, constraints), and I'll get started.\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": """\
I didn't get any content — how can I help you today?

Here are some examples of things I can do (copy any one to start):
- "Summarize this text: [paste text]."
- "Write a professional email to my manager about [topic]."
- "Help debug this code: [paste code and error]."
- "Explain [concept] as if I'm [grade level / beginner / expert]."
- "Plan a 3-day itinerary in [city] with [interests]."
- "Translate this into [language]: [text]."
- "Create a study schedule to learn [skill] in [timeframe]."
- "Generate a recipe using [ingredients]."
- "Compare [A] vs [B] and recommend one."

If you prefer, just tell me what you need and any relevant details (length, tone, constraints), and I'll get started.\
""",
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
