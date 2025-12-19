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
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 6,
                "output_tokens": 214,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 64,
                "raw": "ResponseUsage(input_tokens=6, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=214, output_tokens_details=OutputTokensDetails(reasoning_tokens=64), total_tokens=220)",
                "total_tokens": 220,
            },
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Hi — how can I help you today?

Tell me what you need (question, task, file or image to analyze, code to debug, text to edit, etc.), and any important details or constraints. If you’re not sure, here are some things I can do:
- Answer questions or explain concepts
- Summarize or rewrite text (tone/length/style)
- Draft emails, letters, proposals, or plans
- Write or review code, find bugs, suggest improvements
- Analyze images or screenshots you upload
- Create checklists, study plans, or timelines
- Compare products, pros/cons, or decision matrices

Give me the topic and any specifics, and I’ll get started.\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_09b7d2887a5a543e0069492dc055c081969ebe57eff0beafda",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_09b7d2887a5a543e0069492dc1c0d481969ff7ceb05874fc65",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Hi — how can I help you today?

Tell me what you need (question, task, file or image to analyze, code to debug, text to edit, etc.), and any important details or constraints. If you’re not sure, here are some things I can do:
- Answer questions or explain concepts
- Summarize or rewrite text (tone/length/style)
- Draft emails, letters, proposals, or plans
- Write or review code, find bugs, suggest improvements
- Analyze images or screenshots you upload
- Create checklists, study plans, or timelines
- Compare products, pros/cons, or decision matrices

Give me the topic and any specifics, and I’ll get started.\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
