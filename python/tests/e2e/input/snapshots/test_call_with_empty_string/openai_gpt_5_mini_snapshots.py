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
                "output_tokens": 189,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 64,
                "raw": "ResponseUsage(input_tokens=6, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=189, output_tokens_details=OutputTokensDetails(reasoning_tokens=64), total_tokens=195)",
                "total_tokens": 195,
            },
            "messages": [
                UserMessage(content=[Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Hi — how can I help you today?

Here are some things I can do (pick one or describe your need):
- Answer a question or explain a concept
- Write or edit email, resume, cover letter, or other text
- Summarize an article or long document
- Help with code, debugging, or writing scripts
- Generate ideas: brainstorming, names, plans
- Translate text or improve phrasing
- Create a step-by-step plan or checklist
- Analyze an image (you can upload one)

Or just tell me what you need in your own words.\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_015ebc58872dcc140069492dbc32488193b4bb6167e9c9b504",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_015ebc58872dcc140069492dbd57a88193a50e8fe450f26b24",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Hi — how can I help you today?

Here are some things I can do (pick one or describe your need):
- Answer a question or explain a concept
- Write or edit email, resume, cover letter, or other text
- Summarize an article or long document
- Help with code, debugging, or writing scripts
- Generate ideas: brainstorming, names, plans
- Translate text or improve phrasing
- Create a step-by-step plan or checklist
- Analyze an image (you can upload one)

Or just tell me what you need in your own words.\
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
