from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
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
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
        },
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
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
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
        },
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
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
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
        },
        "n_chunks": 6,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            UserMessage(
                content=[
                    Text(
                        text="Please recommend the most popular book by Patrick Rothfuss"
                    )
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
{
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss"
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
                },
                "required": ["title", "author"],
                "title": "Book",
                "type": "object",
            },
            "mode": "strict",
        },
        "n_chunks": 6,
    }
)
