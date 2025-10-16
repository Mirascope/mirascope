from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        text='{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                        "call_id": "call_hM3bMZUpMupliYkGcFvsvs3c",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_024e33dc9597433f0068dc21e888f081949244a3df73f33c71",
                        "status": "completed",
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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        text='{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                        "call_id": "call_0vnNtPoG4KGTNHDUn8cmD3wo",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_07becd0b396cfeb30068dc21f0eb7481979105ae7bf525b6ca",
                        "status": "completed",
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
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        text='{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                        "call_id": "call_PZDxZlC02RvN8HY9ypCqBQhs",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_0401780ce2eb70720068dc21f82ac081909284ddc41c213c92",
                        "status": "completed",
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
        "n_chunks": 22,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
        "model_id": "gpt-4o",
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
                        text='{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}'
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"title":"THE NAME OF THE WIND","author":"Patrick Rothfuss","rating":7}',
                        "call_id": "call_TdSkqpCk7o7xHbOJKbzLFX1e",
                        "name": "__mirascope_formatted_output_tool__",
                        "type": "function_call",
                        "id": "fc_083f1b215a8e78710068dc21ff3cf08193b07ee2faaf4108d4",
                        "status": "completed",
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
        "n_chunks": 22,
    }
)
