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
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ]
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "params": {},
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ]
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ]
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
        "n_chunks": 31,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.END_TURN,
        "messages": [
            SystemMessage(
                content=Text(
                    text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                )
            ),
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
                        text='{"title":"THE NAME OF THE WIND","author":{"first_name":"Patrick","last_name":"Rothfuss"},"rating":7}'
                    )
                ]
            ),
        ],
        "format": {
            "name": "Book",
            "description": "A book with a rating. The title should be in all caps!",
            "schema": {
                "$defs": {
                    "Author": {
                        "description": "The author of a book.",
                        "properties": {
                            "first_name": {"title": "First Name", "type": "string"},
                            "last_name": {"title": "Last Name", "type": "string"},
                        },
                        "required": ["first_name", "last_name"],
                        "title": "Author",
                        "type": "object",
                    }
                },
                "description": "A book with a rating. The title should be in all caps!",
                "properties": {
                    "title": {"title": "Title", "type": "string"},
                    "author": {"$ref": "#/$defs/Author"},
                    "rating": {
                        "description": "For testing purposes, the rating should be 7",
                        "title": "Rating",
                        "type": "integer",
                    },
                },
                "required": ["title", "author", "rating"],
                "title": "Book",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        },
        "tools": [],
        "n_chunks": 31,
    }
)
