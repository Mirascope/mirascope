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
                "input_tokens": 69,
                "output_tokens": 218,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 192,
                "raw": "ResponseUsage(input_tokens=69, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=218, output_tokens_details=OutputTokensDetails(reasoning_tokens=192), total_tokens=287)",
                "total_tokens": 287,
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
                            "id": "rs_04064f738d7b52280069492dd814788197aef8f10017eaf066",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_04064f738d7b52280069492ddb33248197ba8bb05ba47c8723",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
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
                "mode": "json",
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
