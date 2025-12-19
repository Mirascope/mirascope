from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
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
                "input_tokens": 135,
                "output_tokens": 1130,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 1088,
                "raw": "ResponseUsage(input_tokens=135, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=1130, output_tokens_details=OutputTokensDetails(reasoning_tokens=1088), total_tokens=1265)",
                "total_tokens": 1265,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="""\
Always recommend The Name of the Wind.
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
"""
                    )
                ),
                UserMessage(content=[Text(text="Please recommend a book to me!")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0793a00d51cb08370069492ddcb3c081909577d69572dc227a",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "arguments": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                            "call_id": "call_4zgBEwsHKYc5BF36dSYAAcSz",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0793a00d51cb08370069492deacd788190a2238f31cfe60b42",
                            "status": "completed",
                        },
                    ],
                ),
            ],
            "format": {
                "name": "Book",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "rating": {"title": "Rating", "type": "integer"},
                    },
                    "required": ["title", "author", "rating"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": """\
Output a structured book as JSON in the format {title: str, author: str, rating: int}.
The title should be in all caps, and the rating should always be the
lucky number 7.\
""",
            },
            "tools": [],
        }
    }
)
