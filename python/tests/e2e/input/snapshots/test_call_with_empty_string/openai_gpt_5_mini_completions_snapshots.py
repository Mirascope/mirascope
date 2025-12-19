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
                "output_tokens": 200,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 64,
                "raw": "CompletionUsage(completion_tokens=200, prompt_tokens=6, total_tokens=206, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=64, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 206,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Hi — I didn’t get any details. What can I help you with today?

Here are some examples if you want ideas:
- Answer a question or explain a topic
- Write, edit or summarize text (email, resume, essay, ad, etc.)
- Generate or review code (and debug)
- Translate or proofread
- Create plans, outlines, or checklists
- Brainstorm ideas (names, features, strategies)
- Tutor or solve homework problems
- Troubleshoot tech, math, or data issues

Tell me what you need and any specifics (length, tone, language, code language, deadline).\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": """\
Hi — I didn’t get any details. What can I help you with today?

Here are some examples if you want ideas:
- Answer a question or explain a topic
- Write, edit or summarize text (email, resume, essay, ad, etc.)
- Generate or review code (and debug)
- Translate or proofread
- Create plans, outlines, or checklists
- Brainstorm ideas (names, features, strategies)
- Tutor or solve homework problems
- Troubleshoot tech, math, or data issues

Tell me what you need and any specifics (length, tone, language, code language, deadline).\
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
