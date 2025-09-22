from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
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
                        text="""\
{
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
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
            "mode": "strict-or-json",
        },
    }
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
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
                        text="""\
{
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
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
            "mode": "strict-or-json",
        },
    }
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
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
                        text="""\
{
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
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
            "mode": "strict-or-json",
        },
        "n_chunks": 5,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": FinishReason.END_TURN,
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
                        text="""\
{
  "title": "THE NAME OF THE WIND",
  "author": "Patrick Rothfuss",
  "rating": 7
}\
"""
                    )
                ]
            ),
        ],
        "format_type": {
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
            "mode": "strict-or-json",
        },
        "n_chunks": 5,
    }
)
