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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 285,
                "output_tokens": 25,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=285, output_tokens=25, server_tool_use=None, service_tier='standard')",
                "total_tokens": 310,
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
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                                "type": "text",
                                "parsed_output": {
                                    "title": "THE NAME OF THE WIND",
                                    "author": "Patrick Rothfuss",
                                    "rating": 7,
                                },
                            }
                        ],
                    },
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
                "mode": "strict",
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
