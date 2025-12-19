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
                "output_tokens": 326,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 128,
                "raw": "CompletionUsage(completion_tokens=326, prompt_tokens=6, total_tokens=332, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=128, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 332,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Hi — I didn’t get any details. How can I help you today?

If you’re not sure, here are examples of things I can do:
- Write or edit emails, essays, reports, or creative text
- Summarize or analyze articles, papers, or long text (paste it in)
- Help with coding: write, debug, explain, or review code (specify language)
- Answer questions or explain concepts in science, math, history, etc.
- Generate plans: study schedules, project timelines, meal plans
- Translate or proofread text
- Create prompts, outlines, or checklists

Tell me:
1) What you want me to do (short instruction)
2) Any important details or constraints (length, tone, audience, language)
3) If relevant, paste the text or code

If you prefer, just say “surprise me” and I’ll propose a few options.\
"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": """\
Hi — I didn’t get any details. How can I help you today?

If you’re not sure, here are examples of things I can do:
- Write or edit emails, essays, reports, or creative text
- Summarize or analyze articles, papers, or long text (paste it in)
- Help with coding: write, debug, explain, or review code (specify language)
- Answer questions or explain concepts in science, math, history, etc.
- Generate plans: study schedules, project timelines, meal plans
- Translate or proofread text
- Create prompts, outlines, or checklists

Tell me:
1) What you want me to do (short instruction)
2) Any important details or constraints (length, tone, audience, language)
3) If relevant, paste the text or code

If you prefer, just say “surprise me” and I’ll propose a few options.\
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
