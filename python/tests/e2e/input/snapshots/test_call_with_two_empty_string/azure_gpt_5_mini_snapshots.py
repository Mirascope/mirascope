from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 6,
                "output_tokens": 177,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 64,
                "raw": "CompletionUsage(completion_tokens=177, prompt_tokens=6, total_tokens=183, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=64, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 183,
            },
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Hi — how can I help you today? Here are a few things I can do if you’re not sure:

- Answer a question or explain a topic
- Help write or edit text (emails, essays, resumes, stories)
- Debug or write code (show language and goal)
- Solve math or science problems
- Summarize or translate documents
- Plan projects, schedules, or trips
- Provide creative ideas (names, prompts, outlines)

Tell me what you need and any important details.\
"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": """\
Hi — how can I help you today? Here are a few things I can do if you’re not sure:

- Answer a question or explain a topic
- Help write or edit text (emails, essays, resumes, stories)
- Debug or write code (show language and goal)
- Solve math or science problems
- Summarize or translate documents
- Plan projects, schedules, or trips
- Provide creative ideas (names, prompts, outlines)

Tell me what you need and any important details.\
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
