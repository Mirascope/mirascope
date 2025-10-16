from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
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
                        text='{"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss", "rating": 7}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_01PDre8QuNVcqNR8rx4uYj7o",
                        "input": {
                            "title": "THE NAME OF THE WIND",
                            "author": "Patrick Rothfuss",
                            "rating": 7,
                        },
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "tool_use",
                    }
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
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
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
                        text='{"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss", "rating": 7}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "id": "toolu_018Z4E5MyKa8inkZmkZMkKZU",
                        "input": {
                            "title": "THE NAME OF THE WIND",
                            "author": "Patrick Rothfuss",
                            "rating": 7,
                        },
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "tool_use",
                    }
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
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
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
                        text='{"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss", "rating": 7}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_012K9PfB1AvfmhTBBrA7LVVN",
                        "name": "__mirascope_formatted_output_tool__",
                        "input": {
                            "title": "THE NAME OF THE WIND",
                            "author": "Patrick Rothfuss",
                            "rating": 7,
                        },
                    }
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
        "n_chunks": 15,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "finish_reason": None,
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
                        text='{"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss", "rating": 7}'
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_content=[
                    {
                        "type": "tool_use",
                        "id": "toolu_01TcMCS5iG91SSM8eZgxpPCV",
                        "name": "__mirascope_formatted_output_tool__",
                        "input": {
                            "title": "THE NAME OF THE WIND",
                            "author": "Patrick Rothfuss",
                            "rating": 7,
                        },
                    }
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
        "n_chunks": 14,
    }
)
